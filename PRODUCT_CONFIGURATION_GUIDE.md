# Product Configuration Guide

This guide explains how to add new products to the Review Analysis Platform.

## Overview

The system now supports multiple products through configurable YAML files. Each product can have its own:
- App Store identifiers (Play Store and App Store IDs)
- Search terms for different data sources
- Product-specific feature categories
- Custom fetch limits
- Data source configurations

## Adding a New Product

### 1. Create Product Configuration File

Create a new YAML file in `config/products/` directory:
- File name format: `{product_name}.yaml` (use lowercase with underscores)
- Example: `my_product.yaml`

### 2. Configuration Structure

```yaml
# Basic Product Information
product:
  name: "Your Product Name"
  description: "Brief description of the product"
  company: "Company Name"

# App Store Identifiers
app_identifiers:
  playstore: "com.company.product"  # Android package name
  appstore: "123456789"             # iOS App Store ID

# Search Terms for Data Sources
search_terms:
  twitter:
    primary_query: '"Product Name" OR "Product issues" OR "Product not working"'
    additional_keywords: ["product", "app name", "company"]
    
  rss:
    feed_urls:
      - "https://news.google.com/rss/search?q=\"Product+Name\"&hl=en-US&gl=US&ceid=US:en"
    
  news:
    query: "Product Name issue OR complaint OR review"
    additional_queries: 
      - "Product Name bug"
      - "Product Name not working"

# Product-Specific Feature Categories
categories:
  "Core Feature 1": ["keyword1", "keyword2", "phrase"]
  "Core Feature 2": ["feature", "functionality", "related terms"]
  "Performance": ["slow", "lag", "crash", "performance", "bug"]
  # Add more categories relevant to your product

# Data Source Configuration
data_sources:
  playstore:
    enabled: true
  appstore:
    enabled: true
  twitter:
    enabled: true
  rss:
    enabled: true
  news:
    enabled: true

# Custom Fetch Limits (optional)
limits:
  playstore: 2000
  appstore: 300
  twitter: 150
  rss: 100
  news: 100
```

## Configuration Details

### Product Information
- `name`: Display name for the product
- `description`: Brief description shown in product selection
- `company`: Company/organization name

### App Identifiers
- `playstore`: Android package name (e.g., "com.family.safety")
- `appstore`: iOS App Store ID (numeric string, e.g., "12345678")

### Search Terms
Configure how the system searches for your product across different data sources:

#### Twitter
- `primary_query`: Main search query using Twitter search syntax
- `additional_keywords`: Array of additional keywords

#### RSS
- `feed_urls`: Array of RSS feed URLs for news/updates

#### News
- `query`: Primary news search query
- `additional_queries`: Array of additional search terms

### Feature Categories
Define product-specific features and their associated keywords:
- Each category maps to an array of keywords
- Keywords are used for automatic categorization of reviews
- Include variations, synonyms, and common phrases

### Common Categories
The system includes common categories applicable to most apps:
- App Performance
- User Interface
- Login & Account Issues
- Customer Support
- Privacy Concerns
- Setup & Configuration
- Notifications & Alerts
- Update Issues
- Feature Limitations
- Spending and Purchase

### Data Sources
Enable/disable data sources for your product:
- `playstore`: Google Play Store reviews
- `appstore`: Apple App Store reviews  
- `twitter`: Twitter mentions and discussions
- `rss`: RSS feeds and news
- `news`: News articles and blogs

### Fetch Limits
Customize how many items to fetch from each source:
- Higher limits = more comprehensive data
- Lower limits = faster processing
- Adjust based on product popularity and data availability

## Examples

See existing configurations:
- `microsoft_family_safety.yaml` - Parental control app
- `microsoft_outlook.yaml` - Email and calendar app

## Best Practices

1. **Keywords**: Include both specific terms and general concepts
2. **Search Queries**: Use product name variations and common issues
3. **Categories**: Focus on core product features and common pain points
4. **Testing**: Start with lower limits to test configuration
5. **Iteration**: Refine categories based on initial analysis results

## Using Your Configuration

1. Save your YAML file in `config/products/`
2. Run the main application: `python main.py`
3. Select your product from the list
4. Review the analysis results and refine categories as needed

## Troubleshooting

- **Product not appearing**: Check YAML syntax and file location
- **No reviews found**: Verify app identifiers are correct
- **Poor categorization**: Refine keywords and add more specific terms
- **Missing features**: Add categories for features specific to your product

## Advanced Configuration

You can override default settings from `config/base_config.yaml`:
- Sentiment thresholds
- Output directory structure
- Analysis parameters
- Default data source settings

Consult the base configuration file for available options.