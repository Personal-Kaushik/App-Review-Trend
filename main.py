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
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        
        # Initialize analyzer
        analysis_config = self.config_loader.get_analysis_config()
        self.analyzer = ReviewAnalyzer(
            sentiment_threshold=analysis_config.get('sentiment_threshold', -0.05),
            categories=analysis_config.get('categories')
        )
        
        # Create output directory
        output_config = self.config_loader.get_output_config()
        self.output_dir = output_config.get('directory', 'output')
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
    
    def export_results(self, reviews: List[Review], report: Dict[str, Any]) -> None:
        """
        Export results to files.
        
        Args:
            reviews: List of analyzed Review objects
            report: Analysis report
        """
        print("\nExporting results...")
        
        output_config = self.config_loader.get_output_config()
        
        # Export to CSV
        csv_filename = os.path.join(self.output_dir, output_config.get('csv_filename', 'reviews_analysis.csv'))
        self.analyzer.export_to_csv(reviews, csv_filename)
        
        # Export trend analysis first (this preserves DataFrame structure)
        if 'trend_analysis' in report:
            self.analyzer.export_trend_analysis(report['trend_analysis'], self.output_dir, 
                                              generate_visualizations=True, open_in_browser=True)
        
        # Export summary to JSON (after trend analysis to avoid DataFrame serialization issues)
        summary_filename = os.path.join(self.output_dir, output_config.get('summary_filename', 'analysis_summary.json'))
        with open(summary_filename, 'w', encoding='utf-8') as f:
            # Create a serializable version of the report
            serializable_report = report.copy()
            if 'trend_analysis' in serializable_report:
                trend_data = serializable_report['trend_analysis']
                if 'monthly_data' in trend_data and hasattr(trend_data['monthly_data'], 'to_dict'):
                    trend_data['monthly_data'] = trend_data['monthly_data'].to_dict('records')
            
            json.dump(serializable_report, f, indent=2, ensure_ascii=False)
        
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
    
    def run(self, custom_queries: Optional[Dict[str, str]] = None) -> None:
        """
        Run the complete analysis pipeline with trend analysis and dashboard.
        
        Args:
            custom_queries: Custom queries for each data source
        """
        print("🚀 Starting Review Analysis System with Trend Dashboard...")
        
        # Fetch reviews
        reviews = self.fetch_all_reviews(custom_queries)
        
        if not reviews:
            print("No reviews found. Please check your configuration.")
            return
        
        # Analyze reviews
        analyzed_reviews = self.analyze_reviews(reviews)
        
        # Generate report with trend analysis
        report = self.generate_report(analyzed_reviews)
        
        # Export results (this will generate visualizations and open dashboard)
        self.export_results(analyzed_reviews, report)
        
        # Print summary
        self.print_summary(report)
        
        print("\n🎯 Analysis complete! Dashboard should be open in your browser.")
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
    """Main function - Run complete analysis with trend dashboard."""
    print("🎯 AI-Powered Review Analysis Platform")
    print("=" * 50)
    
    # Create app instance
    app = ReviewAnalysisApp()
    
    # Configure data source queries
    custom_queries = {
        'playstore': 'com.microsoft.familysafety',
        'appstore': '1519844643',
        'twitter': '"Microsoft Family Safety" OR "Family Safety app" OR "Microsoft parental controls"',
        'rss': 'Microsoft Family Safety',
        'news': 'Microsoft Family Safety issue OR complaint OR review'
    }
    
    # Run complete analysis with dashboard
    app.run(custom_queries)


if __name__ == "__main__":
    main()
