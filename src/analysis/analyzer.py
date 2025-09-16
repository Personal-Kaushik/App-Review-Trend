"""
Main analyzer module that combines sentiment analysis and categorization.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.review import Review
from src.analysis.sentiment import SentimentAnalyzer
from src.analysis.categorization import ReviewCategorizer
from src.analysis.trend_analysis import TrendAnalyzer


class ReviewAnalyzer:
    """Main analyzer class that combines all analysis functionality with AI support."""
    
    def __init__(self, 
                 sentiment_threshold: float = -0.05,
                 categories: Optional[Dict[str, Any]] = None,
                 product_name: str = "Unknown Product"):
        """
        Initialize the analyzer with AI categorization support.
        
        Args:
            sentiment_threshold: Threshold for negative sentiment classification
            categories: Custom categories for classification (AI format or legacy keywords)
            product_name: Name of the product for AI categorization
        """
        self.sentiment_analyzer = SentimentAnalyzer(sentiment_threshold)
        self.categorizer = ReviewCategorizer(categories, product_name)
        self.trend_analyzer = TrendAnalyzer()
        self.product_name = product_name
    
    def analyze_reviews(self, reviews: List[Review]) -> List[Review]:
        """
        Perform complete analysis on reviews with AI categorization.
        
        Args:
            reviews: List of Review objects
            
        Returns:
            List of analyzed Review objects
        """
        if not reviews:
            return reviews
        
        print(f"🔍 Starting analysis of {len(reviews)} reviews for {self.product_name}")
        
        # Perform sentiment analysis
        print("📊 Analyzing sentiment...")
        reviews = self.sentiment_analyzer.analyze_reviews(reviews)
        
        # Get categorization status
        status = self.categorizer.get_ai_categorization_status()
        print(f"🤖 Categorization: {status['categorizer_type']}")
        
        # Perform categorization on all reviews (not just negative ones)
        print("🏷️ Categorizing reviews...")
        reviews = self.categorizer.categorize_reviews(reviews, filter_sentiment=None)
        
        print("✅ Analysis complete!")
        return reviews
    
    def get_analysis_summary(self, reviews: List[Review]) -> Dict[str, Any]:
        """
        Get comprehensive summary of analysis results with AI metrics.
        
        Args:
            reviews: List of analyzed Review objects
            
        Returns:
            Dictionary with detailed analysis summary
        """
        total_reviews = len(reviews)
        
        # Sentiment distribution
        sentiment_dist = self.sentiment_analyzer.get_sentiment_distribution(reviews)
        
        # Enhanced category distribution with AI metrics
        category_dist = self.categorizer.get_category_distribution(reviews, filter_sentiment='Negative')
        all_category_dist = self.categorizer.get_category_distribution(reviews, filter_sentiment=None)
        
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
        
        # AI categorization metrics
        ai_status = self.categorizer.get_ai_categorization_status()
        
        return {
            'total_reviews': total_reviews,
            'product_name': self.product_name,
            'sentiment_distribution': sentiment_dist,
            'category_distribution_negative': category_dist,
            'category_distribution_all': all_category_dist,
            'source_distribution': source_dist,
            'date_range': date_range,
            'negative_review_percentage': (sentiment_dist.get('Negative', 0) / total_reviews * 100) if total_reviews > 0 else 0,
            'ai_categorization_status': ai_status
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
                'category': review.category,
                'category_confidence': getattr(review, 'category_confidence', None),
                'categorization_method': getattr(review, 'categorization_method', None)
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
        
        # Extract category counts from the enhanced distribution format
        category_counts = category_dist.get('category_counts', {})
        
        # Sort by count and get top N
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        issues = []
        for category, count in sorted_categories:
            # Get sample reviews for this category
            sample_reviews = [r for r in negative_reviews if r.category == category][:3]
            
            # Get average confidence if available
            avg_confidence = category_dist.get('category_avg_confidence', {}).get(category, 0.5)
            categorization_methods = category_dist.get('category_methods', {}).get(category, {})
            
            issues.append({
                'category': category,
                'count': count,
                'percentage': (count / len(negative_reviews) * 100) if negative_reviews else 0,
                'avg_confidence': avg_confidence,
                'categorization_methods': categorization_methods,
                'sample_reviews': [
                    {
                        'text': r.text[:200] + '...' if len(r.text) > 200 else r.text,
                        'source': r.source,
                        'date': r.date.isoformat() if r.date else None
                    } for r in sample_reviews
                ]
            })
        
        return issues
    
    def analyze_monthly_trends(self, reviews: List[Review], 
                             months_back: int = 12,
                             negative_threshold: float = 3.0) -> Dict[str, Any]:
        """
        Analyze monthly trends of negative reviews by feature.
        
        Args:
            reviews: List of Review objects
            months_back: Number of months to look back
            negative_threshold: Rating threshold for negative reviews
            
        Returns:
            Dictionary with trend analysis results
        """
        # Get monthly trends DataFrame
        trend_df = self.trend_analyzer.get_monthly_negative_trends(
            reviews, months_back, negative_threshold
        )
        
        # Calculate improvement trends
        feature_trends = self.trend_analyzer.calculate_feature_improvement_trends(trend_df)
        
        return {
            'monthly_data': trend_df,
            'feature_trends': feature_trends,
            'analysis_period': f"{months_back} months",
            'negative_threshold': negative_threshold
        }
    
    def export_trend_analysis(self, trend_results: Dict[str, Any], 
                             output_dir: str = 'output',
                             generate_visualizations: bool = True,
                             open_in_browser: bool = True) -> None:
        """
        Export trend analysis results.
        
        Args:
            trend_results: Results from analyze_monthly_trends
            output_dir: Output directory
            generate_visualizations: Whether to generate visualization plots
            open_in_browser: Whether to open HTML dashboard in browser
        """
        self.trend_analyzer.export_trend_analysis(
            trend_results['monthly_data'],
            trend_results['feature_trends'],
            output_dir,
            generate_visualizations,
            open_in_browser
        )
    
    def print_trend_summary(self, trend_results: Dict[str, Any]) -> None:
        """
        Print trend analysis summary.
        
        Args:
            trend_results: Results from analyze_monthly_trends
        """
        self.trend_analyzer.print_trend_summary(trend_results['feature_trends'])
    
    def get_feature_detailed_trends(self, trend_results: Dict[str, Any], 
                                   feature_name: str) -> Dict[str, Any]:
        """
        Get detailed trend analysis for a specific feature.
        
        Args:
            trend_results: Results from analyze_monthly_trends
            feature_name: Name of the feature to analyze
            
        Returns:
            Detailed trend data for the feature
        """
        return self.trend_analyzer.get_feature_monthly_comparison(
            trend_results['monthly_data'],
            feature_name
        )
