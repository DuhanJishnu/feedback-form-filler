# Google Form Playwright Test Tool

A Python + Playwright project for testing Google Forms using structured
data from `feedback.txt`.

> **Important:** Use this automation only with forms you own or are
> explicitly authorized to test. Do not use it to create duplicate,
> fabricated, or manipulated responses in institutional surveys or other
> real-world feedback systems.

## Project Structure

``` text
google-form-bot/
├── form_bot.py
├── config.py
├── feedback.txt
├── requirements.txt
├── README.md
└── playwright-profile/
```

  File                    Purpose
  ----------------------- -----------------------------------
  `form_bot.py`           Main Playwright automation
  `config.py`             Form URL and timing configuration
  `feedback.txt`          Test data
  `requirements.txt`      Python dependencies
  `playwright-profile/`   Persistent browser session

## 1. Requirements

You need Python 3.10+ and Playwright.

Check Python:

``` powershell
python --version
```

## 2. Installation

Install dependencies:

``` powershell
pip install -r requirements.txt
```

Install Chromium:

``` powershell
playwright install chromium
```

If you do not have `requirements.txt`, create it with:

``` text
playwright
```

## 3. Configure `config.py`

``` python
FORM_URL = "https://your-authorized-test-form-url"
HEADLESS = False

MIN_DELAY = 0.8
MAX_DELAY = 2.2
```

Keep `HEADLESS=False` while debugging so you can see the browser.

## 4. Prepare `feedback.txt`

Each record is separated by `---`.

Example:

``` text
PROGRAMME=B. Tech
DEPARTMENT=CS
SEMESTER=7th
COURSE_CODE=CS413
INSTRUCTOR=Instructor Name
RATING=5
COMMENT_INSTRUCTOR=Hardworking and knowledgeable
COMMENT_COURSE=Efficient and sufficient

---

PROGRAMME=B. Tech
DEPARTMENT=CS
SEMESTER=7th
COURSE_CODE=CS417
INSTRUCTOR=Another Instructor
RATING=5
COMMENT_INSTRUCTOR=Hardworking and knowledgeable
COMMENT_COURSE=Efficient and sufficient
```

The parser expects one `KEY=VALUE` pair per line.

## 5. Authentication

If the authorized test form requires Google authentication, the project
uses:

``` text
playwright-profile/
```

as a persistent browser profile.

Run:

``` powershell
python .\form_bot.py
```

and complete authentication manually if requested.

Do not commit this directory to Git because it can contain session
information.

Add to `.gitignore`:

``` gitignore
playwright-profile/
__pycache__/
*.pyc
.env
```

## 6. Run

``` powershell
python .\form_bot.py
```


This project is intended for browser automation testing and educational
use on forms you own or are authorized to test.

Do not use it to spam forms, create duplicate/fabricated survey
responses, bypass response restrictions, or manipulate
institutional/public feedback data.
