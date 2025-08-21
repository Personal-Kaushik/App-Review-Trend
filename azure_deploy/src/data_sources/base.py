"""
Base interface for all data sources.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.models.review import Review


class DataSource(ABC):
    """
    Abstract base class for all data sources.
    Every data source must implement this interface.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data source with configuration.
        
        Args:
            config: Configuration dictionary for the data source
        """
        self.config = config or {}
        self.source_name = self._get_source_name()
    
    @abstractmethod
    def _get_source_name(self) -> str:
        """Return the name of the data source (e.g., 'playstore', 'twitter')."""
        pass
    
    @abstractmethod
    def fetch_reviews(self, query: str, limit: int = 100, **kwargs) -> List[Review]:
        """
        Fetch reviews from the data source.
        
        Args:
            query: Search query or app identifier
            limit: Maximum number of reviews to fetch
            **kwargs: Additional parameters specific to the data source
            
        Returns:
            List of Review objects
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the configuration for this data source.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    def get_supported_parameters(self) -> List[str]:
        """
        Get list of supported parameters for this data source.
        
        Returns:
            List of parameter names
        """
        return []
    
    def preprocess_reviews(self, reviews: List[Review]) -> List[Review]:
        """
        Preprocess reviews if needed (e.g., deduplication, cleaning).
        
        Args:
            reviews: List of Review objects
            
        Returns:
            Preprocessed list of Review objects
        """
        return reviews
