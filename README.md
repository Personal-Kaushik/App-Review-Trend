# AI-Powered Multi-Product Review Analysis Platform

A comprehensive, configurable review analysis system with Azure OpenAI-powered categorization that analyzes customer feedback from multiple sources to provide actionable insights for any product.

## ✨ Key Features

- **🤖 AI-Powered Categorization**: Uses Azure OpenAI for intelligent review categorization with keyword fallback
- **📱 Multi-Product Support**: Configurable for any product with YAML-based configuration  
- **🌐 Multiple Data Sources**: App Store, Play Store, Twitter, RSS feeds, news articles
- **📊 Interactive Dashboard**: Real-time web dashboard with product switching and visual charts
- **🎯 Smart Analysis**: Sentiment analysis, trend detection, and feature-specific insights
- **⚡ Extensible Architecture**: Clean, modular design for easy customization and extension

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI account (optional, for AI categorization)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Azure OpenAI (Optional but Recommended):**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your Azure OpenAI credentials
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Access the interactive dashboard:**
   Open http://localhost:5000 in your browser

## 🤖 Revolutionary AI Categorization System

### Why AI Categorization?
Traditional keyword-based systems fail to understand context and nuance. Our AI system:

- **🧠 Understands Context**: Grasps subtle complaints beyond simple keywords
- **📚 Learns from Examples**: Uses descriptions and examples for better accuracy  
- **🎯 Confidence Scoring**: Provides confidence levels for each categorization
- **🌍 Multilingual Support**: Handles reviews in different languages
- **⚡ Reduces Maintenance**: No need to constantly update keyword lists
- **💰 Cost-Effective**: Caching reduces API calls and costs

### How It Works
1. **Primary**: Azure OpenAI analyzes review text with category context
2. **Fallback**: Keyword matching when AI is unavailable
3. **Caching**: Results cached for 30 days to improve performance
4. **Batch Processing**: Efficient processing of multiple reviews

### Configuration Example
```yaml
categories:
  "Screen Time Management":
    description: "Issues with screen time limits, tracking, time management, and daily usage controls"
    examples:
      - "Screen time limits not working properly"
      - "Daily time limits are being ignored by the app"
      - "Time tracking shows incorrect usage data"
    keywords: ["screen time", "time limit", "daily limit"]  # Fallback
```

## 📋 Supported Products

- **🛡️ Microsoft Family Safety** (`microsoft_family_safety_ai`)
- **💬 WhatsApp** (`whatsapp_ai`)  
- **📧 Microsoft Outlook** (`microsoft_outlook`)
- **🔧 Custom Products**: Easy to add via YAML configuration

## 🔬 Testing AI Categorization

Test the system with sample data:

```bash
python test_ai_categorization.py
```

This shows:
- ✅ Configuration format validation
- 🤖 AI vs keyword categorization comparison  
- 📊 Confidence scores and methods
- 📈 Category distribution analysis

## 🌐 Interactive Web Dashboard

### Real-Time Analytics
- **🔄 Product Switching**: Toggle between configured products instantly
- **📊 Live Charts**: Plotly-powered visualizations with zoom, pan, hover
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🎯 Feature Details**: Click features for detailed AI insights

### Dashboard Components
- **📈 Monthly Trends**: Time-series analysis with trend detection
- **🥧 Category Distribution**: Interactive pie charts by sentiment
- **📋 Feature Table**: Sortable table with confidence scores
- **⚡ Real-time Filtering**: Dynamic data exploration
- **💾 Export Options**: CSV downloads and image exports

## 🏗️ Architecture

```
src/
├── analysis/
│   ├── ai_categorization.py    # 🤖 Azure OpenAI integration
│   ├── categorization.py       # 🔧 Enhanced categorizer with AI
│   ├── sentiment.py           # 😊 Sentiment analysis  
│   └── analyzer.py            # 🎯 Main analysis orchestrator
├── data_sources/              # 📡 Data collection modules
├── models/                    # 📊 Enhanced data models
└── web_dashboard.py          # 🌐 Interactive dashboard

config/
├── products/                  # 📱 Product configurations
│   ├── microsoft_family_safety_ai.yaml
│   ├── whatsapp_ai.yaml
│   └── [your_product]_ai.yaml
└── base_config.yaml          # ⚙️ Base configuration
```

## ⚙️ Environment Configuration

```bash
# Azure OpenAI (Required for AI categorization)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# AI Settings (Optional - defaults provided)
AI_CATEGORIZATION_ENABLED=true
AI_CACHE_ENABLED=true
AI_CONFIDENCE_THRESHOLD=0.75
AI_BATCH_SIZE=5
```

## 🎯 Usage Examples

### Basic Analysis
```python
from src.analysis.analyzer import ReviewAnalyzer

# Initialize with AI support
analyzer = ReviewAnalyzer(
    categories=ai_categories,
    product_name="Your Product"
)

# Analyze reviews with AI
analyzed_reviews = analyzer.analyze_reviews(reviews)
```

### Custom Product Setup
1. **Create configuration**: `config/products/your_product_ai.yaml`
2. **Define AI categories** with descriptions and examples
3. **Configure data sources** and search terms
4. **Run analysis**: `python main.py`
5. **View dashboard**: http://localhost:5000

## 📊 AI Analysis Benefits

### Before (Keyword-Only)
❌ Misses context and nuance  
❌ Requires constant keyword maintenance  
❌ Limited accuracy for complex complaints  
❌ No confidence scoring  

### After (AI-Powered)
✅ Understands context and intent  
✅ Self-improving with examples  
✅ High accuracy for nuanced feedback  
✅ Confidence scores for reliability  
✅ Handles multiple languages  
✅ Reduces manual configuration  

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-ai-feature`
3. **Add** your product configuration or AI enhancement
4. **Test** with: `python test_ai_categorization.py`
5. **Commit**: `git commit -m 'Add amazing AI feature'`
6. **Push**: `git push origin feature/amazing-ai-feature`
7. **Create** Pull Request

## 🆘 Support & Troubleshooting

### Quick Checks
1. **Run test script**: `python test_ai_categorization.py`
2. **Check configuration**: Validate YAML syntax
3. **Verify environment**: Ensure Azure OpenAI credentials
4. **Review logs**: Check console for error messages

### Common Issues
- **AI not working**: Check Azure OpenAI credentials and deployment
- **Poor categorization**: Add more examples to category definitions
- **Slow performance**: Enable caching and reduce batch size
- **Memory issues**: Process reviews in smaller batches

## 📝 License

This project is licensed under the MIT License.

---

**🚀 Built with AI-first approach for the future of customer feedback analysis**
