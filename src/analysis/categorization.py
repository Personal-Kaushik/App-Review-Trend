"""
Review categorization module with AI support.
"""
import os
from typing import List, Dict, Any, Optional
from src.models.review import Review

# Try to import AI categorization, fall back if not available
try:
    from src.analysis.ai_categorization import create_categorizer_from_config, AICategorizer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    create_categorizer_from_config = None
    AICategorizer = None

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass


class ReviewCategorizer:
    """Advanced review categorizer with AI and keyword-based fallback."""
    
    def __init__(self, categories: Dict[str, Any] = None, product_name: str = "Unknown Product"):
        """
        Initialize categorizer.
        
        Args:
            categories: Dictionary mapping category names to definitions (AI format) or keyword lists (legacy)
            product_name: Name of the product for AI categorization
        """
        self.product_name = product_name
        self.categories = categories or self._get_default_categories()
        self.ai_categorizer = None
        self.use_ai = False
        
        # Initialize AI categorizer if available and configured
        if AI_AVAILABLE and self._should_use_ai():
            try:
                self.ai_categorizer = create_categorizer_from_config(product_name, self.categories)
                self.use_ai = True
                print(f"✓ AI categorization enabled for {product_name}")
            except Exception as e:
                print(f"⚠ AI categorization failed to initialize: {e}")
                print("  Falling back to keyword-based categorization")
        else:
            print(f"ℹ Using keyword-based categorization for {product_name}")
    
    def _should_use_ai(self) -> bool:
        """Check if AI categorization should be used."""
        # Check environment variables
        azure_key = os.getenv('AZURE_OPENAI_API_KEY')
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        ai_enabled = os.getenv('AI_CATEGORIZATION_ENABLED', 'true').lower() == 'true'
        
        return azure_key and azure_endpoint and ai_enabled
    
    def _get_default_categories(self) -> Dict[str, Any]:
        """Get default categories (legacy keyword format for backward compatibility)."""
        return {
            "Screen Time": ["screen time", "time limit", "time tracking"],
            "App Usage": ["app usage", "usage report", "usage tracking", "activity report"],
            "App Blocking": ["block", "blocking", "restriction", "access control"],
            "Web Filtering": ["web filter", "web filtering", "filtering", "safe browsing"],
            "Devices": ["device", "phone", "tablet", "tracking"],
            "Spending and Purchase": ["purchase", "paid", "premium", "subscription", "spending", "billing"],
            "Parental Consent & Age Restriction": ["parental consent", "consent", "approval", "age restriction"],
            "Notifications & Alerts": ["notification", "alert", "reminder", "message"],
            "Cross-Platform Sync": ["sync", "synchronization", "not updating", "not reflecting", "delay"],
            "Setup & Configuration": ["setup", "configuration", "install", "initial setup", "settings"],
            "App Performance": ["slow", "lag", "crash", "performance", "bug", "freeze"],
            "App Reliability": ["unstable", "reliable", "reliability", "stability", "fails", "failure"],
            "Login & Account Issues": ["login", "sign in", "account", "authentication", "credentials"],
            "Bypass & Circumvention": ["bypass", "disable", "turn off", "workaround", "hack", "override"],
            "Customer Support": ["support", "help", "contact", "response", "ticket", "no reply"],
            "Privacy Concerns": ["privacy", "data", "tracking", "monitoring", "spy", "surveillance"],
            "User Interface": ["interface", "design", "layout", "navigation", "UI", "UX"],
            "Others": []
        }
    
    def categorize_text(self, text: str) -> Dict[str, Any]:
        """
        Categorize a single text.
        
        Args:
            text: Text to categorize
            
        Returns:
            Dictionary with category, confidence, and method information
        """
        if self.use_ai and self.ai_categorizer:
            # Use AI categorization
            try:
                results = self.ai_categorizer.categorize_reviews([text])
                if results:
                    result = results[0]
                    return {
                        'category': result.get('category', 'Others'),
                        'confidence': result.get('confidence', 0.5),
                        'method': result.get('method', 'ai'),
                        'reason': result.get('reason', '')
                    }
            except Exception as e:
                print(f"AI categorization failed: {e}")
                # Fall through to keyword method
        
        # Fallback to keyword-based categorization
        category, confidence = self._categorize_with_keywords(text)
        return {
            'category': category,
            'confidence': confidence,
            'method': 'keyword',
            'reason': 'Keyword matching'
        }
    
    def _categorize_with_keywords(self, text: str) -> tuple[str, float]:
        """Keyword-based categorization fallback."""
        text_lower = text.lower()
        
        for category, data in self.categories.items():
            # Handle both new format (dict) and old format (list)
            keywords = data.get('keywords', data) if isinstance(data, dict) else data
            
            if not keywords:
                continue
                
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return category, 0.8  # High confidence for exact keyword match
        
        return "Others", 0.5
    
    def categorize_reviews(self, reviews: List[Review], filter_sentiment: str = None) -> List[Review]:
        """
        Categorize a list of reviews using AI or keyword matching.
        
        Args:
            reviews: List of Review objects
            filter_sentiment: Only categorize reviews with this sentiment (e.g., 'Negative')
            
        Returns:
            List of Review objects with categories assigned
        """
        if not reviews:
            return reviews
            
        # Filter reviews if sentiment filter is provided
        reviews_to_categorize = [
            review for review in reviews 
            if filter_sentiment is None or review.sentiment == filter_sentiment
        ]
        
        if not reviews_to_categorize:
            return reviews
        
        # Use AI categorization for batch processing if available
        if self.use_ai and self.ai_categorizer and len(reviews_to_categorize) > 1:
            try:
                review_texts = [review.text for review in reviews_to_categorize]
                ai_results = self.ai_categorizer.categorize_reviews(review_texts)
                
                # Apply results to reviews
                for i, result in enumerate(ai_results):
                    if i < len(reviews_to_categorize):
                        review = reviews_to_categorize[i]
                        review.category = result.get('category', 'Others')
                        review.category_confidence = result.get('confidence', 0.5)
                        review.categorization_method = result.get('method', 'ai')
                
                print(f"✓ AI categorized {len(reviews_to_categorize)} reviews")
                
            except Exception as e:
                print(f"⚠ AI batch categorization failed: {e}")
                # Fall back to individual categorization
                for review in reviews_to_categorize:
                    result = self.categorize_text(review.text)
                    review.category = result['category']
                    review.category_confidence = result['confidence']
                    review.categorization_method = result['method']
        else:
            # Individual categorization (keyword-based or single AI calls)
            for review in reviews_to_categorize:
                if filter_sentiment is None or review.sentiment == filter_sentiment:
                    result = self.categorize_text(review.text)
                    review.category = result['category']
                    review.category_confidence = result['confidence']
                    review.categorization_method = result['method']
                else:
                    review.category = ""
                    review.category_confidence = 0.0
                    review.categorization_method = "none"
        
        return reviews
    
    def categorize_reviews_batch_ai(self, reviews: List[Review]) -> Dict[str, Any]:
        """
        Categorize reviews using AI in batch mode and return detailed results.
        
        Args:
            reviews: List of Review objects
            
        Returns:
            Dictionary with categorization results and summary
        """
        if not self.use_ai or not self.ai_categorizer:
            return {"error": "AI categorization not available"}
        
        try:
            review_texts = [review.text for review in reviews]
            results = self.ai_categorizer.categorize_reviews(review_texts)
            summary = self.ai_categorizer.get_category_summary(results)
            
            # Apply results to reviews
            for i, result in enumerate(results):
                if i < len(reviews):
                    review = reviews[i]
                    review.category = result.get('category', 'Others')
                    review.category_confidence = result.get('confidence', 0.5)
                    review.categorization_method = result.get('method', 'ai')
            
            return {
                "success": True,
                "results": results,
                "summary": summary,
                "categorized_count": len(results)
            }
            
        except Exception as e:
            return {"error": f"AI categorization failed: {e}"}
    
    def get_category_distribution(self, reviews: List[Review], filter_sentiment: str = None) -> Dict[str, Any]:
        """
        Get distribution of categories across reviews with detailed metrics.
        
        Args:
            reviews: List of Review objects
            filter_sentiment: Only count reviews with this sentiment
            
        Returns:
            Dictionary with category counts, percentages, and confidence metrics
        """
        distribution = {}
        confidence_sum = {}
        method_counts = {}
        total_count = 0
        
        for review in reviews:
            # Skip if filter doesn't match
            if filter_sentiment and review.sentiment != filter_sentiment:
                continue
            
            if hasattr(review, 'category') and review.category:
                category = review.category
                distribution[category] = distribution.get(category, 0) + 1
                
                # Track confidence if available
                if hasattr(review, 'category_confidence'):
                    confidence_sum[category] = confidence_sum.get(category, 0) + review.category_confidence
                
                # Track categorization method if available
                if hasattr(review, 'categorization_method'):
                    method = review.categorization_method
                    if category not in method_counts:
                        method_counts[category] = {}
                    method_counts[category][method] = method_counts[category].get(method, 0) + 1
                
                total_count += 1
        
        # Calculate percentages and average confidence
        result = {
            'category_counts': distribution,
            'category_percentages': {},
            'category_avg_confidence': {},
            'category_methods': method_counts,
            'total_categorized': total_count
        }
        
        for category, count in distribution.items():
            result['category_percentages'][category] = (count / total_count * 100) if total_count > 0 else 0
            
            if category in confidence_sum:
                result['category_avg_confidence'][category] = confidence_sum[category] / count
        
        return result
    
    def get_ai_categorization_status(self) -> Dict[str, Any]:
        """Get status of AI categorization system."""
        return {
            'ai_available': AI_AVAILABLE,
            'ai_enabled': self.use_ai,
            'product_name': self.product_name,
            'azure_configured': bool(os.getenv('AZURE_OPENAI_API_KEY')),
            'categories_count': len(self.categories),
            'categorizer_type': 'AI + Keyword Fallback' if self.use_ai else 'Keyword Only'
        }
    
    def add_category(self, category_name: str, definition: Dict[str, Any] = None, keywords: List[str] = None) -> None:
        """
        Add a new category with AI-friendly definition or legacy keywords.
        
        Args:
            category_name: Name of the category
            definition: Full category definition with description, examples, keywords
            keywords: Legacy keyword list (for backward compatibility)
        """
        if definition:
            self.categories[category_name] = definition
        elif keywords:
            self.categories[category_name] = keywords
        else:
            self.categories[category_name] = []
    
    def remove_category(self, category_name: str) -> None:
        """Remove a category."""
        if category_name in self.categories:
            del self.categories[category_name]
    
    def update_category(self, category_name: str, definition: Dict[str, Any] = None, keywords: List[str] = None) -> None:
        """
        Update an existing category.
        
        Args:
            category_name: Name of the category
            definition: Full category definition with description, examples, keywords  
            keywords: Legacy keyword list (for backward compatibility)
        """
        if category_name in self.categories:
            if definition:
                self.categories[category_name] = definition
            elif keywords:
                self.categories[category_name] = keywords
    
    def export_categories_for_ai(self) -> Dict[str, Any]:
        """Export categories in AI-friendly format for configuration."""
        ai_format = {}
        
        for name, data in self.categories.items():
            if isinstance(data, dict):
                # Already in AI format
                ai_format[name] = data
            elif isinstance(data, list):
                # Convert from legacy keyword format
                ai_format[name] = {
                    "description": f"Issues related to {name.lower()}",
                    "examples": [f"Problems with {name.lower()}"],
                    "keywords": data
                }
        
        return ai_format
