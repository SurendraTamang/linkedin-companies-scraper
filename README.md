

# LinkedIn Company Scraper

This is a Scrapy spider designed to scrape company information and employee details from LinkedIn. The script uses Selenium to handle dynamic content and login functionality.


---
This code  was written for my client project  in **2020-02-18** so may not work now . 

## Table of Contents
1. [Overview](#overview)
2. [Dependencies](#dependencies)
3. [Script Structure](#script-structure)
4. [How It Works](#how-it-works)
5. [Usage](#usage)
6. [Output](#output)
7. [Notes](#notes)

---

## Overview

The script scrapes LinkedIn company pages for the following details:
- Company name
- Website
- Industry
- Company size
- Employee details (name, title, LinkedIn profile URL)

It also handles cases where the company page is unavailable and logs these cases in a separate file.

---

## Dependencies

To run this script, you need the following Python libraries:
- `scrapy`
- `scrapy-selenium`
- `selenium`
- `csv`
- `os`
- `pathlib`

Install the required libraries using pip:
```bash
pip install scrapy scrapy-selenium selenium
```

---

## Script Structure

The script is structured as follows:

1. **Initialization**:
   - Reads a CSV file (`links.csv`) containing company names and LinkedIn URLs.
   - Initializes a list to store unavailable company pages.

2. **Login**:
   - Uses Selenium to log in to LinkedIn.

3. **Scraping**:
   - Iterates through the list of companies and scrapes their "About" and "People" pages.
   - Extracts company details and employee information.

4. **Output**:
   - Saves scraped data in a structured format.
   - Logs unavailable company pages in `unavailable.csv`.

---

## How It Works

1. **Initialization**:
   - The script reads a CSV file (`links.csv`) located two directories above the script's location.
   - The CSV file should contain company names and their corresponding LinkedIn URLs.

2. **Login**:
   - The script navigates to the LinkedIn login page and enters the provided email and password.

3. **Scraping**:
   - For each company, the script:
     - Navigates to the company's "About" page to extract website, industry, and company size.
     - Navigates to the company's "People" page to extract employee details.

4. **Error Handling**:
   - If a company page is unavailable, it logs the company name and URL in `unavailable.csv`.

5. **Output**:
   - The scraped data is yielded as a dictionary for each company.
   - The script closes the Selenium driver
