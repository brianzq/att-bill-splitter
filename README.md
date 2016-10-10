# att-bill-splitter

Are you an AT&T account holder for multiple wireless lines and tired of manually splitting the bill, typing every entry into a spreadsheet and sending each of them a custom text message every month? Now you are lucky because this service automates all of them and all you need to do is a press of button. If you happen to be a U-verse TV and/or Internet user also, not a problem.

## Overview

This package is written in Python3 and uses selenium (ChromeDriver) to handle login and web parsing. peewee is used as the ORM and data are stored in a Sqlite database. It also has twilio integration to send auto-generated monthly billing details to each user.

What it does:

  - Log in to your AT&T account.
  - Navigate to history billings, parse and split them. (you can specify which bills to parse and split)
  - Persist data (user, billingcycle, chargecategory, chargetype, charge, monthlybill) in a Sqlite database locally.
  - Aggregate charges for each user in a billing cycle and generate billing details.
  - Send billing details to each user via text message.
  
## Installation
```
[~] git clone git@github.com:brian-ds/att-bill-splitter.git
[~] cd att-bill-splitter
[att-bill-splitter] python3 setup.py install
```
I would recommed using a virtualenv to isolate all the dependencies for this app from your local packages. To do so,
```
[~] git clone git@github.com:brian-ds/att-bill-splitter.git
[~] cd att-bill-splitter
[att-bill-splitter] virtualenv-3.4 venv
[att-bill-splitter] source venv/bin/activate
(venv) [att-bill-splitter] python3 setup.py install
```
*Note: As selenium webdriver relys on chromedriver which is a separate executable from your local Chrome browser, you need to download it too. You can download the latest release from https://sites.google.com/a/chromium.org/chromedriver/downloads and install it.*

## Configuration

Please follow these steps to configure the application:
1. Provide your AT&T account username and password in `config.ini`.
2. Either add the path to chromedriver executable to your PATH variable or in `config.ini` under `settings` section. for example
```
[settings]
page_loading_wait_s = 20
chromedriver = /Users/Brian/Downloads/chromedriver
```
3. (Optional) If you also want the texting feature, add in `config.ini` your twilio number and API key. You can get a free API key at https://www.twilio.com/. Note that for twilio trial account, you have to verify the phone number before you can use the API to send text message to that number. It's fairly easy to do it though. To make it easier for your users to pay you, you can add some payment options at the end of the text message you send by setting the `payment_msg` in `config.ini`.

## Usage
### Parse and Split the Bill
This is the first thing you run. This will start parsing your history bills, splitting them and storing data to database.
*NOTE: If you are running this in `att-bill-splitter` directory, you need to modify `config.ini` to the path to the config file.*
```
[att-bill-splitter]run-split-bill config.ini LAG_BILL_1 [LAG_BILL_2 ...]
```
`LAG_BILL_1` (an integer) is the lag between the first bill you want to parse and the last posted bill. For example, 0 refers to the last posted billing cycle (not yet supported! more details below), and 1 refers to billing cycle before that, so on an so forth. As it's running, you will see loggings printed to your console. And data are stored in `att_bill.db`.
Like most web crawlers, the success of parsing relies on a couple of variables, a good Internet connection, AT&T not redesigning their billing page and no unexpected web activities (like popup survey window). In this app, I set the page loading timeout threshold to be 20 seconds. If you keep getting TimeoutError, you might want to tune it up. Also throughtout the parsing process I tried my best to handle popup windows wherever I can. There are still cases (very rare though) when a survey window pops in a while after the billing page has been loaded. If you see such errors, please retry. 

### View Monthly Charges Summary for Users
After you parsed the bills, you can view them in your terminal. The command below will print the monthly summary for each user.
```
[att-bill-splitter]run-print-summary MONTH [YEAR]
```
`MONTH` (1-12) refers to the month of the end date of the billing cycle. For example if you want to view billing cycle is Sep 15 - Oct 14, `MONTH` should be `10`. `YEAR` (optional) should be 4-digit.
It looks like this
```
--------------------------------------------------------------
    Charge Summary for Billing Cycle Mar 15 - Apr 14, 2016
--------------------------------------------------------------
       USER_NAME_1     (415-555-0001)      Total: 72.99
       USER_NAME_2     (415-555-0002)      Total: 67.25
       USER_NAME_3     (415-555-0003)      Total: 62.67
       USER_NAME_4     (415-555-0004)      Total: 31.42
       USER_NAME_5     (415-555-0005)      Total: 31.42
       USER_NAME_6     (415-555-0006)      Total: 72.99
       USER_NAME_7     (415-555-0007)      Total: 32.42
       USER_NAME_8     (415-555-0008)      Total: 31.42
       USER_NAME_9     (415-555-0009)      Total: 61.42
--------------------------------------------------------------
```

### View Monthly Charges Details for Users
You can also view itemized charge details for each user.
```
[att-bill-splitter]run-print-details MONTH [YEAR]
```
`MONTH` (1-12) refers to the month of the end date of the billing cycle. For example if you want to view billing cycle is Sep 15 - Oct 14, `MONTH` should be `10`. `YEAR` (optional) should be 4-digit.
It looks like this
```
    USER_NAME_1 (415-555-0001)
      - Monthly Charges                            15.00
      - Equipment Charges                          42.50
      - Surcharges & Fees                          2.69
      - Government Fees & Taxes                    2.66
      - Account Monthly Charges Share              10.14
      - Total                                      72.99

    USER_NAME_1 (415-555-0002)
      - Monthly Charges                            15.00
      - Equipment Charges                          37.50
      - Surcharges & Fees                          2.69
      - Government Fees & Taxes                    1.92
      - Account Monthly Charges Share              10.14
      - Total                                      67.25
  ...
 ```
### Send Monthly Charge Details to Users via SMS
View each user's monthly charge details (and total) and decide if you want to send it to the user via SMS.
*NOTE: If you are running this in `att-bill-splitter` directory, you need to modify `config.ini` to the path to the config file.*
```
[att-bill-splitter]run-notify-users config.ini MONTH [YEAR]
```
`MONTH` (1-12) refers to the month of the end date of the billing cycle. For example if you want to view billing cycle is Sep 15 - Oct 14, `MONTH` should be `10`. `YEAR` (optional) should be 4-digit.
It looks like this
```
Hi USER_NAME_1 (415-555-0001),
Your AT&T Wireless Charges for Jul 15 - Aug 14, 2016:
  - Monthly Charges                15.00
  - Equipment Charges              37.50
  - Surcharges & Fees              2.69
  - Government Fees & Taxes        1.92
  - Account Monthly Charges Share  10.14
  - Total                          67.25

Notify (y/n)?
```
If you type `y`, it will call Twilio API to send the message to user 1 @ 415-555-0001 with the extra payment message you edited in `config.ini`. At the mean time, all messages sent are logged in `notif_history.log` file in `att-bill-splitter` directory to help you manage all the history activities.

## FAQ

### Why it doesn't support parsing of the last posted bill?
AT&T uses a different web design for last posted bill (with Ajax, details expandable, different element idenfiers) from previously posted ones (static html). I usually send the splitted bills to my users a few months late, so I wasn't motivated enough to tackle this problem yet.

### How can I take look at the data stored in the database?
You can download a light weight DB browser for sqlite at http://sqlitebrowser.org/. Then click `Open DataBase` from the top, navigate to `att-bill-splitter/attbillsplitter/` and add `att_bill.db`. Now you are good to go.

If for any reason it doesn't work for you, please let me know by either creating an issue or sending me an email at leapingzhang@gmail.com. You'll get my attention very soon.
