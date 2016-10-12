# -*- coding:utf-8 -*-
"""Service that parses the AT&T bill, splits wireless charges among users and
persists data in database.
"""

import datetime as dt
import getpass
import logging
import re
import sys
import click
import peewee as pw
from slugify import slugify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from attbillsplitter.errors import (
    UrlError, WebDriverException, ConfigError, LoginError, ParsingError,
    CalculationError, NoSuchElementException, TimeoutException, IntegrityError
)
from attbillsplitter.models import (
    User, ChargeCategory, ChargeType, BillingCycle, Charge, MonthlyBill, db
)
from attbillsplitter.utils import PAGE_LOADING_WAIT_S

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# suppress logging for selenium
logging.getLogger("selenium").setLevel(logging.WARNING)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def create_tables_if_not_exist():
    """Create tables in database if tables do not exist.

    Tables will be created for following models:
        - User
        - ChargeCategory
        - ChargeType
        - BillingCycle
        - Charge
        - MonthlyBill
    """
    db.connect()
    for model in (User, ChargeCategory, ChargeType, BillingCycle, Charge,
                  MonthlyBill):
        if not model.table_exists():
            model.create_table()


def get_start_end_date(bc_name):
    """Get start date and end date for a billing cycle name using regex.

    :param bc_name: name of billing cycle in format of
        'Mar 15 - Apr 14, 2016'
    :type bc_name: str
    :returns: a tuple of start date (datetime.date) and end date
    :rtype: tuple
    """
    m = re.search('(\w+ \d+) - (\w+ \d+), (\d{4})', bc_name)
    start_date_str = '{}, {}'.format(m.group(1), m.group(3))
    end_date_str = '{}, {}'.format(m.group(2), m.group(3))
    start_date = dt.datetime.strptime(start_date_str, '%b %d, %Y').date()
    end_date = dt.datetime.strptime(end_date_str, '%b %d, %Y').date()
    return (start_date, end_date)


def aggregate_wireless_monthly(bc):
    """Aggregate wireless charges among all lines.

    :param bc: billing_cycle object
    :type bc: BillingCycle
    :returns: None
    """
    if MonthlyBill.select().where(MonthlyBill.billing_cycle == bc).exists():
        logger.info('Charges already aggregated for billing cycle %s',
                    bc.name)
        return

    query = (
        User
        .select(User,
                pw.fn.SUM(Charge.amount).alias('total'))
        .join(Charge)
        .join(BillingCycle)
        .switch(Charge)
        .join(ChargeType)
        .join(ChargeCategory)
        .where(BillingCycle.id == bc.id,
               ChargeCategory.category == 'wireless')
        .group_by(User, BillingCycle)
        .naive()
    )
    results = query.execute()
    for user in results:
        MonthlyBill.create(user=user, billing_cycle=bc, total=user.total)


class AttBillSpliter(object):
    """Parse AT&T bill and split wireless charges among users.

    Currently tested on AT&T account with U-verse TV, Internet and Mobile
    Share Value Plan (for wireless).
    """
    login_url = 'https://www.att.com/olam/'
    login_page_title = (
        'myAT&T Login - Pay Bills Online & Manage Your AT&T Account'
    )
    login_landing_page_title = 'Account Overview'
    history_bills_url = (
        'https://www.att.com/olam/passthroughAction.'
        'myworld?actionType=ViewBillHistory'
    )

    def __init__(self):
        chromedriver = input('Enter the path to chromedriver executable. e.g.'
                             ' /Users/Brian/Downloads/chromedriver\n-> ')
        try:
            self.browser = webdriver.Chrome(chromedriver)
        except WebDriverException:
            msg = (
                'chromedriver executable not found in {}'.format(chromedriver)
            )
            raise ConfigError(msg)
        except:
            msg = ('Something happened when tring to launch the '
                   'Chrome browser. Make sure you have installed '
                   'Chrome and retry.')
            raise ConfigError(msg)

    def try_click_no_on_popup(self):
        """Try to click on 'No' button on a page.

        Sometimes promotion or survey window popup and block the window
        we want to parse. This method will try to find a button element
        <a> with 'No' in the text and click on it.
        """
        try:
            self.browser.find_element_by_xpath(
                "//a[contains(text(), 'No')]"
            ).click()
            logger.info('Popup page skipped.')
        except:
            pass

    def login(self):
        """Log in AT&T account.

        raises UrlError: unexpected page title
        raises LoginError: fail to login, could be wrong cridentials
        """
        self.browser.get(self.login_url)
        if self.browser.title != self.login_page_title:
            raise UrlError('Login page title does not match.')
        try:
            username_elem = self.browser.find_element_by_id('userID')
        except NoSuchElementException:
            raise LoginError('Unable to locate userid input element')
        # first clear the element in case browser autofill
        username_elem.clear()
        username = input('\U0001F464  Username: ')
        username_elem.send_keys(username)
        try:
            password_elem = self.browser.find_element_by_id('password')
        except NoSuchElementException:
            raise LoginError('Unable to locate password input element')
        password_elem.clear()
        password = getpass.getpass(prompt='\U0001F5DD  Password: ')
        password_elem.send_keys(password)
        password_elem.submit()
        self.try_click_no_on_popup()
        if self.browser.title != self.login_landing_page_title:
            raise LoginError(
                'Login landing page title does not match.'
            )
        logger.info('login succeeded.')

    def go_to_history_bills(self):
        """Navigate to billing history page.

        raises UrlError: unexpected page title
        """
        self.browser.get(self.history_bills_url)
        self.try_click_no_on_popup()
        if self.browser.title != 'Billing & Usage - AT&T':
            raise UrlError(
                'Unable to land at history bills page, url may have changed.'
            )
        logger.info('landed at history billings page.')

    def parse_user_info(self):
        """Parse the bill to find name and number for each line and create
        users. Account holder should be the first entry.

        :returns: list of user objects
        :rtype: list
        """
        users = []
        number_elems = self.browser.find_elements_by_xpath(
            "//div[contains(text(), 'Total for')]"
        )
        for number_elem in number_elems:
            m = re.search('Total for ([0-9]{3}-[0-9]{3}-[0-9]{4})',
                          number_elem.text)
            number = m.group(1)
            # get name for number
            name_elem = self.browser.find_element_by_xpath(
                "//div[@class='accRow bold MarTop10' and "
                "contains(text(), '{}')]".format(number)
            )
            m = re.search('(.+) {}'.format(number), name_elem.text)
            name = m.group(1)
            user, _ = User.get_or_create(name=name, number=number)
            users.append(user)
        return users

    def split_previous_bill(self):
        """All parsing and wireless bill splitting happen here.

        First Parse for U-verse TV, then U-verse Internet, and finally
        Wireless. Wireless account monthly charges (after discount if there
        is any) are split among all users.
        """
        logger.info('Start processing new bill...')
        # billing cycle
        new_charge_title = self.browser.find_element_by_xpath(
            "//h3[contains(text(), 'New charges for')]"
        ).text
        billing_cycle_name = new_charge_title[16:]
        if BillingCycle.select().where(
                BillingCycle.name == billing_cycle_name
        ):
            logger.warning('Billing Cycle %s already processed.',
                           billing_cycle_name)
            return

        start_date, end_date = get_start_end_date(billing_cycle_name)
        billing_cycle = BillingCycle.create(name=billing_cycle_name,
                                            start_date=start_date,
                                            end_date=end_date)
        # parse user name and number
        # sometimes a survey window pops up a few seconds after the billing
        # page has been loaded. This usually happens when we are parsing
        # user info. So if the parse_user_info fails the first time, we will
        # try to click No on popup window and give it a second try.
        for trial in (1, 2):
            try:
                users = self.parse_user_info()
            except:
                if trial == 1:
                    logger.warning('Parsing user info failed. Will retry.')
                elif trial == 2:
                    logger.exception('Parsing user info failed.')
                    raise ParsingError('Parsing user info failed.')
        logger.info('Parsing User info succeeded.')
        # set account holder
        account_holder = users[0]
        # ---------------------------------------------------------------------
        # U-verse tv
        # ---------------------------------------------------------------------
        # beginning div
        beginning_div_xpath = (
            "div[starts-with(@class, 'MarLeft12 MarRight90') and "
            "descendant::div[contains(text(), 'U-verse TV')]]"
        )
        # # end div
        end_div_xpath = (
            "div[@class='Padbot5 topDotBorder MarLeft12 MarRight90' and "
            "descendant::div[contains(text(), 'Total U-verse TV Charges')]]"
        )
        charge_elems = self.browser.find_elements_by_xpath(
            "//div[(starts-with(@class, 'accSummary') or "
            "@id='UTV-monthly') and preceding-sibling::{} and "
            "following-sibling::{}]".format(
                beginning_div_xpath, end_div_xpath
            )
        )
        if charge_elems:
            utv_charge_category, _ = ChargeCategory.get_or_create(
                category='utv',
                text='U-verse TV'
            )
            for elem in charge_elems:
                charge_type_text = elem.find_element_by_xpath("div[1]").text
                if charge_type_text.startswith('Monthly Charges'):
                    charge_type_text = 'Monthly Charges'
                m = re.search(
                    'Total {}.*?\$([0-9.]+)'.format(charge_type_text),
                    elem.text,
                    flags=re.DOTALL
                )
                charge_total = float(m.group(1))
                # save data to db
                charge_type_name = slugify(charge_type_text)
                # ChargeType
                charge_type, _ = ChargeType.get_or_create(
                    type=charge_type_name,
                    text=charge_type_text,
                    charge_category=utv_charge_category
                )
                # Charge
                try:
                    new_charge = Charge(
                        user=account_holder,
                        charge_type=charge_type,
                        billing_cycle=billing_cycle,
                        amount=charge_total
                    )
                    new_charge.save()
                except IntegrityError:
                    logger.warning(
                        'Trying to write duplicate charge record!\n%s',
                        new_charge.__dict__
                    )
        else:
            logger.info('No U-verse TV Charge Elements Found, skipped.')

        # ---------------------------------------------------------------------
        # U-verse Internet
        # ---------------------------------------------------------------------
        # beginning div
        beginning_div_xpath = (
            "div[starts-with(@class, 'MarLeft12 MarRight90') and "
            "descendant::div[contains(text(), 'U-verse Internet')]]"
        )
        # end div
        end_div_xpath = (
            "div[@class='Padbot5 topDotBorder MarLeft12 MarRight90' and "
            "descendant::div[contains(text(), "
            "'Total U-verse Internet Charges')]]"
        )
        charge_elems = self.browser.find_elements_by_xpath(
            "//div[(starts-with(@class, 'accSummary') or "
            "@id='UVI-monthly') and preceding-sibling::{} and "
            "following-sibling::{}]".format(
                beginning_div_xpath, end_div_xpath
            )
        )
        if charge_elems:
            uvi_charge_category, _ = ChargeCategory.get_or_create(
                category='uvi',
                text='U-verse Internet'
            )
            for elem in charge_elems:
                charge_type_text = elem.find_element_by_xpath("div[1]").text
                if charge_type_text.startswith('Monthly Charges'):
                    charge_type_text = 'Monthly Charges'
                m = re.search(
                    'Total {}.*?\$([0-9.]+)'.format(charge_type_text),
                    elem.text,
                    flags=re.DOTALL
                )
                charge_total = float(m.group(1))
                # save data to db
                charge_type_name = slugify(charge_type_text)
                # ChargeType
                charge_type, _ = ChargeType.get_or_create(
                    type=charge_type_name,
                    text=charge_type_text,
                    charge_category=uvi_charge_category
                )
                # Charge
                try:
                    new_charge = Charge(
                        user=account_holder,
                        charge_type=charge_type,
                        billing_cycle=billing_cycle,
                        amount=charge_total
                    )
                    new_charge.save()
                except IntegrityError:
                    logger.warning(
                        'Trying to write duplicate charge record!\n%s',
                        new_charge.__dict__
                    )
        else:
            logger.info('No U-verse Internet Charge Elements Found, skipped.')

        # ---------------------------------------------------------------------
        # Wireless
        # ---------------------------------------------------------------------
        # beginning div
        charged_users = users[:1]  # users who have a positive balance
        beginning_div_xpath = (
            "div[@class='MarLeft12 MarRight90 ' and "
            "descendant::div[contains(text(), '{name} {num}')]]"
        )
        # end div
        end_div_xpath = (
            "div[@class='topDotBorder accSummary MarLeft12 "
            "Padbot5 botMar10 botMar23ie' and "
            "descendant::div[contains(text(), 'Total for {num}')]]"
        )
        # first parse charges under account holder
        charge_elems = self.browser.find_elements_by_xpath(
            "//div[starts-with(@class, 'accSummary') and "
            "preceding-sibling::{} and following-sibling::{}]".format(
                beginning_div_xpath.format(name=account_holder.name,
                                           num=account_holder.number),
                end_div_xpath.format(num=account_holder.number)
            )
        )
        if charge_elems:
            wireless_charge_category, _ = ChargeCategory.get_or_create(
                category='wireless',
                text='Wireless'
            )
            for elem in charge_elems:
                charge_type_text = elem.find_element_by_xpath("div[1]").text
                offset = 0
                if charge_type_text.startswith('Monthly Charges'):
                    charge_type_text = 'Monthly Charges'
                    # get account monthly charge and discount
                    act_m_elem = elem.find_element_by_xpath("div[4]/div[1]")
                    m = re.search('.*?\$([0-9.]+)', act_m_elem.text, re.DOTALL)
                    w_act_m = float(m.group(1))

                    m = re.search(
                        'National Account Discount.*?\$([0-9.]+)',
                        elem.text,
                        flags=re.DOTALL
                    )
                    w_act_m_disc = float(m.group(1)) if m else 0
                    offset = w_act_m - w_act_m_disc
                m = re.search(
                    'Total {}.*?\$([0-9.]+)'.format(charge_type_text),
                    elem.text,
                    flags=re.DOTALL
                )
                charge_total = float(m.group(1)) - offset
                # save data to db
                charge_type_name = slugify(charge_type_text)
                # ChargeType
                charge_type, _ = ChargeType.get_or_create(
                    type=charge_type_name,
                    text=charge_type_text,
                    charge_category=wireless_charge_category
                )
                # Charge
                try:
                    new_charge = Charge(
                        user=account_holder,
                        charge_type=charge_type,
                        billing_cycle=billing_cycle,
                        amount=charge_total
                    )
                    new_charge.save()
                except IntegrityError:
                    logger.warning(
                        'Trying to write duplicate charge record!\n%s',
                        new_charge.__dict__
                    )
        else:
            raise ParsingError('No charges found for account holder.')

        # iterate regular users
        for user in users[1:]:
            charge_total = 0
            charge_elems = self.browser.find_elements_by_xpath(
                "//div[starts-with(@class, 'accSummary') and "
                "preceding-sibling::{} and following-sibling::{}]".format(
                    beginning_div_xpath.format(
                        name=user.name, num=user.number
                    ),
                    end_div_xpath.format(num=user.number)
                )
            )
            for elem in charge_elems:
                charge_type_text = elem.find_element_by_xpath("div[1]").text
                if charge_type_text.startswith('Monthly Charges'):
                    charge_type_text = 'Monthly Charges'
                m = re.search(
                    'Total {}.*?\$([0-9.]+)'.format(charge_type_text),
                    elem.text,
                    flags=re.DOTALL
                )
                charge_total = float(m.group(1)) - offset
                # save data to db
                charge_type_name = slugify(charge_type_text)
                # ChargeType
                charge_type, _ = ChargeType.get_or_create(
                    type=charge_type_name,
                    text=charge_type_text,
                    charge_category=wireless_charge_category
                )
                # Charge
                try:
                    new_charge = Charge(
                        user=user,
                        charge_type=charge_type,
                        billing_cycle=billing_cycle,
                        amount=charge_total
                    )
                    new_charge.save()
                except IntegrityError:
                    logger.warning(
                        'Trying to write duplicate charge record!\n%s',
                        new_charge.__dict__
                    )
            if charge_total > 0:
                charged_users.append(user)

        # update share of account monthly charges for each line
        # also calculate total wireless charges (for verification later)
        act_m_share = (w_act_m - w_act_m_disc) / len(charged_users)
        wireless_total = 0

        for user in charged_users:
            # ChargeType
            charge_type, _ = ChargeType.get_or_create(
                type='wireless-acount-monthly-charges-share',
                text='Account Monthly Charges Share',
                charge_category=wireless_charge_category
            )
            # Charge
            try:
                new_charge = Charge(
                    user=user,
                    charge_type=charge_type,
                    billing_cycle=billing_cycle,
                    amount=act_m_share
                )
                new_charge.save()
            except IntegrityError:
                logger.warning(
                    'Trying to write duplicate charge record!\n%s',
                    new_charge.__dict__
                )
            else:
                user_total = Charge.select(
                    pw.fn.Sum(Charge.amount).alias('total')
                ).join(
                    ChargeType,
                    on=Charge.charge_type_id == ChargeType.id
                ).where(
                    (Charge.user == user),
                    Charge.billing_cycle == billing_cycle,
                    ChargeType.charge_category == wireless_charge_category
                )
                wireless_total += user_total[0].total
        # now that we have wireless_total calculated from user charges
        # let's compare if it matches with what the bill says
        wireless_total_elem = self.browser.find_element_by_xpath(
            "//div[preceding-sibling::"
            "div[contains(text(), 'Total Wireless Charges')]]"
        )
        bill_wireless_total = float(wireless_total_elem.text.strip('$'))
        if abs(bill_wireless_total - wireless_total) > 0.01:
            raise CalculationError(
                'Wireless total calculated does not match with the bill'
            )
        logger.info('Wireless charges calculation results verified.')
        # aggregate monthly charges
        aggregate_wireless_monthly(billing_cycle)
        logger.info('Wireless charges aggregated %s.', billing_cycle_name)
        logger.info('Finished procesessing bill %s.', billing_cycle_name)

    def run(self, cycle_lags):
        """Login to AT&T billing page, parse previous bills and store data
        in database.

        param cycle_lags: lags of billing cycles for which you want to parse
            the bill. For example, 1 refers to last billing cycle (not current)
            and 5 refers to the one from 5 months ago. Currently it does
            not support parsing the most recent (current) bill, as AT&T uses
            a different page design for current bill. lags have to be positive
            integers.
        type cycle_lags: iterable
        """
        self.login()
        self.go_to_history_bills()
        wait = WebDriverWait(self.browser, PAGE_LOADING_WAIT_S)
        previous_bill_elems = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//td[@headers='view_bill']")
            )
        )
        # previous_bill_elems = self.browser.find_elements_by_xpath(
        #     "//td[@headers='view_bill']"
        # )
        for lag in cycle_lags:
            elem = previous_bill_elems[lag]
            elem.find_element_by_class_name('wt_Body').click()
            # billing page will be opened in a new window
            current_window = self.browser.current_window_handle
            self.browser.switch_to.window(self.browser.window_handles[-1])
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//h2[contains(text(), 'Account Details')]")
                    )
                )
                logger.info('No popup window detected.')
            except TimeoutException:
                # most likely there is a popup window
                self.try_click_no_on_popup()
            # sanity check
            try:
                self.browser.find_element_by_xpath(
                    "//h2[contains(text(), 'Account Details')]"
                )
            except NoSuchElementException:
                raise UrlError(
                    'Unable to locate the bill, maybe page took too long '
                    'to load, or failed to close popup window. Please retry.'
                )
            else:
                logger.info('Billing detail page sanity check passed.')
            self.split_previous_bill()
            self.browser.switch_to.window(current_window)
        self.browser.quit()
        logger.info('Browser closed.')


@click.command()
@click.argument('lags', nargs=-1, type=int)
def run_split_bill(lags):
    """Worker for parsing the website and splitting the bill.

    :param lags: lag between the first bill you want to parse and the last
        posted bill
    :type lags: list
    """
    # create table if not exists
    create_tables_if_not_exist()
    # split
    bill_splitter = AttBillSpliter()
    bill_splitter.run(lags)
    db.close()
