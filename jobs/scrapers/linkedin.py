import time
import logging
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from .base import JobScraper

logger = logging.getLogger(__name__)

class LinkedInScraper(JobScraper):
    def search(self, keywords: str, location: str = "", limit: int = 10) -> List[Dict]:
        options = Options()
        options.add_argument("--headless=new") # Required for Docker/Server
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        # Rotate user agent to avoid bot detection
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return []

        jobs = []
        try:
            # LinkedIn Guest Job Search URL
            url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={location}"
            driver.get(url)
            
            # Wait for job list to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
            )

            # Scroll to load more jobs if needed
            last_height = driver.execute_script("return document.body.scrollHeight")
            while len(jobs) < limit:
                job_cards = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list > li")
                
                # Check for new jobs
                if len(job_cards) > len(jobs):
                    new_jobs_batch = job_cards[len(jobs):]
                    for card in new_jobs_batch:
                        if len(jobs) >= limit:
                            break
                        
                        try:
                            # Scroll to card to make it clickable
                            driver.execute_script("arguments[0].scrollIntoView();", card)
                            time.sleep(0.5)
                            
                            # Extract basic info first
                            title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
                            company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
                            location_elem = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
                            link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                            
                            # Store text immediately to avoid stale element later
                            title_text = title_elem.text.strip()
                            company_text = company_elem.text.strip()
                            location_text = location_elem.text.strip()
                            job_url = link_elem.get_attribute('href')
                            remote_bool = 'remote' in location_text.lower() or 'remoto' in location_text.lower()

                            # Click to load details
                            description = "Ver detalle en LinkedIn (Descripción no accesible en vista rápida)"
                            try:
                                link_elem.click()
                                time.sleep(2) # Wait for details to load
                                
                                # Try to find description in the details pane
                                try:
                                    description_elem = driver.find_element(By.CSS_SELECTOR, "div.show-more-less-html__markup")
                                    description = description_elem.get_attribute("innerHTML").strip()
                                except:
                                    try:
                                        description_elem = driver.find_element(By.CSS_SELECTOR, "div.description__text")
                                        description = description_elem.text.strip()
                                    except:
                                        pass
                            except:
                                pass

                            # Try to find JSON-LD for salary
                            salary_min = None
                            salary_max = None
                            salary_currency = None
                            
                            try:
                                import json
                                json_ld_elem = driver.find_element(By.XPATH, "//script[@type='application/ld+json']")
                                json_ld_text = json_ld_elem.get_attribute("innerHTML")
                                job_data = json.loads(json_ld_text)
                                
                                base_salary = job_data.get('baseSalary', {})
                                if base_salary:
                                    value = base_salary.get('value', {})
                                    salary_min = value.get('minValue')
                                    salary_max = value.get('maxValue')
                                    salary_currency = base_salary.get('currency')
                            except Exception as e:
                                # logger.warning(f"Could not extract JSON-LD salary: {e}")
                                pass

                            jobs.append({
                                'title': title_text,
                                'company': company_text,
                                'location': location_text,
                                'url': job_url,
                                'apply_url': job_url,
                                'description': description, 
                                'source': 'LinkedIn',
                                'remote': remote_bool,
                                'posted_at': datetime.today().date(),
                                'salary_min': salary_min,
                                'salary_max': salary_max,
                                'salary_currency': salary_currency
                            })
                        except Exception as e:
                            logger.warning(f"Error parsing job card: {e}")
                            continue

                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        finally:
            driver.quit()

        return jobs
