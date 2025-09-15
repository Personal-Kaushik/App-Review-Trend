"""
Main application for Review Analysis System.
"""
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add current directory to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.models.review import Review
from src.data_sources import DataSourceFactory
from src.analysis.analyzer import ReviewAnalyzer
from config import ConfigLoader


class ReviewAnalysisApp:
    """Main application class for review analysis."""
    
    def __init__(self, product_name: str = None):
        """
        Initialize the application.
        
        Args:
            product_name: Name of the product to analyze
        """
        self.product_name = product_name
        self.config_loader = ConfigLoader(product_name=product_name)
        self.config = self.config_loader.load_config()
        
        # Get product info for display
        self.product_info = self.config_loader.get_product_info()
        
        # Initialize analyzer
        analysis_config = self.config_loader.get_analysis_config()
        self.analyzer = ReviewAnalyzer(
            sentiment_threshold=analysis_config.get('sentiment_threshold', -0.05),
            categories=analysis_config.get('categories')
        )
        
        # Create output directory
        output_config = self.config_loader.get_output_config()
        self.output_dir = output_config.get('directory', 'output')
        
        # Add product name to output directory if specified
        if product_name:
            self.output_dir = os.path.join(self.output_dir, product_name.replace('_', '-'))
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_all_reviews(self, custom_queries: Optional[Dict[str, str]] = None) -> List[Review]:
        """
        Fetch reviews from all configured data sources.
        
        Args:
            custom_queries: Custom queries for each data source
            
        Returns:
            List of Review objects from all sources
        """
        # Create data sources
        data_sources = DataSourceFactory.create_all_sources(self.config.get('data_sources', {}))
        limits = self.config_loader.get_limits_config()
        
        all_reviews = []
        
        for source_name, data_source in data_sources.items():
            print(f"\nFetching reviews from {source_name}...")
            
            try:
                # Get query and limit
                query = custom_queries.get(source_name, '') if custom_queries else ''
                limit = limits.get(source_name, 100)
                
                # Fetch reviews
                reviews = data_source.fetch_reviews(query, limit)
                
                print(f"Fetched {len(reviews)} reviews from {source_name}")
                all_reviews.extend(reviews)
                
            except Exception as e:
                print(f"Error fetching from {source_name}: {e}")
                continue
        
        print(f"\nTotal reviews fetched: {len(all_reviews)}")
        return all_reviews
    
    def analyze_reviews(self, reviews: List[Review]) -> List[Review]:
        """
        Analyze reviews for sentiment and categorization.
        
        Args:
            reviews: List of Review objects
            
        Returns:
            List of analyzed Review objects
        """
        print("\nAnalyzing reviews...")
        analyzed_reviews = self.analyzer.analyze_reviews(reviews)
        print("Analysis complete!")
        return analyzed_reviews
    
    def generate_report(self, reviews: List[Review]) -> Dict[str, Any]:
        """
        Generate analysis report.
        
        Args:
            reviews: List of analyzed Review objects
            
        Returns:
            Report dictionary
        """
        print("\nGenerating report...")
        
        # Get summary
        summary = self.analyzer.get_analysis_summary(reviews)
        
        # Get top issues
        top_issues = self.analyzer.get_top_issues(reviews, 10)
        
        # Analyze monthly trends
        print("Analyzing monthly trends...")
        trend_results = self.analyzer.analyze_monthly_trends(reviews, months_back=12)
        
        # Create report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'top_issues': top_issues,
            'trend_analysis': trend_results
        }
        
        return report
    
    def export_results(self, reviews: List[Review], report: Dict[str, Any], 
                      start_web_dashboard: bool = False) -> None:
        """
        Export results to files and optionally start web dashboard.
        
        Args:
            reviews: List of analyzed Review objects
            report: Analysis report
            start_web_dashboard: Whether to start the interactive web dashboard
        """
        print("\nExporting results...")
        
        output_config = self.config_loader.get_output_config()
        
        # Export to CSV
        csv_filename = os.path.join(self.output_dir, output_config.get('csv_filename', 'reviews_analysis.csv'))
        self.analyzer.export_to_csv(reviews, csv_filename)
        
        # Export trend analysis first (this preserves DataFrame structure)
        dashboard_opened = False
        if 'trend_analysis' in report:
            dashboard_opened = self.analyzer.export_trend_analysis(
                report['trend_analysis'], 
                self.output_dir, 
                generate_visualizations=True, 
                open_in_browser=not start_web_dashboard  # Don't open static if web dashboard will start
            )
        
        # Export summary to JSON (after trend analysis to avoid DataFrame serialization issues)
        summary_filename = os.path.join(self.output_dir, output_config.get('summary_filename', 'analysis_summary.json'))
        with open(summary_filename, 'w', encoding='utf-8') as f:
            # Create a serializable version of the report
            serializable_report = report.copy()
            if 'trend_analysis' in serializable_report:
                trend_data = serializable_report['trend_analysis']
                if 'monthly_data' in trend_data and hasattr(trend_data['monthly_data'], 'to_dict'):
                    trend_data['monthly_data'] = trend_data['monthly_data'].to_dict('records')
            
            # Convert all numpy/pandas types to JSON-serializable types
            def convert_types(obj):
                import numpy as np
                if isinstance(obj, (np.integer, np.int64)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float64)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {key: convert_types(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_types(item) for item in obj]
                return obj
            
            serializable_report = convert_types(serializable_report)
            json.dump(serializable_report, f, indent=2, ensure_ascii=False)
        
        # Start interactive web dashboard if requested
        if start_web_dashboard:
            print("\n🚀 Starting interactive web dashboard...")
            try:
                from web_dashboard import create_and_run_dashboard
                print("📊 Interactive dashboard starting...")
                print("🌐 This will open your browser automatically")
                create_and_run_dashboard(self.output_dir)
            except ImportError as e:
                print(f"❌ Could not start web dashboard: {e}")
                print("📁 Static HTML dashboard available in output directory")
            except Exception as e:
                print(f"❌ Error starting web dashboard: {e}")
                print("📁 Static HTML dashboard available in output directory")
        
        print(f"Results exported to {self.output_dir}")
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """
        Print concise analysis summary to console.
        
        Args:
            report: Analysis report
        """
        summary = report['summary']
        
        print("\n" + "📊 QUICK SUMMARY")
        print("=" * 30)
        
        print(f"📝 Total Reviews: {summary['total_reviews']:,}")
        print(f"😞 Negative Reviews: {summary.get('sentiment_distribution', {}).get('Negative', 0)} ({summary['negative_review_percentage']:.1f}%)")
        
        # Show data sources
        sources = summary.get('source_distribution', {})
        active_sources = [source for source, count in sources.items() if count > 0]
        print(f"📡 Data Sources: {', '.join(active_sources)}")
        
        # Show top 3 issues
        top_issues = report.get('top_issues', [])[:3]
        if top_issues:
            print(f"\n🔥 Top Issues:")
            for i, issue in enumerate(top_issues, 1):
                print(f"   {i}. {issue['category']}: {issue['count']} reviews")
        
        print("=" * 30)
        print("🌐 Interactive dashboard opened in browser for detailed analysis!")
    
    def run(self, custom_queries: Optional[Dict[str, str]] = None, 
            interactive_dashboard: bool = False) -> None:
        """
        Run the complete analysis pipeline with trend analysis and dashboard.
        
        Args:
            custom_queries: Custom queries for each data source
            interactive_dashboard: Whether to start interactive web dashboard
        """
        dashboard_type = "Interactive Web Dashboard" if interactive_dashboard else "Static HTML Dashboard"
        product_name = self.product_info.get('name', self.product_name or 'Unknown Product')
        
        print(f"\n🚀 Starting Review Analysis for {product_name}")
        print(f"📊 Dashboard: {dashboard_type}")
        print("=" * 60)
        
        # Fetch reviews
        reviews = self.fetch_all_reviews(custom_queries)
        
        if not reviews:
            print("No reviews found. Please check your configuration.")
            return
        
        # Analyze reviews
        analyzed_reviews = self.analyze_reviews(reviews)
        
        # Generate report with trend analysis
        report = self.generate_report(analyzed_reviews)
        
        # Export results (this will generate visualizations and optionally start web dashboard)
        self.export_results(analyzed_reviews, report, start_web_dashboard=interactive_dashboard)
        
        # Print summary
        self.print_summary(report)
        
        if interactive_dashboard:
            print(f"\n🌐 Interactive web dashboard is running for {product_name}!")
            print("📊 Access your dashboard at: http://localhost:5000")
            print("⚠️  Press Ctrl+C to stop the server")
        else:
            print(f"\n🎯 Analysis complete for {product_name}! Dashboard should be open in your browser.")
        
        print(f"📁 All files saved to: {os.path.abspath(self.output_dir)}")
        
        # Show key insights
        if 'trend_analysis' in report and report['trend_analysis']['feature_trends']:
            self._print_key_insights(report['trend_analysis'])
    
    def _print_key_insights(self, trend_results: Dict[str, Any]) -> None:
        """Print key insights from the trend analysis."""
        feature_trends = trend_results['feature_trends']
        
        print("\n" + "🔍 KEY INSIGHTS" + "\n" + "="*50)
        
        # Most improved feature
        improving_features = [(f, d) for f, d in feature_trends.items() 
                            if d['trend_direction'] == 'Improving' and d['total_negative_reviews'] > 5]
        
        if improving_features:
            best_improving = min(improving_features, key=lambda x: x[1]['percentage_change'])
            print(f"✅ MOST IMPROVED: {best_improving[0]}")
            print(f"   📉 {best_improving[1]['percentage_change']:.1f}% improvement")
            print(f"   📊 {best_improving[1]['total_negative_reviews']} total negative reviews")
        
        # Most concerning feature
        worsening_features = [(f, d) for f, d in feature_trends.items() 
                            if d['trend_direction'] == 'Worsening']
        
        if worsening_features:
            worst_worsening = max(worsening_features, key=lambda x: x[1]['percentage_change'])
            print(f"\n⚠️  NEEDS ATTENTION: {worst_worsening[0]}")
            print(f"   📈 +{worst_worsening[1]['percentage_change']:.1f}% increase in negative reviews")
            print(f"   📊 {worst_worsening[1]['total_negative_reviews']} total negative reviews")
        
        # Overall trend
        improving_count = len([f for f in feature_trends.values() if f['trend_direction'] == 'Improving'])
        worsening_count = len([f for f in feature_trends.values() if f['trend_direction'] == 'Worsening'])
        
        if improving_count > worsening_count:
            print(f"\n🎉 OVERALL: More features improving ({improving_count}) than worsening ({worsening_count})")
        elif worsening_count > improving_count:
            print(f"\n🚨 OVERALL: More features worsening ({worsening_count}) than improving ({improving_count})")
        else:
            print(f"\n📊 OVERALL: Balanced trends - {improving_count} improving, {worsening_count} worsening")
        
        print("="*50)


def main():
    """Main function - Run complete analysis with product and dashboard options."""
    print("🎯 AI-Powered Review Analysis Platform")
    print("=" * 50)
    
    # Get available products
    temp_loader = ConfigLoader()
    available_products = temp_loader.get_available_products()
    
    if not available_products:
        print("❌ No product configurations found!")
        print("Please create product configuration files in the config/products/ directory.")
        return
    
    # Product selection
    print("\n📦 Available Products:")
    for i, product in enumerate(available_products, 1):
        # Get product info for display
        product_info = temp_loader.get_product_info(product)
        product_name = product_info.get('name', product.replace('_', ' ').title())
        company = product_info.get('company', 'Unknown')
        description = product_info.get('description', '')
        
        print(f"  {i}. {product_name} ({company})")
        if description:
            print(f"     {description}")
    
    # Ask user to select product
    while True:
        try:
            choice = input(f"\nSelect product (1-{len(available_products)}): ").strip()
            product_index = int(choice) - 1
            
            if 0 <= product_index < len(available_products):
                selected_product = available_products[product_index]
                break
            else:
                print(f"❌ Please enter a number between 1 and {len(available_products)}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Create app instance with selected product
    app = ReviewAnalysisApp(selected_product)
    
    # Display selected product info
    product_info = app.product_info
    if product_info:
        print(f"\n✅ Selected: {product_info.get('name', selected_product)}")
        if product_info.get('company'):
            print(f"   Company: {product_info['company']}")
        if product_info.get('description'):
            print(f"   Description: {product_info['description']}")
    
    # Configure data source queries (empty to use product config)
    custom_queries = {}
    
    # Ask user for dashboard preference
    print("\n📊 Dashboard Options:")
    print("1. Interactive Web Dashboard (localhost:5000) - Real-time, filterable")
    print("2. Static HTML Dashboard - Traditional, opens in browser")
    
    while True:
        choice = input("\nChoose dashboard type (1 for Interactive, 2 for Static, or press Enter for Interactive): ").strip()
        
        if choice == '' or choice == '1':
            interactive_dashboard = True
            print("✅ Starting with Interactive Web Dashboard")
            break
        elif choice == '2':
            interactive_dashboard = False
            print("✅ Starting with Static HTML Dashboard")
            break
        else:
            print("❌ Please enter 1, 2, or press Enter")
    
    # Run complete analysis with selected dashboard
    app.run(custom_queries, interactive_dashboard=interactive_dashboard)


if __name__ == "__main__":
    main()
