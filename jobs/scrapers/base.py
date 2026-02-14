from abc import ABC, abstractmethod
from typing import List, Dict

class JobScraper(ABC):
    @abstractmethod
    def search(self, keywords: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        Search for jobs and return a list of dictionaries with:
        - title
        - company
        - location
        - description
        - url
        - salary (optional)
        - posted_at (optional datetime)
        - remote (boolean)
        """
        pass
