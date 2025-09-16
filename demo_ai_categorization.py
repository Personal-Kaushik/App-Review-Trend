#!/usr/bin/env python3
"""
Demonstration script showing the power of AI categorization vs keywords.
"""
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.models.review import Review
from src.analysis.categorization import ReviewCategorizer


def demonstrate_ai_vs_keywords():
    """Demonstrate the difference between AI and keyword categorization."""
    print("🎯 AI vs Keyword Categorization Demonstration")
    print("=" * 60)
    print()
    
    # Load enhanced configuration
    from config import ConfigLoader
    config_loader = ConfigLoader("microsoft_family_safety_ai")
    categories = config_loader.get_analysis_config().get('categories', {})
    
    # Create categorizer
    categorizer = ReviewCategorizer(categories, "Microsoft Family Safety")
    
    # Complex reviews that showcase AI advantages
    complex_reviews = [
        {
            "text": "My teenager cleverly found a way around the time restrictions by changing the device clock. The app doesn't seem to validate against network time.",
            "expected_ai": "Bypass & Security Issues",
            "expected_keyword": "Others"
        },
        {
            "text": "The application consumes excessive battery power and makes my phone run hot during normal usage throughout the day.",
            "expected_ai": "App Performance Issues", 
            "expected_keyword": "Others"
        },
        {
            "text": "Setting up multiple children with different age-appropriate restrictions is confusing and the interface doesn't make it clear which child you're configuring.",
            "expected_ai": "Account Management",
            "expected_keyword": "Others"
        },
        {
            "text": "The parental approval notifications arrive hours late, making it impossible to respond to my child's requests in a timely manner.",
            "expected_ai": "Approval & Permissions",
            "expected_keyword": "Others"
        },
        {
            "text": "Despite enabling content filters, my child still encounters inappropriate material when browsing educational websites.",
            "expected_ai": "Web Filtering & Safe Browsing",
            "expected_keyword": "Web Filtering & Safe Browsing"
        },
        {
            "text": "The daily usage reports show conflicting numbers compared to what I observe, making it hard to trust the monitoring features.",
            "expected_ai": "App Usage & Monitoring",
            "expected_keyword": "App Usage & Monitoring"
        }
    ]
    
    print("🧠 Testing Complex Reviews (AI excels here)")
    print("─" * 60)
    
    results = []
    for i, review_data in enumerate(complex_reviews, 1):
        review = Review(
            id=f"demo_{i}",
            source="demo",
            text=review_data["text"],
            sentiment="Negative"
        )
        
        # Categorize with current system
        result = categorizer.categorize_text(review.text)
        
        print(f"\n📝 Review {i}:")
        print(f"Text: {review.text}")
        print(f"─" * 40)
        
        if categorizer.use_ai:
            print(f"🤖 AI Result: {result['category']} (confidence: {result['confidence']:.2f})")
            ai_correct = result['category'] == review_data['expected_ai']
            print(f"   {'✅ Correct' if ai_correct else '❌ Incorrect'} - Expected: {review_data['expected_ai']}")
        else:
            print(f"🔤 Keyword Result: {result['category']}")
            keyword_correct = result['category'] == review_data['expected_keyword']
            print(f"   {'✅ Correct' if keyword_correct else '❌ Incorrect'} - Expected: {review_data['expected_keyword']}")
            print(f"🤖 AI Would Predict: {review_data['expected_ai']}")
        
        results.append({
            'review': review_data,
            'actual': result,
            'ai_would_be_correct': result['category'] == review_data['expected_ai'] if categorizer.use_ai else False,
            'keyword_correct': result['category'] == review_data['expected_keyword']
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Categorization Analysis Summary")
    print("=" * 60)
    
    if categorizer.use_ai:
        ai_correct = sum(1 for r in results if r['ai_would_be_correct'])
        print(f"🤖 AI Accuracy: {ai_correct}/{len(results)} ({ai_correct/len(results)*100:.1f}%)")
    else:
        keyword_correct = sum(1 for r in results if r['keyword_correct'])
        ai_would_correct = sum(1 for r in results if r['review']['expected_ai'] != 'Others')
        
        print(f"🔤 Keyword Accuracy: {keyword_correct}/{len(results)} ({keyword_correct/len(results)*100:.1f}%)")
        print(f"🤖 AI Would Achieve: {ai_would_correct}/{len(results)} ({ai_would_correct/len(results)*100:.1f}%)")
        
        print(f"\n💡 AI Advantage Examples:")
        for i, r in enumerate(results, 1):
            if r['review']['expected_ai'] != r['review']['expected_keyword']:
                print(f"   {i}. Would correctly identify '{r['review']['expected_ai']}' instead of '{r['actual']['category']}'")
    
    return results


def show_ai_benefits():
    """Show the key benefits of AI categorization."""
    print("\n🚀 Key Benefits of AI Categorization")
    print("=" * 60)
    
    benefits = [
        ("🧠 Context Understanding", "Understands nuanced complaints beyond simple keywords"),
        ("🎯 Higher Accuracy", "Better categorization of complex, multi-faceted reviews"),
        ("🌍 Language Flexibility", "Can handle different phrasings and languages"),
        ("📈 Confidence Scoring", "Provides reliability metrics for each categorization"),
        ("🔧 Less Maintenance", "No need to constantly update keyword lists"),
        ("📚 Learning from Examples", "Improves accuracy using category descriptions"),
        ("⚡ Batch Processing", "Efficient processing of multiple reviews"),
        ("💰 Cost-Effective Caching", "Caches results to minimize API costs")
    ]
    
    for benefit, description in benefits:
        print(f"{benefit}: {description}")
    
    print(f"\n💭 Without AI: Limited to exact keyword matches")
    print(f"🤖 With AI: Understands intent, context, and nuance")


def main():
    """Main demonstration function."""
    print("🎭 AI Categorization Demonstration")
    print("This script shows why AI categorization is superior to keyword matching")
    print()
    
    # Run demonstration
    results = demonstrate_ai_vs_keywords()
    
    # Show benefits
    show_ai_benefits()
    
    print(f"\n🔧 Setup Instructions:")
    print(f"1. Get Azure OpenAI service access")
    print(f"2. Copy .env.example to .env") 
    print(f"3. Add your Azure OpenAI credentials")
    print(f"4. Re-run this demo to see AI in action!")
    
    print(f"\n🏃‍♂️ Quick Test: python test_ai_categorization.py")


if __name__ == "__main__":
    main()