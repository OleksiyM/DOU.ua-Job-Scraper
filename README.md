- [DOU.ua Job Scraper](#douua-job-scraper)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
  - [Approach](#approach)
  - [Solution](#solution)
  - [Summary](#summary)
  - [License](#license)

# DOU.ua Job Scraper

This project implements a Python web scraper to extract job postings from [jobs.dou.ua](https://jobs.dou.ua/). It can scrape data from both the main website search results and the RSS feed, providing flexibility and comprehensive data collection.

## Features

*   **Website Scraping:** Extracts job listings from the main search results pages on jobs.dou.ua, including:
    *   Job ID
    *   Job Title (Role)
    *   Company Name
    *   Company DOU.ua Page URL
    *   City/Location
    *   Job Detail Page URL
    *   Salary (if available)
    *   Detailed Job Description (with preserved formatting: paragraphs, lists)
    *   Extracted Skills (using keyword matching)
    *   Date Scraped
*   **RSS Feed Scraping:** Fetches job listings from the jobs.dou.ua RSS feed, providing an alternative and often faster way to get data.  Includes the same detailed information as website scraping by fetching each job's detail page.
*   **Filtering:** Supports filtering by job category, remote work (boolean), and experience level (string).
*   **CSV Output:** Saves the scraped data to a CSV file, with separate files for website and RSS feed scraping.
*   **Error Handling:** Includes robust error handling for network requests, HTML/XML parsing, and data extraction.
*   **Modular Design:** Uses separate functions for URL generation, data extraction, and detail page fetching, making the code well-organized and maintainable.
*   **Respectful Scraping:** Includes delays between requests to avoid overloading the target website.

## Prerequisites

*   Python 3.6+
*   `requests` library (`pip install requests`)
*   `beautifulsoup4` library (`pip install beautifulsoup4`)

## Usage

The script provides two main functions:

*   `main(category, remote=False, experience=None)`: Scrapes job data from the website's search results.
*   `rss_main(category, remote=False, experience=None)`: Scrapes job data from the RSS feed.

Both functions take the following arguments:

*   `category` (str):  The job category to search for (e.g., "Python", "Data Science", "Analyst").  See below for a full list of valid categories.
*   `remote` (bool, optional):  If `True`, filters for remote jobs.  Defaults to `False`.
*   `experience` (str, optional):  Filters by experience level.  Valid options are: "0-1", "1-3", "3-5", "5plus".  If not specified, all experience levels are included.

**Example Usage (in a Python script or Jupyter Notebook):**

```python
# from your_script_name import main, rss_main  # If running from a separate script

# Scrape remote Python jobs with 1-3 years of experience from the website:
main("Python", remote=True, experience="1-3")

# Scrape Data Science jobs (all locations and experience levels) from the RSS feed:
rss_main("Data Science")

# Scrape Analyst jobs in Kyiv, all experience levels, from the website:
main("Analyst", remote=False)  # No need to specify experience if you want all.
```

**Valid Job Categories:**

".NET", "Account Manager", "AI/ML", "Analyst", "Android", "Animator", "Architect", "Artist", "Assistant", "Big Data", "Blockchain", "C++", "C-level", "Copywriter", "Data Engineer", "Data Science", "DBA", "Design", "DevOps", "Embedded", "Engineering Manager", "Erlang", "ERP/CRM", "Finance", "Flutter", "Front End", "Golang", "Hardware", "HR", "iOS/macOS", "Java", "Legal", "Marketing", "Node.js", "Office Manager", "Other", "PHP", "Product Manager", "Project Manager", "Python", "QA", "React Native", "Ruby", "Rust", "Sales", "Salesforce", "SAP", "Scala", "Scrum Master", "Security", "SEO", "Support", "SysAdmin", "Technical Writer", "Unity", "Unreal Engine", "Військова справа"

**Output:**

The script creates CSV files in the same directory where it's run.

*   `main` function creates files named:  `{category}_jobs_{YYYYMMDD_HHMMSS}.csv`
*   `rss_main` function creates files named: `rss_{category}_jobs_{YYYYMMDD_HHMMSS}.csv`

**CSV File Structure:**

The CSV files have the following columns:

*   `id`:  The unique job ID from the DOU.ua URL.
*   `title`:  The job title (role).
*   `company`:  The company name.
*   `company_dou_url`:  The URL of the company's page on DOU.ua.
*   `city`:  The job location (city or "Remote").
*   `url`:  The URL of the job detail page.
*   `salary`:  The salary (if available).
*   `detailed_description`:  The full job description, with paragraphs and lists preserved.
*   `skills`:  A list of extracted skills (keywords).
*   `date_scraped`:  The date and time when the data was scraped.

## Approach

1.  **Website Analysis:** The HTML structure of jobs.dou.ua was analyzed using browser developer tools to identify the relevant tags and attributes for data extraction.  The RSS feed structure was also examined.
2.  **Core Scraping Implementation:**  `requests` is used to fetch HTML content, and `BeautifulSoup` is used for parsing.  Functions were created to extract data from both the main search results page and individual job detail pages.
3.  **Detailed Information Extraction:**  The script fetches each job's detail page to extract the full description, skills, company information, and role.
4.  **RSS Feed Integration:**  The `xml.etree.ElementTree` module is used to parse the XML data from the RSS feed.  A separate function (`rss_main`) handles RSS feed scraping, providing an alternative data source.
5.  **Skill Extraction:**  A keyword-based approach is used to extract skills from the detailed job descriptions.
6.  **Error Handling:**  `try...except` blocks are used throughout the code to handle potential network errors, parsing errors, and missing data.
7. **Code modularity:** Code refactored and splitted by function for better readibility.
8. **Respectful Scraping**: Added delays

## Solution

This solution achieves the project objectives by providing a robust and flexible way to scrape job data from jobs.dou.ua. It can retrieve data from both the main website and the RSS feed, offering alternative data sources. The script extracts comprehensive information, including detailed descriptions and skills. The use of functions and error handling makes the code maintainable and reliable. The CSV output provides a structured format for further analysis and use.

## Summary
Developed a Python web scraper using Requests, BeautifulSoup, and XML parsing to extract comprehensive job data, including detailed descriptions and skills, from `jobs.dou.ua`, saving the results to `CSV` files. The solution supports both website and `RSS` feed scraping, providing flexibility and robust data capture.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
