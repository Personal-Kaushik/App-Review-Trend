"""
Data source factory for creating data source instances.
"""
from typing import Dict, Any, Optional, Type
from src.data_sources.base import DataSource

# Import data sources with error handling
available_sources = {}

# Try to import PlayStore data source
try:
    from src.data_sources.playstore import PlayStoreDataSource
    available_sources['playstore'] = PlayStoreDataSource
except ImportError as e:
    print(f"Warning: PlayStore data source is not available: {e}")

# Try to import AppStore data source
try:
    from src.data_sources.appstore import AppStoreDataSource
    available_sources['appstore'] = AppStoreDataSource
except ImportError as e:
    print(f"Warning: AppStore data source is not available: {e}")

# Try to import RSS data source
try:
    from src.data_sources.rss import RSSDataSource
    available_sources['rss'] = RSSDataSource
except ImportError as e:
    print(f"Warning: RSS data source is not available: {e}")

# Try to import News data source
try:
    from src.data_sources.news import NewsDataSource
    available_sources['news'] = NewsDataSource
except ImportError as e:
    print(f"Warning: News data source is not available: {e}")

# Try to import Twitter data source
try:
    from src.data_sources.twitter import TwitterDataSource
    available_sources['twitter'] = TwitterDataSource
except ImportError as e:
    print(f"Warning: Twitter data source is not available: {e}")


class DataSourceFactory:
    """Factory class for creating data source instances."""
    
    _sources: Dict[str, Type[DataSource]] = available_sources
    
    @classmethod
    def get_available_sources(cls) -> list:
        """Get list of available data sources."""
        return list(cls._sources.keys())
    
    @classmethod
    def create_source(cls, source_name: str, config: Optional[Dict[str, Any]] = None) -> DataSource:
        """
        Create a data source instance.
        
        Args:
            source_name: Name of the data source
            config: Configuration dictionary for the data source
            
        Returns:
            DataSource instance
            
        Raises:
            ValueError: If source_name is not supported
        """
        if source_name not in cls._sources:
            raise ValueError(f"Unknown data source: {source_name}. Available: {list(cls._sources.keys())}")
        
        source_class = cls._sources[source_name]
        return source_class(config)
    
    @classmethod
    def register_source(cls, source_name: str, source_class: Type[DataSource]) -> None:
        """
        Register a new data source.
        
        Args:
            source_name: Name of the data source
            source_class: Data source class
        """
        cls._sources[source_name] = source_class
    
    @classmethod
    def create_all_sources(cls, config: Dict[str, Dict[str, Any]]) -> Dict[str, DataSource]:
        """
        Create all configured data sources.
        
        Args:
            config: Configuration dictionary with source-specific configs
            
        Returns:
            Dictionary mapping source names to DataSource instances
        """
        sources = {}
        
        for source_name in cls._sources:
            source_config = config.get(source_name, {})
            if source_config.get('enabled', True):  # Default to enabled
                try:
                    source = cls.create_source(source_name, source_config)
                    if source.validate_config():
                        sources[source_name] = source
                    else:
                        print(f"Warning: Invalid configuration for {source_name}")
                except Exception as e:
                    print(f"Error creating {source_name} source: {e}")
        
        return sources
