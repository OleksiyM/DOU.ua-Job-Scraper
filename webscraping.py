## Step 1: Importing Required Libraries


import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import re
import xml.etree.ElementTree as ET

## Step 2:

def generate_url(category, remote=False, experience=None):
    """Generates a URL for the jobs.dou.ua website with filters."""
    base_url = "https://jobs.dou.ua/vacancies/"
    url = f"{base_url}?"
    if remote:
        url += "remote&"
    url += f"category={category.replace(' ', '+')}"
    if experience:
        url += f"&exp={experience}"
    return url

def extract_job_data(job_card):
    """Extracts data from a single job posting card (used by main function)."""
    try:
        title_link = job_card.find('a', class_='vt')
        job_title = title_link.text.strip()
        job_url = title_link['href']


        match = re.search(r'/vacancies/(\d+)/?', job_url)
        job_id = int(match.group(1)) if match else None


        company_link = job_card.find('a', class_='company')
        company_name = company_link.text.strip()

        city_span = job_card.find('span', class_='cities')
        city = city_span.text.strip() if city_span else "N/A"
        if "віддалено" not in city.lower() and "remote" in generate_url(job_title).lower():
            city = "Remote"

        salary = None
        salary_span = job_card.find('span', class_='salary')
        if salary_span:
            salary = salary_span.text.strip()

        job_data = {
            'id': job_id,
            'title': job_title,
            'company': company_name,
            'company_dou_url': company_link['href'] if company_link else "N/A",
            'city': city,
            'url': job_url,
            'salary': salary,
            'detailed_description': "",
            'skills': [],
            'date_scraped': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return job_data

    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error extracting data from job card: {e}")
        return None

def extract_rss_job_data(item):
    """Extracts data from a single RSS feed item."""
    try:
        title = item.find('title').text if item.find('title') is not None else "N/A"
        link = item.find('link').text if item.find('link') is not None else "N/A"

        match = re.search(r'/vacancies/(\d+)/?', link)
        job_id = int(match.group(1)) if match else None

        job_data = {
            'id': job_id,
            'title': title,
            'company': "N/A",
            'company_dou_url': "N/A",
            'city': "N/A",
            'url': link,
            'salary': None,
            'detailed_description': "",
            'skills': [],
            'date_scraped': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return job_data

    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error extracting data from RSS item: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing job ID: {e}")
        return None


def extract_detailed_description_and_skills(detail_url):
    """Fetches detailed job info, including company DOU URL and role."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(detail_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        vacancy_section = soup.find('div', class_='b-typo vacancy-section')
        if not vacancy_section:
            return "", [], None, "N/A", "N/A", "N/A", "N/A"

        detailed_description_parts = []
        for element in vacancy_section.children:
            if element.name == 'p':
                detailed_description_parts.append(element.get_text(strip=True))
            elif element.name == 'ul':
                list_items = ["- " + li.get_text(strip=True) for li in element.find_all('li')]
                detailed_description_parts.append("\n".join(list_items))
            elif element.name == 'ol':
                list_items = [f"{i+1}. {li.get_text(strip=True)}" for i, li in enumerate(element.find_all('li'))]
                detailed_description_parts.append("\n".join(list_items))
            elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                detailed_description_parts.append(element.get_text(strip=True))
        detailed_description = "\n\n".join(detailed_description_parts)

        skills = extract_skills(detailed_description)

        company_dou_url = "N/A"
        company_link_container = soup.find('div', class_='l-n')
        if company_link_container:
             company_link = company_link_container.find('a', href=True)
             if company_link:
                company_dou_url = company_link['href']
                company_name = company_link.text.strip()

        role = "N/A"
        role_h1 = soup.find('h1', class_='g-h2')
        if role_h1:
            role = role_h1.text.strip()

        city = "N/A"
        city_span = soup.find('span', class_='place')
        if city_span:
            city = city_span.text.strip()
            if "віддалено" not in city.lower() and "remote" in detail_url.lower():
                city = "Remote"

        salary = None
        salary_span = soup.find('span', class_='salary')
        if salary_span:
            salary = salary_span.text.strip()

        return detailed_description, skills, salary, company_name, city, company_dou_url, role

    except requests.exceptions.RequestException as e:
        print(f"Error fetching detailed description: {e}")
        return "", [], None, "N/A", "N/A", "N/A", "N/A"

    except (AttributeError, KeyError, TypeError) as e:
        print(f"An unexpected error occurred: {e}")
        return "", [], None, "N/A", "N/A", "N/A", "N/A"

def extract_skills(text):
    """Extracts skills from the detailed job description text."""
    skills_set = set()
    skill_keywords = {
        "Programming Languages": ["Python", "Java", "C++", "C#", "JavaScript", "Ruby", "Go", "PHP", "Swift", "Kotlin", "TypeScript", "Rust", "Scala", "R"],
        "Frameworks/Libraries": ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring", "Ruby on Rails", ".NET", "ASP.NET", "jQuery", "Bootstrap", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Express.js", "FastAPI"],
        "Databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "Redis", "Cassandra", "DynamoDB", "SQL Server", "SQLite"],
        "Cloud Platforms": ["AWS", "Azure", "Google Cloud Platform", "GCP", "Heroku", "DigitalOcean"],
        "DevOps": ["Docker", "Kubernetes", "Jenkins", "Git", "CI/CD", "Ansible", "Terraform", "Chef", "Puppet"],
        "Big Data": ["Hadoop", "Spark", "Hive", "Pig", "Kafka", "Flink"],
        "AI/ML": ["Machine Learning", "Deep Learning", "Natural Language Processing", "NLP", "Computer Vision", "Reinforcement Learning", "ML", "AI", "LLMs", "LoRA", "RLHF"],
        "Other Tools": ["Jira", "Confluence", "Slack", "Trello", "Asana", "REST APIs", "GraphQL"],
        "Soft Skills": ["Communication", "Teamwork", "Problem-solving", "Critical Thinking", "Time Management", "Leadership"],
        "Methodologies": ["Agile", "Scrum", "Kanban", "Waterfall"],
        "Operating Systems": ["Linux", "Windows", "macOS"],
    }
    all_keywords = []
    for category, keywords in skill_keywords.items():
        all_keywords.extend(keywords)
    pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in all_keywords) + r')\b'
    regex = re.compile(pattern, re.IGNORECASE)
    for match in regex.finditer(text):
        skills_set.add(match.group(0))
    return list(skills_set)

def main(category, remote=False, experience=None):
    """Scrapes job postings, handling detailed descriptions, skills, company URL, and role."""
    all_jobs = []
    url = generate_url(category, remote, experience)
    print(f"Scraping: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    job_list_container = soup.find('div', id='vacancyListId')

    if not job_list_container:
        print("Job list container not found.")
        return

    job_cards = job_list_container.find_all('li', class_='l-vacancy')

    if not job_cards:
        print("No job cards found on this page.")
        return

    for job_card in job_cards:
        job_data = extract_job_data(job_card)
        if job_data:
            detailed_description, skills, detail_salary, company_name, city, company_dou_url, role = extract_detailed_description_and_skills(job_data['url'])
            job_data['detailed_description'] = detailed_description
            job_data['skills'] = skills
            if detail_salary:
                job_data['salary'] = detail_salary
            if company_dou_url:
               job_data['company_dou_url'] = company_dou_url
            job_data['company'] = company_name
            job_data['title'] = role
            job_data['city'] = city
            all_jobs.append(job_data)
            time.sleep(2)

    if all_jobs:
        filename = f"{category}_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'company', 'company_dou_url', 'city', 'url', 'salary', 'detailed_description', 'skills', 'date_scraped']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_jobs)
        print(f"Successfully scraped {len(all_jobs)} job postings and saved to {filename}")
    else:
        print("No job data to write.")

def parse_rss_feed(rss_url):
    """Parses an RSS feed."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        job_listings = []
        for item in root.findall('.//item'):
            job_data = extract_rss_job_data(item)
            if job_data:
                job_listings.append(job_data)
        return job_listings

    except requests.exceptions.RequestException as e:
        print(f"Error fetching or parsing RSS feed: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

def generate_rss_url(category, remote=False, experience=None):
    """Generates an RSS feed URL for jobs.dou.ua with filters."""
    base_url = "https://jobs.dou.ua/vacancies/feeds/"
    url = f"{base_url}?"
    if experience:
        url += f"exp={experience}&"
    if remote:
        url += "remote&"
    url += f"category={category.replace(' ', '%20')}"
    return url

def rss_main(category, remote=False, experience=None):
    """Fetches, processes, and saves job listings from an RSS feed to CSV."""
    rss_url = generate_rss_url(category, remote, experience)
    print(f"Fetching RSS feed from: {rss_url}")

    job_listings = parse_rss_feed(rss_url)

    if not job_listings:
        print("No job listings found in the RSS feed.")
        return

    all_jobs = []
    for job_data in job_listings:
        detailed_description, skills, detail_salary, company_name, city, company_dou_url, role = extract_detailed_description_and_skills(job_data['url'])
        job_data['detailed_description'] = detailed_description
        job_data['skills'] = skills
        if detail_salary:
            job_data['salary'] = detail_salary
        if company_dou_url:
           job_data['company_dou_url'] = company_dou_url
        job_data['company'] = company_name
        job_data['title'] = role
        job_data['city'] = city
        all_jobs.append(job_data)
        time.sleep(2)

    if all_jobs:
        filename = f"rss_{category}_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'company', 'company_dou_url', 'city', 'url', 'salary', 'detailed_description', 'skills', 'date_scraped']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_jobs)
        print(f"Successfully scraped {len(all_jobs)} job postings from RSS and saved to {filename}")
    else:
        print("No job data to write.")

## Step 3: Run the Scraper

# Parameters Explanation:

# Category can be one of the following: ".NET", "Account Manager", "AI/ML", "Analyst", "Android", "Animator",
# "Architect", "Artist", "Assistant", "Big Data", "Blockchain", "C++", "C-level", "Copywriter", "Data Engineer",
# "Data Science", "DBA", "Design", "DevOps", "Embedded", "Engineering Manager", "Erlang", "ERP/CRM", "Finance",
# "Flutter", "Front End", "Golang", "Hardware", "HR", "iOS/macOS", "Java", "Legal", "Marketing", "Node.js",
# "Office Manager", "Other", "PHP", "Product Manager", "Project Manager", "Python", "QA", "React Native", "Ruby",
# "Rust", "Sales", "Salesforce", "SAP", "Scala", "Scrum Master", "Security", "SEO", "Support", "SysAdmin",
# "Technical Writer", "Unity", "Unreal Engine", "Військова справа".
#
# remote:  If True, searches for remote jobs.  If False or not specified, searches for all jobs (both remote and
#          on-site).  Boolean value (True or False).
#
# experience:  Experience level in years.  Can be: "0-1", "1-3", "3-5", "5plus".  If not specified, all experience
#              levels are included.  String value.
#
# rss_main vs. main:
#   rss_main:
#       Pros:  Often finds more vacancies and is generally faster.  Gets data from the RSS feed.
#       Cons:  Might include listings that are no longer actively displayed on the main website search results.
#   main:
#       Pros:  Scrapes directly from the website's search results pages, so you get exactly what you see on the site.
#       Cons:  Can be slower than rss_main and might find fewer vacancies (since it only scrapes the initially loaded results).
#

# Examples of Use:

# main("Analyst", remote=True, experience="0-1")  # Scrape remote Analyst jobs with 0-1 years of experience from the website.
# rss_main("Analyst", remote=True, experience="0-1") # Scrape remote Analyst jobs with 0-1 years of experience from the RSS feed.

# main("Військова справа", experience="5plus")  # Scrape all "Військова справа" jobs with 5+ years of experience from the website.
# rss_main("Військова справа", experience="5plus") # Scrape "Військова справа" jobs with 5+ years of experience from the RSS feed.

# main("Data Science", remote=True, experience="1-3") # Scrape remote Data Science jobs with 1-3 years of experience from the website.
# rss_main("Data Science", remote=True, experience="1-3") # Scrape remote Data Science jobs with 1-3 years of experience from the RSS feed.

# main("Python", remote=True, experience="0-1")  # Scrape remote Python jobs with 0-1 years of experience from the website.
# rss_main("Python", remote=True, experience="0-1") # Scrape remote Python jobs with 0-1 years of experience from the RSS feed.

main("Python", remote=True, experience="1-3")  # Scrape remote Python jobs with 1-3 years of experience from the website.
# rss_main("Python", remote=True, experience="1-3") # Scrape remote Python jobs with 1-3 years of experience from the RSS feed.
