# AI-Powered Review Analysis Platform

A comprehensive system for analyzing customer reviews across multiple platforms with trend analysis and interactive dashboard.

## 🚀 Quick Start

Simply run the main script to get a complete analysis with interactive dashboard:

```bash
python main.py
```

This will:
- ✅ Fetch reviews from Play Store, App Store, RSS feeds, and more
- ✅ Perform sentiment analysis and feature categorization
- ✅ Generate monthly trend analysis for the last 12 months
- ✅ Create visualizations and export data
- ✅ Open an interactive HTML dashboard in your browser automatically

## 📊 What You Get

### Interactive Dashboard
- **Monthly Trends**: Line charts showing negative review trends by feature
- **Feature Comparison**: Bar charts comparing problematic areas
- **Trend Analysis**: Identify improving vs worsening features
- **Key Insights**: Automatically highlighted important findings

### Exported Files
- `trend_analysis_dashboard.html` - Interactive web dashboard
- `monthly_negative_trends.csv` - Monthly data by feature
- `feature_trend_analysis.json` - Detailed trend analysis
- `reviews_analysis.csv` - All analyzed reviews
- Various visualization images (PNG files)

## 🛠️ Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the analysis:
```bash
python main.py
```

## 📈 Key Features

- **Multi-Platform Data**: Play Store, App Store, RSS feeds, Twitter, News
- **Smart Categorization**: Automatically categorizes reviews into 25+ feature areas
- **Trend Analysis**: Month-over-month tracking of negative reviews by feature
- **Sentiment Analysis**: Identifies positive, negative, and neutral reviews
- **Interactive Dashboard**: Beautiful HTML dashboard that opens automatically
- **Export Options**: CSV, JSON, and visualization files

## 🎯 Feature Categories

The system categorizes reviews into areas like:
- Screen Time Management
- App Performance & Reliability
- Device Management
- App Blocking & Restrictions
- Login & Account Issues
- And 20+ more categories

## 📊 Trend Analysis

- **Improving Features**: Features with decreasing negative reviews
- **Worsening Features**: Features needing attention
- **Stable Features**: Features with consistent feedback
- **Monthly Breakdown**: Detailed month-by-month analysis

## 🌐 Dashboard Features

- Overview statistics and key metrics
- Top problematic features with trend indicators
- Most improved features over time
- Features needing attention
- Monthly breakdown table
- Embedded visualizations
- Responsive design for all devices

## 🔧 Configuration

Edit `config/config.yaml` to:
- Add new data sources
- Modify feature categories
- Adjust analysis parameters
- Configure output options

## 📝 Output Structure

```
output/
├── trend_analysis_dashboard.html      # Interactive dashboard
├── monthly_negative_trends.csv        # Monthly data
├── feature_trend_analysis.json        # Trend analysis
├── reviews_analysis.csv               # All reviews
├── analysis_summary.json              # Summary data
└── *.png                              # Visualization files
```

The dashboard will automatically open in your default browser when the analysis completes.

## 🤖 AI-Powered Analysis

- Intelligent review categorization using keyword matching
- Sentiment analysis to identify customer satisfaction
- Trend detection to spot improving/worsening areas
- Automated insights and recommendations
- Smart data aggregation across multiple sources
