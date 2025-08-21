"""
Main analyzer module that combines sentiment analysis and categorization.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.review import Review
from src.analysis.sentiment import SentimentAnalyzer
from src.analysis.categorization import ReviewCategorizer


class ReviewAnalyzer:
    """Main analyzer class that combines all analysis functionality."""
    
    def __init__(self, 
                 sentiment_threshold: float = -0.05,
                 categories: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the analyzer.
        
        Args:
            sentiment_threshold: Threshold for negative sentiment classification
            categories: Custom categories for classification
        """
        self.sentiment_analyzer = SentimentAnalyzer(sentiment_threshold)
        self.categorizer = ReviewCategorizer(categories)
    
    def analyze_reviews(self, reviews: List[Review]) -> List[Review]:
        """
        Perform complete analysis on reviews.
        
        Args:
            reviews: List of Review objects
            
        Returns:
            List of analyzed Review objects
        """
        # Perform sentiment analysis
        reviews = self.sentiment_analyzer.analyze_reviews(reviews)
        
        # Perform categorization (only for negative reviews by default)
        reviews = self.categorizer.categorize_reviews(reviews, filter_sentiment='Negative')
        
        return reviews
    
    def get_analysis_summary(self, reviews: List[Review]) -> Dict[str, Any]:
        """
        Get summary of analysis results.
        
        Args:
            reviews: List of analyzed Review objects
            
        Returns:
            Dictionary with analysis summary
        """
        total_reviews = len(reviews)
        
        # Sentiment distribution
        sentiment_dist = self.sentiment_analyzer.get_sentiment_distribution(reviews)
        
        # Category distribution (for negative reviews)
        category_dist = self.categorizer.get_category_distribution(reviews, filter_sentiment='Negative')
        
        # Source distribution
        source_dist = {}
        for review in reviews:
            source_dist[review.source] = source_dist.get(review.source, 0) + 1
        
        # Date range
        dates = [review.date for review in reviews if review.date]
        date_range = {
            'earliest': min(dates).isoformat() if dates else None,
            'latest': max(dates).isoformat() if dates else None,
            'total_days': (max(dates) - min(dates)).days if len(dates) > 1 else 0
        }
        
        return {
            'total_reviews': total_reviews,
            'sentiment_distribution': sentiment_dist,
            'category_distribution': category_dist,
            'source_distribution': source_dist,
            'date_range': date_range,
            'negative_review_percentage': (sentiment_dist.get('Negative', 0) / total_reviews * 100) if total_reviews > 0 else 0
        }
    
    def export_to_dataframe(self, reviews: List[Review]) -> pd.DataFrame:
        """
        Export reviews to pandas DataFrame.
        
        Args:
            reviews: List of Review objects
            
        Returns:
            pandas DataFrame with review data
        """
        data = []
        
        for review in reviews:
            row = {
                'id': review.id,
                'source': review.source,
                'text': review.text,
                'title': review.title,
                'author': review.author,
                'rating': review.rating,
                'date': review.date.isoformat() if review.date else None,
                'url': review.url,
                'sentiment': review.sentiment,
                'category': review.category
            }
            
            # Add metadata as separate columns
            if review.metadata:
                for key, value in review.metadata.items():
                    row[f'metadata_{key}'] = value
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def export_to_csv(self, reviews: List[Review], filename: str) -> None:
        """
        Export reviews to CSV file.
        
        Args:
            reviews: List of Review objects
            filename: Output filename
        """
        df = self.export_to_dataframe(reviews)
        df.to_csv(filename, index=False)
        print(f"Reviews exported to {filename}")
    
    def filter_reviews(self, 
                      reviews: List[Review], 
                      sentiment: Optional[str] = None,
                      category: Optional[str] = None,
                      source: Optional[str] = None,
                      date_from: Optional[datetime] = None,
                      date_to: Optional[datetime] = None) -> List[Review]:
        """
        Filter reviews based on criteria.
        
        Args:
            reviews: List of Review objects
            sentiment: Filter by sentiment
            category: Filter by category
            source: Filter by source
            date_from: Filter by date from
            date_to: Filter by date to
            
        Returns:
            Filtered list of Review objects
        """
        filtered = reviews
        
        if sentiment:
            filtered = [r for r in filtered if r.sentiment == sentiment]
        
        if category:
            filtered = [r for r in filtered if r.category == category]
        
        if source:
            filtered = [r for r in filtered if r.source == source]
        
        if date_from:
            filtered = [r for r in filtered if r.date and r.date >= date_from]
        
        if date_to:
            filtered = [r for r in filtered if r.date and r.date <= date_to]
        
        return filtered
    
    def get_top_issues(self, reviews: List[Review], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top issues (categories) from negative reviews.
        
        Args:
            reviews: List of Review objects
            top_n: Number of top issues to return
            
        Returns:
            List of dictionaries with issue information
        """
        negative_reviews = [r for r in reviews if r.sentiment == 'Negative']
        category_dist = self.categorizer.get_category_distribution(negative_reviews)
        
        # Sort by count and get top N
        sorted_categories = sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        issues = []
        for category, count in sorted_categories:
            # Get sample reviews for this category
            sample_reviews = [r for r in negative_reviews if r.category == category][:3]
            
            issues.append({
                'category': category,
                'count': count,
                'percentage': (count / len(negative_reviews) * 100) if negative_reviews else 0,
                'sample_reviews': [
                    {
                        'text': r.text[:200] + '...' if len(r.text) > 200 else r.text,
                        'source': r.source,
                        'date': r.date.isoformat() if r.date else None
                    } for r in sample_reviews
                ]
            })
        
        return issues
