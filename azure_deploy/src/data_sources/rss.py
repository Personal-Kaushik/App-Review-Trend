"""
RSS data source implementation.
"""
import hashlib
import feedparser
import requests
import certifi
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from src.data_sources.base import DataSource
from src.models.review import Review


class RSSDataSource(DataSource):
    """RSS data source."""
    
    def _get_source_name(self) -> str:
        return "rss"
    
    def validate_config(self) -> bool:
        """Validate RSS configuration."""
        return True  # RSS doesn't require specific config
    
    def get_supported_parameters(self) -> List[str]:
        """Get supported parameters for RSS."""
        return ['feed_urls', 'days_back']
    
    def fetch_reviews(self, query: str, limit: int = 100, **kwargs) -> List[Review]:
        """
        Fetch reviews from RSS feeds.
        
        Args:
            query: Search query (used to generate Google News RSS URL if feed_urls not provided)
            limit: Maximum number of articles to fetch
            **kwargs: Additional parameters (feed_urls, days_back)
            
        Returns:
            List of Review objects
        """
        feed_urls = kwargs.get('feed_urls', self.config.get('feed_urls'))
        
        if not feed_urls:
            # Generate Google News RSS URL from query
            if query:
                encoded_query = query.replace(' ', '+').replace('"', '%22')
                feed_urls = [f'https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en']
            else:
                feed_urls = [
                    'https://news.google.com/rss/search?q="Microsoft+Family+Safety"&hl=en-IN&gl=IN&ceid=IN:en'
                ]
        
        days_back = kwargs.get('days_back', self.config.get('days_back', 120))
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        reviews_list = []
        seen_hashes = set()
        
        for url in feed_urls:
            try:
                articles = self._fetch_feed_articles(url, cutoff_date)
                
                for article in articles:
                    # Deduplication
                    combined_text = f"{article['title']} {article['text']}"
                    text_hash = hashlib.md5(combined_text.encode()).hexdigest()
                    if text_hash in seen_hashes:
                        continue
                    seen_hashes.add(text_hash)
                    
                    review_id = hashlib.md5(f"rss_{article['url']}".encode()).hexdigest()
                    
                    review = Review(
                        id=review_id,
                        source=self.source_name,
                        text=article['text'],
                        title=article['title'],
                        date=article.get('date'),
                        url=article['url'],
                        metadata={
                            'feed_url': url,
                            'published': article.get('published_raw')
                        }
                    )
                    reviews_list.append(review)
                    
                    if len(reviews_list) >= limit:
                        break
                        
                if len(reviews_list) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error fetching RSS feed {url}: {e}")
                continue
        
        return self.preprocess_reviews(reviews_list)
    
    def _fetch_feed_articles(self, url: str, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Fetch articles from a single RSS feed."""
        try:
            response = requests.get(url, verify=certifi.where(), timeout=10)
            feed = feedparser.parse(response.content)
            
            articles = []
            for entry in feed.entries:
                # Parse date
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    try:
                        pub_date = datetime.fromtimestamp(time.mktime(published))
                        if pub_date < cutoff_date:
                            continue
                    except:
                        pub_date = None
                else:
                    pub_date = None
                
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")
                
                articles.append({
                    'title': title,
                    'text': summary,
                    'url': link,
                    'date': pub_date,
                    'published_raw': entry.get("published", "")
                })
            
            return articles
            
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
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
            
            combined_text = f"{review.title or ''} {review.text or ''}"
            text_hash = hashlib.md5(combined_text.encode()).hexdigest()
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_reviews.append(review)
        
        return unique_reviews
