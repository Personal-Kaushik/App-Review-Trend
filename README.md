# AI-Powered Review Analysis Platform

A comprehensive system for analyzing customer reviews across multiple platforms with trend analysis and interactive web dashboard.

## 🚀 Quick Start

### Option 1: Complete Analysis with Interactive Web Dashboard
```bash
python main.py
```
Choose "Interactive Web Dashboard" when prompted for real-time, filterable dashboard.

### Option 2: Launch Dashboard Only (with existing data)
```bash
python launch_dashboard.py
```

This will:
- ✅ Fetch reviews from Play Store, App Store, RSS feeds, and more
- ✅ Perform sentiment analysis and feature categorization
- ✅ Generate monthly trend analysis for the last 12 months
- ✅ Create visualizations and export data
- ✅ Launch interactive web dashboard at http://localhost:5000

## 🌐 Interactive Web Dashboard Features

### Real-Time Analytics
- **Live Filtering**: Filter by trend direction and minimum reviews
- **Interactive Charts**: Plotly-powered visualizations with zoom, pan, hover
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Feature Details**: Click on any feature for detailed analysis

### Dashboard Components
- **Statistics Overview**: Key metrics at a glance
- **Monthly Trends**: Interactive line charts showing feature trends over time
- **Feature Comparison**: Horizontal bar chart comparing problematic areas
- **Trend Distribution**: Pie chart showing improving vs worsening features
- **Monthly Heatmap**: Color-coded view of review patterns
- **Detailed Feature Table**: Sortable, clickable table with all features

### Advanced Features
- **Dynamic Filtering**: Filter features by trend direction and review count
- **Real-time Updates**: Timestamp shows last data refresh
- **Feature Details Modal**: Click any feature for comprehensive insights
- **Toast Notifications**: User-friendly success/error messages
- **Export Capabilities**: All visualizations can be exported as images

## 📊 What You Get

### Two Dashboard Options

#### 1. Interactive Web Dashboard (Recommended)
- Runs on localhost:5000
- Real-time filtering and interaction
- Modern responsive design
- Advanced charting with Plotly
- Feature detail modals
- Live data exploration

#### 2. Static HTML Dashboard (Traditional)
- Single HTML file that opens in browser
- Embedded visualizations
- Comprehensive overview
- No server required

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
