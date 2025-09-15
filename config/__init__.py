"""
Configuration loader for the application.
"""
import yaml
import os
from typing import Dict, Any, Optional, List


class ConfigLoader:
    """Configuration loader class with product support."""
    
    def __init__(self, product_name: str = None, config_path: str = None):
        """
        Initialize config loader.
        
        Args:
            product_name: Name of the product to load configuration for
            config_path: Path to base configuration file (optional)
        """
        self.config_dir = os.path.dirname(__file__)
        self.products_dir = os.path.join(self.config_dir, 'products')
        
        # Set base config path
        if config_path is None:
            config_path = os.path.join(self.config_dir, 'base_config.yaml')
        self.base_config_path = config_path
        
        # Set product
        self.product_name = product_name
        self.product_config_path = None
        if product_name:
            self.product_config_path = os.path.join(self.products_dir, f"{product_name}.yaml")
        
        self._config = None
        self._base_config = None
        self._product_config = None
    
    def get_available_products(self) -> List[str]:
        """
        Get list of available product configurations.
        
        Returns:
            List of available product names
        """
        if not os.path.exists(self.products_dir):
            return []
        
        products = []
        for file in os.listdir(self.products_dir):
            if file.endswith('.yaml') or file.endswith('.yml'):
                # Remove extension to get product name
                product_name = os.path.splitext(file)[0]
                products.append(product_name)
        
        return sorted(products)
    
    def get_product_info(self, product_name: str = None) -> Dict[str, Any]:
        """
        Get product information (name, description, company).
        
        Args:
            product_name: Product name (uses current product if None)
            
        Returns:
            Product information dictionary
        """
        if product_name is None:
            product_name = self.product_name
        
        if not product_name:
            return {}
        
        product_config = self._load_product_config(product_name)
        return product_config.get('product', {})
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load merged configuration (base + product-specific).
        
        Returns:
            Merged configuration dictionary
        """
        if self._config is None:
            # Load base configuration
            base_config = self._load_base_config()
            
            # Load product configuration if specified
            if self.product_name:
                product_config = self._load_product_config(self.product_name)
                self._config = self._merge_configs(base_config, product_config)
            else:
                self._config = base_config
        
        return self._config
    
    def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration."""
        if self._base_config is None:
            try:
                with open(self.base_config_path, 'r', encoding='utf-8') as file:
                    self._base_config = yaml.safe_load(file)
            except FileNotFoundError:
                print(f"Base config file not found: {self.base_config_path}")
                self._base_config = self._get_default_base_config()
            except yaml.YAMLError as e:
                print(f"Error parsing base config file: {e}")
                self._base_config = self._get_default_base_config()
        
        return self._base_config
    
    def _load_product_config(self, product_name: str) -> Dict[str, Any]:
        """Load product-specific configuration."""
        product_path = os.path.join(self.products_dir, f"{product_name}.yaml")
        
        try:
            with open(product_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Product config file not found: {product_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing product config file: {e}")
            return {}
    
    def _merge_configs(self, base_config: Dict[str, Any], product_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge base and product configurations.
        
        Args:
            base_config: Base configuration
            product_config: Product-specific configuration
            
        Returns:
            Merged configuration
        """
        merged = base_config.copy()
        
        # Merge analysis settings
        if 'analysis' in merged and 'categories' in product_config:
            # Combine common categories with product-specific ones
            common_categories = merged['analysis'].get('common_categories', {})
            product_categories = product_config.get('categories', {})
            merged['analysis']['categories'] = {**common_categories, **product_categories}
        
        # Build data sources configuration
        data_sources = {}
        default_settings = merged.get('default_data_source_settings', {})
        product_data_sources = product_config.get('data_sources', {})
        app_identifiers = product_config.get('app_identifiers', {})
        search_terms = product_config.get('search_terms', {})
        
        for source_name in ['playstore', 'appstore', 'twitter', 'rss', 'news']:
            source_config = default_settings.get(source_name, {}).copy()
            
            # Add app identifiers
            if source_name in app_identifiers:
                source_config['app_id'] = app_identifiers[source_name]
            
            # Add search terms
            if source_name in search_terms:
                search_config = search_terms[source_name]
                if source_name == 'twitter':
                    source_config['default_query'] = search_config.get('primary_query', '')
                elif source_name == 'rss':
                    source_config['feed_urls'] = search_config.get('feed_urls', [])
                elif source_name == 'news':
                    source_config['default_query'] = search_config.get('query', '')
            
            # Set enabled status
            source_config['enabled'] = product_data_sources.get(source_name, {}).get('enabled', False)
            
            data_sources[source_name] = source_config
        
        merged['data_sources'] = data_sources
        
        # Merge limits
        default_limits = merged.get('default_limits', {})
        product_limits = product_config.get('limits', {})
        merged['limits'] = {**default_limits, **product_limits}
        
        return merged
    
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
    
    def _get_default_base_config(self) -> Dict[str, Any]:
        """
        Get default base configuration if file is not found.
        
        Returns:
            Default base configuration
        """
        return {
            'analysis': {
                'sentiment_threshold': -0.05,
                'data_collection_period_months': 6
            },
            'output': {
                'directory': 'output',
                'csv_filename': 'reviews_analysis.csv',
                'summary_filename': 'analysis_summary.json'
            },
            'default_limits': {
                'playstore': 2000,
                'appstore': 200,
                'twitter': 100,
                'rss': 100,
                'news': 100
            },
            'default_data_source_settings': {
                'playstore': {
                    'lang': 'en',
                    'country': 'us'
                },
                'appstore': {
                    'countries': ['us', 'in', 'gb', 'ca', 'au']
                },
                'twitter': {
                    'days_back': 120,
                    'include_retweets': False
                },
                'rss': {
                    'days_back': 120
                },
                'news': {
                    'days_back': 120,
                    'search_results': 100
                }
            }
        }
