# Troubleshooting Guide

## Common Issues and Solutions

### 1. Import Errors

**Problem**: `ImportError` or `ModuleNotFoundError` when running the application.

**Solution**:
- Run `python install.py` to install dependencies
- Use `python main_minimal.py` instead of `python main.py`
- Check that you're in the correct directory

### 2. snscrape Compatibility Issues

**Problem**: `AttributeError: 'FileFinder' object has no attribute 'find_module'`

**Solution**:
- Twitter functionality is disabled by default due to this issue
- The system will work without Twitter data
- Alternative: Use older Python version (3.11 or earlier) if Twitter data is needed

### 3. lxml.html.clean Issues

**Problem**: `ImportError: lxml.html.clean module is now a separate project`

**Solution**:
- Install the separate package: `pip install lxml[html_clean]`
- Or use the minimal version which doesn't require news scraping
- News functionality will be disabled if this fails

### 4. No Reviews Found

**Problem**: System reports "No reviews found"

**Possible Causes & Solutions**:
- **Network Issues**: Check internet connection
- **API Limits**: Try reducing the fetch limits in config.yaml
- **App ID Issues**: Verify the app IDs are correct in config.yaml
- **Rate Limiting**: Wait some time before retrying

### 5. SSL Certificate Errors

**Problem**: SSL certificate verification failed

**Solution**:
- Update certificates: `pip install --upgrade certifi`
- The system uses certifi for SSL verification

### 6. Google Play Scraper Issues

**Problem**: No PlayStore reviews fetched

**Solution**:
- Check if the app ID is correct (e.g., 'com.microsoft.familysafety')
- Verify the app exists in the specified country store
- Try different country codes in config.yaml

### 7. Memory Issues

**Problem**: System runs out of memory with large datasets

**Solution**:
- Reduce fetch limits in config.yaml
- Process data in smaller batches
- Close other applications to free memory

### 8. Configuration Issues

**Problem**: Configuration file not found or invalid

**Solution**:
- Check that `config/config.yaml` exists
- Verify YAML syntax is correct
- The system will use default settings if config file is missing

## Working Configurations

### Minimal Working Setup
```yaml
data_sources:
  playstore:
    enabled: true
    app_id: "com.microsoft.familysafety"
  
  appstore:
    enabled: true
    app_id: "1519844643"
  
  rss:
    enabled: true
  
  twitter:
    enabled: false
  
  news:
    enabled: false
```

### Maximum Compatibility
Use only these data sources for best compatibility:
- PlayStore: Most reliable
- RSS: Generally works well
- AppStore: Usually works but may have regional issues

## Getting Help

1. Check the output directory for partial results
2. Look at the console output for specific error messages
3. Try the test version first: `python test_basic.py`
4. Use the minimal version: `python main_minimal.py`
5. Check Python version compatibility (3.8-3.12 recommended)

## File Structure Verification

Ensure your project structure looks like this:
```
AppReview/
├── main_minimal.py      # Recommended entry point
├── test_basic.py        # Test functionality
├── install.py           # Installation script
├── config/
│   ├── config.yaml      # Configuration file
│   └── __init__.py      # Config loader
├── src/
│   ├── models/
│   ├── data_sources/
│   └── analysis/
└── output/              # Results will be saved here
```

## Performance Tips

1. Start with small limits (50-100 reviews per source)
2. Increase limits gradually based on performance
3. Monitor memory usage with large datasets
4. Use filtered queries to get more relevant results
5. Consider running analysis on different time periods separately
