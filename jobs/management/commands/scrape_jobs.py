from django.core.management.base import BaseCommand
from jobs.models import JobOffer
from jobs.scrapers.linkedin import LinkedInScraper
from jobs.scrapers.remoteok import RemoteOkScraper
from jobs.scrapers.rigzone import RigzoneScraper
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape jobs from various sources'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, default='all', help='Source to scrape: linkedin, remoteok, or all')
        parser.add_argument('--keywords', type=str, default='API 510', help='Keywords to search for (e.g., API 510, CWI, NDT)')
        parser.add_argument('--location', type=str, default='', help='Location to search for')
        parser.add_argument('--limit', type=int, default=10, help='Max jobs to scrape per source')
        parser.add_argument('--schedule', action='store_true', help='Schedule this command to run daily')

    def handle(self, *args, **options):
        if options['schedule']:
            from jobs.tasks import scrape_all_jobs_task
            keywords = options['keywords']
            limit = options['limit']
            # Schedule it to run now (and repeat if configured in task)
            scrape_all_jobs_task(keywords=keywords, limit=limit, repeat=24*60*60)
            self.stdout.write(self.style.SUCCESS(f"Scheduled scraping task for keywords='{keywords}' daily."))
            return

        source = options['source']
        keywords = options['keywords']
        location = options['location']
        limit = options['limit']

        scrapers = []
        if source == 'all' or source == 'linkedin':
            scrapers.append(LinkedInScraper())
        if source == 'all' or source == 'remoteok':
            scrapers.append(RemoteOkScraper())
        if source == 'all' or source == 'rigzone':
            scrapers.append(RigzoneScraper())

        total_new_jobs = 0

        for scraper in scrapers:
            scraper_name = scraper.__class__.__name__
            self.stdout.write(f"Scraping {scraper_name} for '{keywords}' in '{location}'...")
            
            try:
                jobs = scraper.search(keywords, location, limit)
                self.stdout.write(f"Found {len(jobs)} jobs from {scraper_name}.")

                for job_data in jobs:
                    # Avoid duplicates by URL and ensure title exists
                    url = job_data.get('url')
                    title = job_data.get('title')
                    if not url or not title:
                        self.stdout.write(self.style.WARNING(f"Skipping job due to missing data: Title='{title}', URL='{url}'"))
                        continue

                    # Handle valid posted_at date or default to today
                    posted_at = job_data.get('posted_at')
                    if posted_at:
                        try:
                            # Handle ISO format from RemoteOK
                            if isinstance(posted_at, str):
                                posted_at = datetime.fromisoformat(posted_at).date()
                        except ValueError:
                            posted_at = date.today()
                    else:
                        posted_at = date.today()
                    
                    # Convert salary string to fields (basic placeholder logic)
                    # Real implementation would need a parser
                    salary_str = job_data.get('salary', '')
                    
                    obj, created = JobOffer.objects.get_or_create(
                        url=url,
                        defaults={
                            'title': job_data.get('title'),
                            'company': job_data.get('company'),
                            'location': job_data.get('location'),
                            'description': job_data.get('description'),
                            'apply_link': job_data.get('apply_url'),
                            'source': job_data.get('source'),
                            'posted_at': posted_at,
                            'remote': job_data.get('remote', False),
                            'company_logo': job_data.get('company_logo'),
                            'salary_range': salary_str[:100] if salary_str else '',
                            'salary_min': job_data.get('salary_min'),
                            'salary_max': job_data.get('salary_max'),
                            'currency': job_data.get('salary_currency')
                        }
                    )
                    
                    if created:
                        total_new_jobs += 1
                        self.stdout.write(self.style.SUCCESS(f"Saved: {job_data.get('title')}"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error executing {scraper_name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Scraping completed. {total_new_jobs} new jobs added."))
