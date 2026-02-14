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

class RigzoneScraper(JobScraper):
    def search(self, keywords: str, location: str = "", limit: int = 10) -> List[Dict]:
        options = Options()
        options.add_argument("--headless=new") # Required for Docker/Server
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return []

        jobs = []
        try:
            # Rigzone Job Search URL
            # Example: https://www.rigzone.com/oil/jobs/search/?term=NDT
            url = f"https://www.rigzone.com/oil/jobs/search/?term={keywords}"
            if location:
                 url += f"&location={location}"
            
            logger.info(f"Navigating to {url}")
            driver.get(url)
            
            # Wait for job list
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article.update-block"))
                )
            except Exception as e:
                logger.warning(f"Timeout waiting for job cards: {e}")

            # Scroll to load more (Rigzone might use pagination or infinite scroll, let's assume pagination for now or just grab first page)
            # Rigzone uses standard pagination "Load More" or pages. Let's try to grab what's visible first.
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, "article.update-block")
            
            logger.info(f"Found {len(job_cards)} job cards on Rigzone.")

            for card in job_cards:
                if len(jobs) >= limit:
                    break
                
                try:
                    # Title
                    title_elem = card.find_element(By.CSS_SELECTOR, "div.heading h3 a")
                    job_url = title_elem.get_attribute('href')
                    title = title_elem.text.strip()

                    # Address contains Company + Location separated by <br> or newlines
                    # Structure: <address> Company <br> Location </address>
                    address_elem = card.find_element(By.CSS_SELECTOR, "address")
                    address_text = address_elem.text.strip()
                    # Split by newline if possible, otherwise just use the whole text
                    parts = address_text.split('\n')
                    company = parts[0].strip() if parts else "Rigzone"
                    location = parts[-1].strip() if len(parts) > 1 else ""

                    # Description
                    description = ""
                    try:
                        desc_elem = card.find_element(By.CSS_SELECTOR, "div.description div.text")
                        description = desc_elem.text.strip()
                    except:
                        pass
                    
                    # Date
                    posted_at = datetime.today().date()
                    try:
                        time_elem = card.find_element(By.CSS_SELECTOR, "footer.details time")
                        # Format: "Posted: February 12, 2026"
                        date_text = time_elem.text.replace("Posted:", "").strip()
                        # Parse date if needed, or just keep as today for now
                    except:
                         pass

                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': job_url,
                        'apply_url': job_url, 
                        'description': description,
                        'source': 'Rigzone',
                        'remote': 'remote' in location.lower(),
                        'posted_at': posted_at
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Rigzone job card: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping Rigzone: {e}")
            try:
                driver.save_screenshot("rigzone_error.png")
                with open("rigzone_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.info("Saved screenshot and source.")
            except:
                pass
        finally:
            driver.quit()

        return jobs
