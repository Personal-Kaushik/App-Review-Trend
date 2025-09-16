"""
AI-powered review categorization using Azure OpenAI.
Provides intelligent, configurable categorization for different products.
"""
import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

try:
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AzureOpenAI = None

logger = logging.getLogger(__name__)


@dataclass
class CategoryDefinition:
    """Definition of a product category with description and examples."""
    name: str
    description: str
    examples: List[str]
    keywords: List[str] = None  # Fallback keywords for non-AI categorization


@dataclass
class CategorizationConfig:
    """Configuration for AI categorization."""
    product_name: str
    categories: List[CategoryDefinition]
    use_ai: bool = True
    cache_results: bool = True
    confidence_threshold: float = 0.7
    batch_size: int = 10


class AICategorizer:
    """AI-powered categorization system using Azure OpenAI."""
    
    def __init__(self, config: CategorizationConfig):
        """
        Initialize the AI categorizer.
        
        Args:
            config: Categorization configuration
        """
        self.config = config
        self.client = None
        self.cache = {}
        self.cache_file = f"cache/categorization_cache_{config.product_name}.json"
        
        # Initialize Azure OpenAI client if available and enabled
        if OPENAI_AVAILABLE and config.use_ai:
            self._initialize_openai_client()
        
        # Load cache if enabled
        if config.cache_results:
            self._load_cache()
    
    def _initialize_openai_client(self):
        """Initialize Azure OpenAI client from environment variables."""
        try:
            # Get Azure OpenAI configuration from environment
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
            
            if not api_key or not endpoint:
                logger.warning("Azure OpenAI credentials not found in environment variables")
                logger.warning("Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")
                return
            
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            
            logger.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            self.client = None
    
    def _load_cache(self):
        """Load categorization cache from file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Only load recent cache entries (last 30 days)
                    cutoff_date = datetime.now() - timedelta(days=30)
                    self.cache = {
                        k: v for k, v in cache_data.items()
                        if datetime.fromisoformat(v.get('timestamp', '2000-01-01')) > cutoff_date
                    }
                logger.info(f"Loaded {len(self.cache)} cached categorizations")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save categorization cache to file."""
        if not self.config.cache_results:
            return
        
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(f"{self.config.product_name}:{text}".encode()).hexdigest()
    
    def _create_categorization_prompt(self, reviews: List[str]) -> str:
        """Create the prompt for AI categorization."""
        # Build category descriptions
        category_descriptions = []
        for cat in self.config.categories:
            examples_text = ", ".join(cat.examples[:3])  # Limit examples
            category_descriptions.append(
                f"- **{cat.name}**: {cat.description}\n  Examples: {examples_text}"
            )
        
        categories_text = "\n".join(category_descriptions)
        reviews_text = "\n".join([f"{i+1}. {review}" for i, review in enumerate(reviews)])
        
        prompt = f"""You are an expert at categorizing customer reviews for {self.config.product_name}.

**Available Categories:**
{categories_text}

**Instructions:**
1. Analyze each review and assign it to the MOST appropriate category
2. If a review doesn't clearly fit any category, assign it to "Others"
3. Focus on the main complaint or issue mentioned
4. Return results as a JSON array with this format:
   [{{"review_index": 1, "category": "Category Name", "confidence": 0.85, "reason": "Brief explanation"}}]

**Reviews to categorize:**
{reviews_text}

Return only the JSON array, no other text:"""
        
        return prompt
    
    def _categorize_with_ai(self, reviews: List[str]) -> List[Dict[str, Any]]:
        """Categorize reviews using Azure OpenAI."""
        if not self.client:
            return []
        
        try:
            prompt = self._create_categorization_prompt(reviews)
            
            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert at categorizing customer feedback for {self.config.product_name}. Always return valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Clean up the response (remove code blocks if present)
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            results = json.loads(content)
            
            # Validate results
            valid_categories = {cat.name for cat in self.config.categories} | {"Others"}
            for result in results:
                if result.get('category') not in valid_categories:
                    result['category'] = 'Others'
                    result['confidence'] = 0.5
            
            return results
            
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            return []
    
    def _categorize_with_keywords(self, review_text: str) -> Tuple[str, float]:
        """Fallback categorization using keyword matching."""
        review_lower = review_text.lower()
        best_match = ("Others", 0.5)
        
        for category in self.config.categories:
            if not category.keywords:
                continue
            
            # Count keyword matches
            matches = sum(1 for keyword in category.keywords if keyword.lower() in review_lower)
            confidence = min(matches / len(category.keywords), 1.0)
            
            if confidence > best_match[1]:
                best_match = (category.name, confidence)
        
        return best_match
    
    def categorize_reviews(self, reviews: List[str]) -> List[Dict[str, Any]]:
        """
        Categorize a list of reviews.
        
        Args:
            reviews: List of review texts
            
        Returns:
            List of categorization results with category, confidence, and method
        """
        results = []
        uncached_reviews = []
        uncached_indices = []
        
        # Check cache first
        for i, review in enumerate(reviews):
            cache_key = self._get_cache_key(review)
            if cache_key in self.cache:
                cached_result = self.cache[cache_key].copy()
                cached_result['review_index'] = i
                results.append(cached_result)
            else:
                uncached_reviews.append(review)
                uncached_indices.append(i)
        
        logger.info(f"Found {len(results)} cached results, {len(uncached_reviews)} to process")
        
        # Process uncached reviews
        if uncached_reviews:
            # Try AI categorization first
            ai_results = []
            if self.client and self.config.use_ai:
                # Process in batches
                for i in range(0, len(uncached_reviews), self.config.batch_size):
                    batch = uncached_reviews[i:i + self.config.batch_size]
                    batch_results = self._categorize_with_ai(batch)
                    
                    # Adjust indices for the full list
                    for result in batch_results:
                        if 'review_index' in result:
                            result['review_index'] = uncached_indices[i + result['review_index'] - 1]
                            result['method'] = 'ai'
                    
                    ai_results.extend(batch_results)
            
            # Fill in any missing results with keyword matching
            ai_indices = {r.get('review_index') for r in ai_results}
            for i, review in enumerate(uncached_reviews):
                original_index = uncached_indices[i]
                
                if original_index not in ai_indices:
                    category, confidence = self._categorize_with_keywords(review)
                    ai_results.append({
                        'review_index': original_index,
                        'category': category,
                        'confidence': confidence,
                        'method': 'keyword',
                        'reason': 'AI categorization unavailable'
                    })
            
            # Cache new results
            for i, result in enumerate(ai_results):
                review_index = result.get('review_index')
                if review_index is not None and review_index < len(reviews):
                    review = reviews[review_index]
                    cache_key = self._get_cache_key(review)
                    cache_entry = result.copy()
                    cache_entry['timestamp'] = datetime.now().isoformat()
                    self.cache[cache_key] = cache_entry
            
            results.extend(ai_results)
        
        # Save cache
        if self.config.cache_results and uncached_reviews:
            self._save_cache()
        
        # Sort results by review index
        results.sort(key=lambda x: x.get('review_index', 0))
        
        return results
    
    def get_category_summary(self, categorization_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of categorization results.
        
        Args:
            categorization_results: Results from categorize_reviews
            
        Returns:
            Summary statistics
        """
        total_reviews = len(categorization_results)
        if total_reviews == 0:
            return {}
        
        # Count by category
        category_counts = {}
        ai_count = 0
        keyword_count = 0
        total_confidence = 0
        
        for result in categorization_results:
            category = result.get('category', 'Others')
            category_counts[category] = category_counts.get(category, 0) + 1
            
            if result.get('method') == 'ai':
                ai_count += 1
            else:
                keyword_count += 1
            
            total_confidence += result.get('confidence', 0.5)
        
        # Calculate percentages
        category_percentages = {
            cat: (count / total_reviews) * 100 
            for cat, count in category_counts.items()
        }
        
        return {
            'total_reviews': total_reviews,
            'category_counts': category_counts,
            'category_percentages': category_percentages,
            'ai_categorized': ai_count,
            'keyword_categorized': keyword_count,
            'average_confidence': total_confidence / total_reviews,
            'method_breakdown': {
                'ai_percentage': (ai_count / total_reviews) * 100,
                'keyword_percentage': (keyword_count / total_reviews) * 100
            }
        }


def create_categorizer_from_config(product_name: str, categories_config: Dict[str, Any]) -> AICategorizer:
    """
    Create an AI categorizer from product configuration.
    
    Args:
        product_name: Name of the product
        categories_config: Categories configuration from YAML
        
    Returns:
        Configured AICategorizer instance
    """
    # Convert categories config to CategoryDefinition objects
    category_definitions = []
    
    if isinstance(categories_config, dict):
        for cat_name, cat_data in categories_config.items():
            if isinstance(cat_data, list):
                # Old format: category name -> keyword list
                category_definitions.append(CategoryDefinition(
                    name=cat_name,
                    description=f"Issues related to {cat_name.lower()}",
                    examples=[f"Problems with {cat_name.lower()}"],
                    keywords=cat_data
                ))
            elif isinstance(cat_data, dict):
                # New format: category name -> definition dict
                category_definitions.append(CategoryDefinition(
                    name=cat_name,
                    description=cat_data.get('description', f"Issues related to {cat_name.lower()}"),
                    examples=cat_data.get('examples', []),
                    keywords=cat_data.get('keywords', [])
                ))
    
    # Add "Others" category if not present
    if not any(cat.name == "Others" for cat in category_definitions):
        category_definitions.append(CategoryDefinition(
            name="Others",
            description="General issues or complaints that don't fit into specific categories",
            examples=["General app complaints", "Unspecified problems", "Mixed feedback"],
            keywords=[]
        ))
    
    config = CategorizationConfig(
        product_name=product_name,
        categories=category_definitions,
        use_ai=os.getenv('AZURE_OPENAI_API_KEY') is not None,
        cache_results=True,
        confidence_threshold=0.7,
        batch_size=5  # Smaller batches for better reliability
    )
    
    return AICategorizer(config)


# Example usage and testing
if __name__ == "__main__":
    # Example categories for Microsoft Family Safety
    example_categories = {
        "Screen Time": {
            "description": "Issues with screen time limits, tracking, and time management features",
            "examples": [
                "Screen time limits not working properly",
                "Daily time limits are being ignored",
                "Time tracking is inaccurate"
            ],
            "keywords": ["screen time", "time limit", "daily limit", "usage time"]
        },
        "App Blocking": {
            "description": "Problems with blocking or restricting access to specific applications",
            "examples": [
                "App blocking feature is not working",
                "Restricted apps are still accessible",
                "Cannot block specific games"
            ],
            "keywords": ["block", "blocking", "restriction", "access control"]
        }
    }
    
    # Create categorizer
    categorizer = create_categorizer_from_config("Microsoft Family Safety", example_categories)
    
    # Example reviews
    test_reviews = [
        "The screen time limits don't work at all, my kid can still use apps after the time is up",
        "App blocking is completely broken, blocked apps are still accessible",
        "The app crashes when I try to open it"
    ]
    
    # Categorize
    results = categorizer.categorize_reviews(test_reviews)
    summary = categorizer.get_category_summary(results)
    
    print("Categorization Results:")
    for result in results:
        print(f"Review {result['review_index']}: {result['category']} (confidence: {result['confidence']:.2f})")
    
    print("\nSummary:")
    print(json.dumps(summary, indent=2))