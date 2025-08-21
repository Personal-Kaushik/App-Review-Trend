"""
Apple App Store data source implementation.
"""
import hashlib
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.data_sources.base import DataSource
from src.models.review import Review


class AppStoreDataSource(DataSource):
    """App Store review data source."""
    
    def _get_source_name(self) -> str:
        return "appstore"
    
    def validate_config(self) -> bool:
        """Validate App Store configuration."""
        required_fields = ['app_id']
        return all(field in self.config for field in required_fields)
    
    def get_supported_parameters(self) -> List[str]:
        """Get supported parameters for App Store."""
        return ['app_id', 'countries']
    
    def fetch_reviews(self, query: str, limit: int = 100, **kwargs) -> List[Review]:
        """
        Fetch reviews from Apple App Store.
        
        Args:
            query: App ID (e.g., '1519844643')
            limit: Maximum number of reviews to fetch
            **kwargs: Additional parameters (countries)
            
        Returns:
            List of Review objects
        """
        app_id = query if query else self.config.get('app_id')
        if not app_id:
            raise ValueError("App ID is required for App Store reviews")
        
        countries = kwargs.get('countries', self.config.get('countries', ['us', 'in', 'gb', 'ca', 'au']))
        
        all_reviews = []
        
        for country in countries:
            try:
                reviews_data = self._fetch_country_reviews(app_id, country, limit)
                all_reviews.extend(reviews_data)
                
                if len(all_reviews) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error fetching App Store reviews for {country}: {e}")
                continue
        
        return self.preprocess_reviews(all_reviews[:limit])
    
    def _fetch_country_reviews(self, app_id: str, country: str, max_reviews: int) -> List[Review]:
        """Fetch reviews from a specific country's App Store."""
        reviews_list = []
        page = 1
        
        while len(reviews_list) < max_reviews:
            url = f'https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json'
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    break
                
                data = response.json()
                entries = data.get('feed', {}).get('entry', [])[1:]  # Skip metadata
                
                if not entries:
                    break
                
                for entry in entries:
                    review_id = hashlib.md5(f"{app_id}_{entry['content']['label']}".encode()).hexdigest()
                    
                    # Parse date
                    date_str = entry['updated']['label']
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S-07:00')
                    except:
                        date = None
                    
                    review = Review(
                        id=review_id,
                        source=self.source_name,
                        text=entry['content']['label'],
                        title=entry['title']['label'],
                        author=entry['author']['name']['label'],
                        rating=float(entry['im:rating']['label']),
                        date=date,
                        metadata={
                            'app_id': app_id,
                            'country': country,
                            'version': entry.get('im:version', {}).get('label')
                        }
                    )
                    reviews_list.append(review)
                    
                    if len(reviews_list) >= max_reviews:
                        break
                
                page += 1
                
            except Exception as e:
                print(f"Error fetching page {page} for {country}: {e}")
                break
        
        return reviews_list
    
    def preprocess_reviews(self, reviews: List[Review]) -> List[Review]:
        """Remove duplicate reviews based on text content."""
        seen_texts = set()
        unique_reviews = []
        
        for review in reviews:
            text_hash = hashlib.md5(review.text.encode()).hexdigest()
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_reviews.append(review)
        
        return unique_reviews
