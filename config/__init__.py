"""
Configuration loader for the application.
"""
import yaml
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """Configuration loader class."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        
        self.config_path = config_path
        self._config = None
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
        """
        if self._config is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._config = yaml.safe_load(file)
            except FileNotFoundError:
                print(f"Config file not found: {self.config_path}")
                self._config = self._get_default_config()
            except yaml.YAMLError as e:
                print(f"Error parsing config file: {e}")
                self._config = self._get_default_config()
        
        return self._config
    
    def get_data_source_config(self, source_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Data source configuration
        """
        config = self.load_config()
        return config.get('data_sources', {}).get(source_name, {})
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """
        Get analysis configuration.
        
        Returns:
            Analysis configuration
        """
        config = self.load_config()
        return config.get('analysis', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        Get output configuration.
        
        Returns:
            Output configuration
        """
        config = self.load_config()
        return config.get('output', {})
    
    def get_limits_config(self) -> Dict[str, int]:
        """
        Get limits configuration.
        
        Returns:
            Limits configuration
        """
        config = self.load_config()
        return config.get('limits', {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration if file is not found.
        
        Returns:
            Default configuration
        """
        return {
            'data_sources': {
                'playstore': {
                    'enabled': True,
                    'app_id': 'com.microsoft.familysafety',
                    'lang': 'en',
                    'country': 'us'
                },
                'appstore': {
                    'enabled': True,
                    'app_id': '1519844643',
                    'countries': ['us', 'in', 'gb', 'ca', 'au']
                },
                'twitter': {
                    'enabled': False,  # Disabled due to snscrape compatibility issues
                    'default_query': '"Microsoft Family Safety" OR "Family Safety app"',
                    'days_back': 120,
                    'include_retweets': False
                },
                'rss': {
                    'enabled': True,
                    'days_back': 120
                },
                'news': {
                    'enabled': True,
                    'default_query': 'Microsoft Family Safety issue OR complaint',
                    'days_back': 120,
                    'search_results': 100
                }
            },
            'analysis': {
                'sentiment_threshold': -0.05
            },
            'output': {
                'directory': 'output',
                'csv_filename': 'reviews_analysis.csv',
                'summary_filename': 'analysis_summary.json'
            },
            'limits': {
                'playstore': 500,
                'appstore': 200,
                'twitter': 100,
                'rss': 100,
                'news': 100
            }
        }
