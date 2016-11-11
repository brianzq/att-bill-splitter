# att-bill-splitter

Are you an AT&T account holder for multiple wireless lines and tired of manually splitting the bill, typing every entry into a spreadsheet and sending each of them a custom text message every month? Now you are lucky because this little application automates all of that and all you need to do is a press of button. It requires very little setup and is straightforward enough to use even if you have little experience with command line tools.

## Overview

This package is written in Python3 and uses requests and beautifulsoup4 to login your AT&T account and parse the bills. peewee is used as the ORM and data are stored in a Sqlite database. It also has twilio integration to send auto-generated monthly billing details to each user.

## Installation
```
[~] git clone https://github.com/brian-ds/att-bill-splitter.git
[~] cd att-bill-splitter
[att-bill-splitter] python3 setup.py install
```
All set! Just that simple!

*I would recommed using a virtualenv to isolate all the dependencies of this application from your local packages.*

## Quick Start
### Parse and Split All your Bills
This is the first thing you run. You will be prompted to input your AT&T username and password (within terminal). Once logged in, it will start parsing your history bills, splitting them and storing data to database.
```
[att-bill-splitter]att-split-bill
```
For example,
```
(att) [att-bill-splitter] att-split-bill
👤  AT&T Username: your_user_name
🗝  AT&T Password:
Login started...
Start splitting bill Sep 15 - Oct 14, 2016...
Finished splitting bill Sep 15 - Oct 14, 2016.
Start splitting bill Aug 15 - Sep 14, 2016...
Finished splitting bill Aug 15 - Sep 14, 2016.
Start splitting bill Jul 15 - Aug 14, 2016...
Finished splitting bill Jul 15 - Aug 14, 2016.
Start splitting bill Jun 15 - Jul 14, 2016...
Finished splitting bill Jun 15 - Jul 14, 2016.
Start splitting bill May 15 - Jun 14, 2016...
Finished splitting bill May 15 - Jun 14, 2016.
...
```
Sometimes promotion or survey window pops up on AT&T web pages. If you got any elements not found error, you might be able to resolve it by manually logging in to your account in a browser, clicking No on the popup window before you rerun `att-split-bill`.

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

If for any reason it doesn't work for you, please let me know by either creating an issue or sending me an email at leapingzhang@gmail.com. You'll get my attention very soon.
