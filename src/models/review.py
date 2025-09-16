"""
Review data model for the application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Review:
    """
    Standardized review data model that all data sources must conform to.
    Enhanced with AI categorization support.
    """
    id: str
    source: str  # 'playstore', 'appstore', 'twitter', 'rss', 'news'
    text: str
    title: Optional[str] = None
    author: Optional[str] = None
    rating: Optional[float] = None
    date: Optional[datetime] = None
    url: Optional[str] = None
    sentiment: Optional[str] = None
    category: Optional[str] = None
    category_confidence: Optional[float] = None  # Confidence score for categorization
    categorization_method: Optional[str] = None  # 'ai', 'keyword', 'manual'
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate and clean data after initialization."""
        if not self.text:
            raise ValueError("Review text cannot be empty")
        
        # Clean text
        self.text = self.text.strip()
        
        # Ensure source is lowercase
        self.source = self.source.lower()
        
        # Initialize metadata if None
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert review to dictionary for easier processing."""
        return {
            'id': self.id,
            'source': self.source,
            'text': self.text,
            'title': self.title,
            'author': self.author,
            'rating': self.rating,
            'date': self.date.isoformat() if self.date else None,
            'url': self.url,
            'sentiment': self.sentiment,
            'category': self.category,
            'category_confidence': self.category_confidence,
            'categorization_method': self.categorization_method,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Review':
        """Create review from dictionary."""
        if data.get('date') and isinstance(data['date'], str):
            data['date'] = datetime.fromisoformat(data['date'])
        
        return cls(**data)
