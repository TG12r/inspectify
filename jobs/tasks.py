from background_task import background
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@background(schedule=60*60*24) # Daily by default
def scrape_all_jobs_task(keywords='API 510', limit=10, keywords_file=None):
    logger.info(f"Starting background job scrape: keyword={keywords}, keywords_file={keywords_file}, limit={limit}")
    try:
        # If a file is provided, use it. Otherwise use the single keyword.
        if keywords_file:
             call_command('scrape_jobs', source='all', from_file=keywords_file, limit=limit)
        else:
             call_command('scrape_jobs', source='all', keywords=keywords, limit=limit)
             
        logger.info("Background job scrape completed.")
    except Exception as e:
        logger.error(f"Background job scrape failed: {e}")
