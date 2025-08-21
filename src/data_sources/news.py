"""
News data source implementation using web scraping.
"""
import hashlib
import ssl
import certifi
from newspaper import Article
from googlesearch import search
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

from src.data_sources.base import DataSource
from src.models.review import Review


class NewsDataSource(DataSource):
    """News data source using web scraping."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Set up SSL context for news scraping
        ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())
    
    def _get_source_name(self) -> str:
        return "news"
    
    def validate_config(self) -> bool:
        """Validate News configuration."""
        return True  # News scraping doesn't require specific config
    
    def get_supported_parameters(self) -> List[str]:
        """Get supported parameters for News."""
        return ['days_back', 'search_results']
    
    def fetch_reviews(self, query: str, limit: int = 100, **kwargs) -> List[Review]:
        """
        Fetch reviews from news articles.
        
        Args:
            query: Search query (e.g., "Microsoft Family Safety issue OR complaint")
            limit: Maximum number of articles to fetch
            **kwargs: Additional parameters (days_back, search_results)
            
        Returns:
            List of Review objects
        """
        if not query:
            query = self.config.get('default_query', 'Microsoft Family Safety issue OR complaint OR review')
        
        days_back = kwargs.get('days_back', self.config.get('days_back', 120))
        search_results = kwargs.get('search_results', self.config.get('search_results', 200))
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        reviews_list = []
        seen_hashes = set()
        
        try:
            print(f"Searching news articles: {query}")
            
            for url in search(query, num_results=search_results):
                if len(reviews_list) >= limit:
                    break
                
                try:
                    article = Article(url)
                    article.download()
                    article.parse()
                    
                    # Check article date if available
                    if article.publish_date and article.publish_date < cutoff_date:
                        continue
                    
                    # Skip if article text is too short
                    if len(article.text) < 100:
                        continue
                    
                    # Deduplication
                    text_hash = hashlib.md5(article.text.encode()).hexdigest()
                    if text_hash in seen_hashes:
                        continue
                    seen_hashes.add(text_hash)
                    
                    review_id = hashlib.md5(f"news_{url}".encode()).hexdigest()
                    
                    # Truncate text for manageable size
                    text_content = article.text[:1000] + "..." if len(article.text) > 1000 else article.text
                    
                    review = Review(
                        id=review_id,
                        source=self.source_name,
                        text=text_content,
                        title=article.title,
                        date=article.publish_date,
                        url=url,
                        metadata={
                            'authors': article.authors,
                            'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                            'full_text_length': len(article.text)
                        }
                    )
                    reviews_list.append(review)
                    
                except Exception as e:
                    # Skip articles that can't be parsed
                    continue
                
                # Be gentle to servers
                time.sleep(0.2)
            
            return self.preprocess_reviews(reviews_list)
            
        except Exception as e:
            print(f"Error fetching news articles: {e}")
            return []
    
    def preprocess_reviews(self, reviews: List[Review]) -> List[Review]:
        """Remove duplicate reviews and clean text."""
        seen_texts = set()
        unique_reviews = []
        
        for review in reviews:
            # Clean text
            if review.text:
                cleaned_text = ' '.join(review.text.split())
                review.text = cleaned_text
            
            text_hash = hashlib.md5(review.text.encode()).hexdigest()
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_reviews.append(review)
        
        return unique_reviews
