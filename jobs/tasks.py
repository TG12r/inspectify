from background_task import background
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@background(schedule=60*60*24) # Daily by default
def scrape_all_jobs_task(keywords='API 510', limit=10, source='all', location='', keywords_file=None):
    logger.info(f"Starting background job scrape: source={source}, keyword={keywords}, location={location}, limit={limit}")
    try:
        if keywords.upper() in ['TODAS', 'ALL']:
            # List of standard industry keywords
            default_keywords = ['API 510', 'API 570', 'API 653', 'CWI', 'NDT', 'Welding Inspector', 'QA/QC Inspector']
            logger.info(f"Scraping ALL keywords: {default_keywords}")
            for kw in default_keywords:
                call_command('scrape_jobs', source=source, keywords=kw, location=location, limit=limit)
        elif keywords_file:
             call_command('scrape_jobs', source=source, from_file=keywords_file, limit=limit)
        else:
             call_command('scrape_jobs', source=source, keywords=keywords, location=location, limit=limit)
             
        logger.info("Background job scrape completed.")
    except Exception as e:
        logger.error(f"Background job scrape failed: {e}")
