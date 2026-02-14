import requests
import logging
from typing import List, Dict
from .base import JobScraper

logger = logging.getLogger(__name__)

class RemoteOkScraper(JobScraper):
    def search(self, keywords: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        RemoteOK API is public but doesn't support complex filtering perfectly via URL params in a standard way.
        It returns a JSON list. We'll filter client-side.
        """
        url = "https://remoteok.com/api"
        headers = {'User-Agent': 'Inspectify-Job-Board'} # Required by RemoteOK

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Error fetching from RemoteOK: {e}")
            return []

        jobs = []
        # First item in RemoteOK API is usually legal text, skip it if it doesn't have 'id'
        for item in data:
            if 'id' not in item:
                continue
            
            # Keyword filter (simple case-insensitive containment)
            tags = item.get('tags', [])
            tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)
            text_to_search = (item.get('position', '') + " " + item.get('description', '') + " " + tags_str).lower()
            if keywords.lower() not in text_to_search:
                continue

            # Location filter (RemoteOK is mostly remote, but sometimes has restrictions)
            if location and location.lower() not in item.get('location', '').lower():
                continue

            jobs.append({
                'title': item.get('position'),
                'company': item.get('company'),
                'location': item.get('location', 'Remote'),
                'description': item.get('description'), # Contains HTML
                'url': item.get('url'),
                'apply_url': item.get('apply_url'),
                'salary': f"{item.get('salary_min', '')} - {item.get('salary_max', '')} {item.get('salary_currency', '')}".strip() if item.get('salary_min') else "",
                'posted_at': item.get('date'), # ISO timestamp
                'source': 'RemoteOK',
                'tags': item.get('tags', []),
                'company_logo': item.get('company_logo'),
                'remote': True
            })

            if len(jobs) >= limit:
                break
        
        return jobs
