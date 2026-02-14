
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_linkedin_salary():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Search for a job that likely has salary info
        keywords = "python"
        location = "United States"
        url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={location}"
        
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        # Wait for job list
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
        )
        
        # Find first job card
        job_cards = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list > li")
        if job_cards:
            card = job_cards[0]
            logger.info("Found job card. Clicking...")
            
            # Scroll and click
            driver.execute_script("arguments[0].scrollIntoView();", card)
            time.sleep(1)
            
            link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
            # Use JS click to avoid interception
            driver.execute_script("arguments[0].click();", link_elem)
            
            logger.info("Clicked job. Waiting for details...")
            time.sleep(5) # Wait for details to load
            
            # Save page source
            with open("linkedin_details.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info("Saved linkedin_details.html")
            
            # Also save a screenshot just in case
            driver.save_screenshot("linkedin_details.png")
            logger.info("Saved linkedin_details.png")
            
        else:
            logger.warning("No job cards found.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_linkedin_salary()
