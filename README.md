# att-bill-splitter

Are you an AT&T account holder for multiple wireless lines and tired of manually splitting the bill, typing every entry into a spreadsheet and sending each of them a custom text message every month? Now you are lucky because this service automates all of them and all you need to do is a press of button. If you happen to be a U-verse TV and/or Internet user also, not a problem.

## Overview

This package is written in Python3 and uses selenium (ChromeDriver) to handle login and web parsing. peewee is used as the ORM and data are stored in a Sqlite database. It also has twilio integration to send auto-generated monthly billing details to each user.

What it does:

  - Log in to your AT&T account.
  - Navigate to history billings, parse and split them. (you can specify which bills to parse and split)
  - Persist data (user, billingcycle, chargecategory, chargetype and charge) in a Sqlite database locally.
  - Aggregate charges for each user in a billing cycle and generate billing details. (TODO)
  - Send billing details to each user via text message. (TODO)
  
## Installation
```
git clone git@github.com:brian-ds/att-bill-splitter.git
cd att-bill-splitter
python3 setup.py install
```
As selenium runs on ChromeDriver which is a separate executable from your local Chrome browser, you need to download it too. You can download the latest release from https://sites.google.com/a/chromium.org/chromedriver/downloads and install it.

## Configuration

To make it work for you, you need to provide your AT&T account username and password, together with a phonebook of names and numbers for all the lines in your account (with account holder as the first entry) in `att-bill-splitter/attbillsplitter/settings.py`.

If you also want the texting feature, you will need a twilio number and an API key. You can get a free API key within a minute at https://www.twilio.com/.

## Usage
```
run-split-bill LAG_BILL_1 [LAG_BILL_2 ...]
```
LAG_BILL_1 (an integer) is the lag between the first bill you want to parse and the last posted bill. For example, 0 refers to the last posted billing cycle (not yet supported! more details below), and 1 refers to billing cycle before that, so on an so forth.

I'm currently working on the charges aggregation and twilio integration, stay tuned.

## FAQ

### Why it doesn't support parsing of the last posted bill?
AT&T uses a different web design for last posted bill (with Ajax, details expandable, different element idenfiers) from previously posted ones (static html). I usually send the splitted bills to my users a few months late, so I wasn't motivated enough to tackle this problem yet.

### Now that I splitted the bill, how can I take look at the data stored in the database?
You can download a light weight DB browser for sqlite at http://sqlitebrowser.org/. Then click `Open DataBase` from the top, navigate to `att-bill-splitter/attbillsplitter/` and add `att_bill.db`. Now you are good to go.

### It does not work for me, Why?
So far I've only tested it on my own account (AT&T Mobile Share Value Plan with U-verse TV and Internet). If you are under a different plan and this package does not work for you, or for any reason that it doesn't work for you, please let me know by either creating an issue or sending me an email at leapingzhang@gmail.com. You'll get my attention very soon.
