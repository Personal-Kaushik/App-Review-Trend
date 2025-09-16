"""
Enhanced web dashboard with AI categorization display.
This module shows categorization method and confidence in the UI.
"""
import json
from flask import jsonify
from web_dashboard import app


@app.route('/api/ai-categorization-status')
def get_ai_status():
    """Get AI categorization system status."""
    try:
        from src.analysis.categorization import ReviewCategorizer
        from config import ConfigLoader
        
        # Get current product configuration
        product_name = app.config.get('current_product', 'microsoft_family_safety_ai')
        config_loader = ConfigLoader(product_name)
        categories = config_loader.get_analysis_config().get('categories', {})
        product_info = config_loader.get_product_info()
        
        # Create categorizer to check status
        categorizer = ReviewCategorizer(categories, product_info.get('name', 'Unknown'))
        status = categorizer.get_ai_categorization_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'product': product_info.get('name', 'Unknown'),
            'categories_count': len(categories)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/categorization-demo')
def get_categorization_demo():
    """Get a demonstration of AI vs keyword categorization."""
    try:
        from src.models.review import Review
        from src.analysis.categorization import ReviewCategorizer
        from config import ConfigLoader
        
        # Load configuration
        config_loader = ConfigLoader('microsoft_family_safety_ai')
        categories = config_loader.get_analysis_config().get('categories', {})
        product_info = config_loader.get_product_info()
        
        # Create categorizer
        categorizer = ReviewCategorizer(categories, product_info.get('name', 'Microsoft Family Safety'))
        
        # Demo reviews
        demo_reviews = [
            "My teenager found a way around the restrictions by changing device settings",
            "The app crashes frequently and drains battery life",
            "Setting up multiple children is confusing and unclear",
            "Approval notifications arrive too late to be useful",
            "Screen time limits don't work properly after the latest update"
        ]
        
        results = []
        for i, text in enumerate(demo_reviews):
            review = Review(id=f"demo_{i}", source="demo", text=text)
            result = categorizer.categorize_text(text)
            
            results.append({
                'text': text,
                'category': result['category'],
                'confidence': result['confidence'],
                'method': result['method'],
                'reason': result.get('reason', '')
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'ai_enabled': categorizer.use_ai,
            'categorizer_type': categorizer.get_ai_categorization_status()['categorizer_type']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


# Add AI status to the main dashboard template context
@app.context_processor
def inject_ai_status():
    """Inject AI categorization status into all templates."""
    try:
        from src.analysis.categorization import ReviewCategorizer
        from config import ConfigLoader
        
        product_name = app.config.get('current_product', 'microsoft_family_safety_ai')
        config_loader = ConfigLoader(product_name)
        categories = config_loader.get_analysis_config().get('categories', {})
        product_info = config_loader.get_product_info()
        
        categorizer = ReviewCategorizer(categories, product_info.get('name', 'Unknown'))
        status = categorizer.get_ai_categorization_status()
        
        return {
            'ai_categorization_enabled': status['ai_enabled'],
            'categorizer_type': status['categorizer_type']
        }
        
    except:
        return {
            'ai_categorization_enabled': False,
            'categorizer_type': 'Keyword Only'
        }


if __name__ == '__main__':
    print("🚀 Enhanced AI-Powered Review Analysis Dashboard")
    print("Features:")
    print("  🤖 AI categorization with confidence scores")
    print("  📊 Method tracking (AI vs keyword)")
    print("  🎯 Categorization demonstration")
    print("  ⚡ Real-time AI status monitoring")
    print()
    print("Starting dashboard at http://localhost:5000")
    app.run(debug=True, port=5000)