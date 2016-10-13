# att-bill-splitter

Are you an AT&T account holder for multiple wireless lines and tired of manually splitting the bill, typing every entry into a spreadsheet and sending each of them a custom text message every month? Now you are lucky because this little application automates all of that and all you need to do is a press of button. It requires very little setup and is straightforward enough to use even if you have little experience with command line tools.

## Overview

This package is written in Python3 and uses selenium (ChromeDriver) to handle login and web parsing. peewee is used as the ORM and data are stored in a Sqlite database. It also has twilio integration to send auto-generated monthly billing details to each user. Currently it only works on Mac OS X.

What it does:

  - Log in to your AT&T account.
  - Navigate to history billings, parse and split them. (you can specify which bills to parse and split)
  - Persist data (user, billingcycle, chargecategory, chargetype, charge, monthlybill) in a Sqlite database locally.
  - Aggregate charges for each user in a billing cycle and generate billing details.
  - Send billing details to each user via text message.
  
## Installation
```
[~] git clone https://github.com/brian-ds/att-bill-splitter.git
[~] cd att-bill-splitter
[att-bill-splitter] python3 setup.py install
```
All set! Just that simple!

*If you know python and like to keep your local packages clean. I would recommed using a virtualenv to isolate all the dependencies of this application from your local packages.*

## Usage
### Parse and Split the Bill
This is the first thing you run. A Chrome browser will be fired up in the background. You will be prompted to input your AT&T username and password (within terminal). Once logged in, it will start parsing your history bills, splitting them and storing data to database.
```
[att-bill-splitter]att-split-bill LAG_BILL_1 [LAG_BILL_2 ...]
```
`LAG_BILL_1` (an integer) is the lag between the first bill you want to parse and the last posted bill. For example, 0 refers to the last posted billing cycle (not yet supported! more details below), and 1 refers to billing cycle before that, so on an so forth. As it's running, you will see logs printed to your console. And data are stored in `att_bill.db`.

For example,
```
[att-bill-splitter] att-split-bill 1
👤  Username: your_user_name
🗝  Password: 
2016-10-13 14:09:16,437 - INFO - login succeeded.
2016-10-13 14:09:22,418 - INFO - landed at history billings page.
2016-10-13 14:09:34,520 - INFO - No popup window detected.
2016-10-13 14:09:34,540 - INFO - Billing detail page sanity check passed.
2016-10-13 14:09:34,540 - INFO - Start processing new bill...
2016-10-13 14:09:36,380 - INFO - Parsing User info succeeded.
2016-10-13 14:09:39,267 - INFO - Wireless charges calculation results verified.
2016-10-13 14:09:39,278 - INFO - Wireless charges aggregated Jul 15 - Aug 14, 2016.
2016-10-13 14:09:39,279 - INFO - Finished procesessing bill Jul 15 - Aug 14, 2016.
2016-10-13 14:09:39,346 - INFO - Browser closed.
```
Sometimes promotion or survey window pops up on AT&T web pages. I tried my best to handle them wherever I can. There are still cases (very rare though) when a survey window pops up a while after the billing page has been loaded. If you see such errors, please retry. 

### View Monthly Charges Summary for Users
After you parsed the bills, you can view them in your terminal. The command below will print the monthly summary for each user.
```
[att-bill-splitter] att-print-summary MONTH [YEAR]
```
`MONTH` (1-12) refers to the month of the end date of the billing cycle. For example if you want to view billing cycle is Sep 15 - Oct 14, `MONTH` should be `10`. `YEAR` (optional) should be 4-digit.

For example,
```
[att-bill-splitter] att-print-summary 8

--------------------------------------------------------------
    Charge Summary for Billing Cycle Jul 15 - Aug 14, 2016
--------------------------------------------------------------
       USER_NAME_1     (415-555-0001)      Total: 72.99
       USER_NAME_3     (415-555-0003)      Total: 62.67
       USER_NAME_4     (415-555-0004)      Total: 31.42
       USER_NAME_5     (415-555-0005)      Total: 31.42
       USER_NAME_6     (415-555-0006)      Total: 72.99
       USER_NAME_7     (415-555-0007)      Total: 32.42
       USER_NAME_8     (415-555-0008)      Total: 31.42
       USER_NAME_9     (415-555-0009)      Total: 61.42
--------------------------------------------------------------
                                 Wireless Total: 444.52
```

### View Monthly Charges Details for Users
You can also view itemized charge details for each user.
```
[att-bill-splitter] att-print-details MONTH [YEAR]
```
`MONTH` (1-12) refers to the month of the end date of the billing cycle. For example if you want to view billing cycle is Sep 15 - Oct 14, `MONTH` should be `10`. `YEAR` (optional) should be 4-digit.

For example,
```
(venv) [att-bill-splitter] att-print-details 8 -y 2016

    USER_NAME_1 (415-555-0001)
      - Monthly Charges                            15.00
      - Equipment Charges                          42.50
      - Surcharges & Fees                          2.69
      - Government Fees & Taxes                    2.66
      - Account Monthly Charges Share              10.14
      - Total                                      72.99

    USER_NAME_2 (415-555-0002)
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

You will be prompt to input your Twilio number, account SID and authentication token. You can get them in a minute for free at www.twilio.com. You will also be asked to input a short message to put at the end of the text messages you send to your users, for instance, to tell your users how to pay you.
```
[att-bill-splitter] att-notify-users MONTH [YEAR]
```
`MONTH` (1-12) refers to the month of the end date of the billing cycle. For example if you want to view billing cycle is Sep 15 - Oct 14, `MONTH` should be `10`. `YEAR` (optional) should be 4-digit.
For example,
```
[att-bill-splitter]  att-notify-users 8 --year 2016
Twilio Number (e.g. +11234567890): your_twilio_number
Twilio Account SID: your_account_sid
Twilio Authentication Token: your_auth_token
✅  Twilio account added.
You can enter a short message to put after the charge details to send to your users. (For example, letting your users know how to pay you)
-> Please Venmo me at Brianz56.
✅  Payment message saved.

415-555-0001
Hi USER_NAME_1 (415-555-0001),
Your AT&T Wireless Charges for Jul 15 - Aug 14, 2016:
  - Monthly Charges                15.00
  - Equipment Charges              42.50
  - Surcharges & Fees              2.69
  - Government Fees & Taxes        2.66
  - Account Monthly Charges Share  10.14
  - Total                          72.99 🤑

Notify (y/n)?
```
If you type `y`, it will call Twilio API to send the message to user 1 @ 415-555-0001 with the extra payment message you inputed upfront. At the mean time, all messages sent are logged in `notif_history.log` file in `att-bill-splitter` directory to help you manage all the history activities.

## FAQ

### Why it doesn't support parsing of the last posted bill?
AT&T uses a different web design for last posted bill (with Ajax, details expandable, different element idenfiers) from previously posted ones (static html). I usually send the splitted bills to my users a few months late, so I wasn't motivated enough to tackle this problem yet.

### How can I take look at the data stored in the database?
You can download a light weight DB browser for sqlite at http://sqlitebrowser.org/. Then click `Open DataBase` from the top, navigate to `att-bill-splitter/attbillsplitter/` and add `att_bill.db`. Now you are good to go.

If for any reason it doesn't work for you, please let me know by either creating an issue or sending me an email at leapingzhang@gmail.com. You'll get my attention very soon.
