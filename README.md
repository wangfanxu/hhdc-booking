# bbdc-booking

It is for checking practical slots in BBDC website.

## Prerequisite

* Python3
* Download [chrome driver](http://chromedriver.chromium.org/)

## Setup

1. Clone the repo

```bash
git clone https://github.com/weimingwill/bbdc-booking.git
```

2. Setup virtual env

```bash
virtualenv env
source env/bin/activate
pip install -r requirement.txt
```

## How to use

1. Create a new file named `config.json` in the root directory locally following below template.

```json
{
  "bbdc": {
    "username": "your-bbdc-username",
    "password": "your-bbdc-password"
  },
  "gmail": {
    "email": "your-email-to-receive-notification@gmail.com",
    "password": "your-email-password"
  },
  "want_months": ["May/2019","Jun/2019"],
  "want_sessions": ["1", "6", "8"],
  "want_days": ["2","3","4","5","6"],
  "chrome_path": "chromedriver"
}
```

Make sure that your selenium chrome driver path is correct.

2. Schedule it to run using `crontab` with `run.sh` (or other scheduling tool)

```bash
# Schedule it to run every 10 minutes
*/10 * * * * /home/weiming/bbdc-booking/run.sh >> /home/weiming/bbdc-booking/system.log 2>&1
```
