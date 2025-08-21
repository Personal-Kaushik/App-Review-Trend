"""
Review categorization module.
"""
from typing import List, Dict, Any
from src.models.review import Review


class ReviewCategorizer:
    """Review categorizer based on keywords."""
    
    def __init__(self, categories: Dict[str, List[str]] = None):
        """
        Initialize categorizer.
        
        Args:
            categories: Dictionary mapping category names to keyword lists
        """
        self.categories = categories or self._get_default_categories()
    
    def _get_default_categories(self) -> Dict[str, List[str]]:
        """Get default categories for Microsoft Family Safety."""
        return {
            "Screen Time": ["screen time", "time limit", "time tracking"],
            "App Usage": ["app usage", "usage report", "usage tracking", "activity report"],
            "App Blocking": ["block", "blocking", "restriction", "access control"],
            "Web Filtering": ["web filter", "web filtering", "filtering", "safe browsing"],
            "Devices": ["device", "phone", "tablet", "tracking"],
            "Spending and Purchase": ["purchase", "paid", "premium", "subscription", "spending", "billing"],
            "Parental Consent & Age Restriction": ["parental consent", "consent", "approval", "age restriction", "age limit", "age control"],
            "Notifications & Alerts": ["notification", "alert", "reminder", "message"],
            "Cross-Platform Sync": ["sync", "synchronization", "not updating", "not reflecting", "delay", "real-time"],
            "Setup & Configuration": ["setup", "configuration", "install", "initial setup", "settings"],
            "App Performance": ["slow", "lag", "crash", "performance", "bug", "freeze"],
            "App Reliability": ["unstable", "reliable", "reliability", "stability", "fails", "failure"],
            "Login & Account Issues": ["login", "sign in", "account", "authentication", "credentials", "password", "email"],
            "Bypass & Circumvention": ["bypass", "disable", "turn off", "workaround", "hack", "override", "ignore"],
            "Customer Support": ["support", "help", "contact", "response", "ticket", "no reply", "assistance"],
            "Privacy Concerns": ["privacy", "data", "tracking", "monitoring", "spy", "surveillance"],
            "User Interface": ["interface", "design", "layout", "navigation", "UI", "UX"],
            "Full Frustration": ["hate", "terrible", "worst", "awful", "useless", "frustrating", "annoying", "disappointed"],
            "Feature Limitations": ["missing feature", "can't do", "not available", "removed", "limited", "lack of"],
            "Approval & Permissions": ["approve", "approval", "permission", "request", "grant access", "extra time"],
            "Time Propagation & Sync Delay": ["delay", "not updating", "not reflecting", "takes time", "propagate"],
            "Child Account Management": ["child account", "add child", "manage child", "child profile"],
            "Game & Xbox Integration": ["xbox", "game", "minecraft", "console", "play", "gaming"],
            "Forced Usage & App Dependency": ["forced", "have to use", "required", "mandatory", "can't avoid"],
            "Account Linking & Sharing": ["share", "link", "family member", "office", "account sharing"],
            "Update Issues": ["update", "after update", "new version", "latest version"],
            "Add Money": ["add money", "in-app purchase", "buy", "payment", "add balance", "billing"]
        }
    
    def categorize_text(self, text: str) -> str:
        """
        Categorize a single text.
        
        Args:
            text: Text to categorize
            
        Returns:
            Category name or "Others" if no match
        """
        text_lower = text.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return "Others"
    
    def categorize_reviews(self, reviews: List[Review], filter_sentiment: str = None) -> List[Review]:
        """
        Categorize a list of reviews.
        
        Args:
            reviews: List of Review objects
            filter_sentiment: Only categorize reviews with this sentiment (e.g., 'Negative')
            
        Returns:
            List of Review objects with categories assigned
        """
        for review in reviews:
            # Only categorize if no filter or sentiment matches
            if filter_sentiment is None or review.sentiment == filter_sentiment:
                review.category = self.categorize_text(review.text)
            else:
                review.category = ""
        
        return reviews
    
    def get_category_distribution(self, reviews: List[Review], filter_sentiment: str = None) -> Dict[str, int]:
        """
        Get distribution of categories across reviews.
        
        Args:
            reviews: List of Review objects
            filter_sentiment: Only count reviews with this sentiment
            
        Returns:
            Dictionary with category counts
        """
        distribution = {}
        
        for review in reviews:
            # Skip if filter doesn't match
            if filter_sentiment and review.sentiment != filter_sentiment:
                continue
            
            if review.category:
                distribution[review.category] = distribution.get(review.category, 0) + 1
        
        return distribution
    
    def add_category(self, category_name: str, keywords: List[str]) -> None:
        """
        Add a new category.
        
        Args:
            category_name: Name of the category
            keywords: List of keywords for the category
        """
        self.categories[category_name] = keywords
    
    def remove_category(self, category_name: str) -> None:
        """
        Remove a category.
        
        Args:
            category_name: Name of the category to remove
        """
        if category_name in self.categories:
            del self.categories[category_name]
    
    def update_category_keywords(self, category_name: str, keywords: List[str]) -> None:
        """
        Update keywords for an existing category.
        
        Args:
            category_name: Name of the category
            keywords: New list of keywords
        """
        self.categories[category_name] = keywords
