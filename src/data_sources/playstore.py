"""
Google Play Store data source implementation.
"""
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from google_play_scraper import reviews, Sort

from src.data_sources.base import DataSource
from src.models.review import Review


class PlayStoreDataSource(DataSource):
    """Play Store review data source."""
    
    def _get_source_name(self) -> str:
        return "playstore"
    
    def validate_config(self) -> bool:
        """Validate Play Store configuration."""
        required_fields = ['app_id']
        return all(field in self.config for field in required_fields)
    
    def get_supported_parameters(self) -> List[str]:
        """Get supported parameters for Play Store."""
        return ['app_id', 'lang', 'country', 'sort', 'count']
    
    def fetch_reviews(self, query: str, limit: int = 2000, **kwargs) -> List[Review]:
        """
        Fetch reviews from Google Play Store for the last 6 months.
        
        Args:
            query: App ID (e.g., 'com.microsoft.familysafety')
            limit: Maximum number of reviews to fetch (will fetch until 6 months back)
            **kwargs: Additional parameters (lang, country, sort)
            
        Returns:
            List of Review objects from last 6 months
        """
        from datetime import datetime, timedelta
        
        app_id = query if query else self.config.get('app_id')
        if not app_id:
            raise ValueError("App ID is required for Play Store reviews")
        
        # Calculate 6 months ago
        six_months_ago = datetime.now() - timedelta(days=180)
        
        # Set default parameters - fetch more to ensure we get 6 months of data
        params = {
            'lang': kwargs.get('lang', self.config.get('lang', 'en')),
            'country': kwargs.get('country', self.config.get('country', 'us')),
            'sort': kwargs.get('sort', Sort.NEWEST),
            'count': min(limit, 2000)  # Increased to get more data
        }
        
        try:
            # Fetch reviews from Play Store
            review_data, _ = reviews(app_id, **params)
            
            # Convert to Review objects and filter by date
            reviews_list = []
            for item in review_data:
                review_date = item.get('at')
                
                # Filter reviews to last 6 months only
                if review_date and review_date >= six_months_ago:
                    review_id = hashlib.md5(f"{app_id}_{item['content']}".encode()).hexdigest()
                    
                    review = Review(
                        id=review_id,
                        source=self.source_name,
                        text=item['content'],
                        author=item.get('userName'),
                        rating=float(item.get('score', 0)),
                        date=review_date,
                        metadata={
                            'app_id': app_id,
                            'thumbs_up': item.get('thumbsUpCount', 0),
                            'review_id': item.get('reviewId'),
                            'version': item.get('appVersion')
                        }
                    )
                    reviews_list.append(review)
            
            print(f"Filtered to {len(reviews_list)} reviews from last 6 months")
            return self.preprocess_reviews(reviews_list)
            
        except Exception as e:
            print(f"Error fetching Play Store reviews: {e}")
            return []
    
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
