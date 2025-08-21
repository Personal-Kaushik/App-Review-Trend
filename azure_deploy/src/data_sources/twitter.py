"""
Twitter data source implementation.
"""
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from src.data_sources.base import DataSource
from src.models.review import Review

# Try to import snscrape, fallback to disabled if not available
try:
    import snscrape.modules.twitter as sntwitter
    SNSCRAPE_AVAILABLE = True
except (ImportError, AttributeError) as e:
    SNSCRAPE_AVAILABLE = False
    print(f"Warning: snscrape not available: {e}")
    print("Twitter data source will be disabled")


class TwitterDataSource(DataSource):
    """Twitter data source."""
    
    def _get_source_name(self) -> str:
        return "twitter"
    
    def validate_config(self) -> bool:
        """Validate Twitter configuration."""
        if not SNSCRAPE_AVAILABLE:
            return False
        return True
    
    def get_supported_parameters(self) -> List[str]:
        """Get supported parameters for Twitter."""
        return ['days_back', 'include_retweets']
    
    def fetch_reviews(self, query: str, limit: int = 100, **kwargs) -> List[Review]:
        """
        Fetch reviews from Twitter.
        
        Args:
            query: Search query (e.g., '"Microsoft Family Safety" OR "Family Safety app"')
            limit: Maximum number of tweets to fetch
            **kwargs: Additional parameters (days_back, include_retweets)
            
        Returns:
            List of Review objects
        """
        if not SNSCRAPE_AVAILABLE:
            print("Warning: Twitter scraping is disabled due to snscrape compatibility issues")
            return []
            
        if not query:
            query = self.config.get('default_query', 'Microsoft Family Safety')
        
        days_back = kwargs.get('days_back', self.config.get('days_back', 120))
        include_retweets = kwargs.get('include_retweets', self.config.get('include_retweets', False))
        
        # Add date range to query
        today = datetime.now().date()
        start_date = today - timedelta(days=days_back)
        query_with_date = f'{query} since:{start_date} until:{today}'
        
        reviews_list = []
        seen_hashes = set()
        
        try:
            print(f"Searching tweets: {query_with_date}")
            
            for tweet in sntwitter.TwitterSearchScraper(query_with_date).get_items():
                if len(reviews_list) >= limit:
                    break
                
                # Skip retweets if not wanted
                if not include_retweets and tweet.content.startswith('RT @'):
                    continue
                
                # Deduplication
                content = tweet.content.strip()
                text_hash = hashlib.md5(content.encode()).hexdigest()
                if text_hash in seen_hashes:
                    continue
                seen_hashes.add(text_hash)
                
                review_id = hashlib.md5(f"twitter_{tweet.id}".encode()).hexdigest()
                
                review = Review(
                    id=review_id,
                    source=self.source_name,
                    text=content,
                    author=tweet.user.username,
                    date=tweet.date,
                    url=f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
                    metadata={
                        'tweet_id': tweet.id,
                        'retweet_count': tweet.retweetCount,
                        'like_count': tweet.likeCount,
                        'reply_count': tweet.replyCount,
                        'user_followers': tweet.user.followersCount,
                        'user_verified': tweet.user.verified
                    }
                )
                reviews_list.append(review)
            
            return self.preprocess_reviews(reviews_list)
            
        except Exception as e:
            print(f"Error fetching Twitter reviews: {e}")
            return []
    
    def preprocess_reviews(self, reviews: List[Review]) -> List[Review]:
        """Remove duplicate reviews and clean text."""
        seen_texts = set()
        unique_reviews = []
        
        for review in reviews:
            # Clean text (remove excessive whitespace, etc.)
            cleaned_text = ' '.join(review.text.split())
            review.text = cleaned_text
            
            text_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_reviews.append(review)
        
        return unique_reviews
