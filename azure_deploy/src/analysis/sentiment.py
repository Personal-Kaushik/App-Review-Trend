"""
Sentiment analysis module.
"""
from textblob import TextBlob
from typing import List, Dict, Any
from src.models.review import Review


class SentimentAnalyzer:
    """Sentiment analyzer using TextBlob."""
    
    def __init__(self, negative_threshold: float = -0.05):
        """
        Initialize sentiment analyzer.
        
        Args:
            negative_threshold: Threshold below which sentiment is considered negative
        """
        self.negative_threshold = negative_threshold
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity < self.negative_threshold:
            sentiment = 'Negative'
        elif polarity > 0.1:
            sentiment = 'Positive'
        else:
            sentiment = 'Neutral'
        
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'confidence': abs(polarity)
        }
    
    def analyze_reviews(self, reviews: List[Review]) -> List[Review]:
        """
        Analyze sentiment for a list of reviews.
        
        Args:
            reviews: List of Review objects
            
        Returns:
            List of Review objects with sentiment analysis
        """
        for review in reviews:
            sentiment_result = self.analyze_sentiment(review.text)
            review.sentiment = sentiment_result['sentiment']
            
            # Add sentiment details to metadata
            if not review.metadata:
                review.metadata = {}
            
            review.metadata.update({
                'sentiment_polarity': sentiment_result['polarity'],
                'sentiment_subjectivity': sentiment_result['subjectivity'],
                'sentiment_confidence': sentiment_result['confidence']
            })
        
        return reviews
    
    def get_sentiment_distribution(self, reviews: List[Review]) -> Dict[str, int]:
        """
        Get distribution of sentiments across reviews.
        
        Args:
            reviews: List of Review objects
            
        Returns:
            Dictionary with sentiment counts
        """
        distribution = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
        
        for review in reviews:
            if review.sentiment in distribution:
                distribution[review.sentiment] += 1
        
        return distribution
