"""
Trend analysis module for tracking feature-based negative reviews over time.
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import calendar

from src.models.review import Review


def convert_for_json(obj):
    """Convert numpy/pandas types to Python native types for JSON serialization."""
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_json(item) for item in obj]
    return obj


class TrendAnalyzer:
    """Analyzer for tracking trends in negative reviews by feature over time."""
    
    def __init__(self):
        """Initialize the trend analyzer."""
        pass
    
    def get_monthly_negative_trends(self, reviews: List[Review], 
                                  months_back: int = 12,
                                  negative_threshold: float = 3.0) -> pd.DataFrame:
        """
        Get monthly trends of negative reviews by feature.
        
        Args:
            reviews: List of analyzed Review objects
            months_back: Number of months to look back from current date
            negative_threshold: Rating threshold for considering a review negative
            
        Returns:
            DataFrame with monthly negative review counts by feature
        """
        # Filter to last N months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Filter reviews to date range and negative sentiment/rating
        filtered_reviews = []
        for review in reviews:
            if not review.date:
                continue
            
            # Check if within date range
            if review.date < start_date or review.date > end_date:
                continue
            
            # Check if negative (either by sentiment or rating)
            is_negative = (
                review.sentiment == 'Negative' or 
                (review.rating and review.rating <= negative_threshold)
            )
            
            if is_negative and review.category:
                filtered_reviews.append(review)
        
        # Group by month and feature
        monthly_data = defaultdict(lambda: defaultdict(int))
        
        for review in filtered_reviews:
            month_key = review.date.strftime('%Y-%m')
            feature = review.category
            monthly_data[month_key][feature] += 1
        
        # Create DataFrame
        if not monthly_data:
            return pd.DataFrame()
        
        # Get all unique features
        all_features = set()
        for month_data in monthly_data.values():
            all_features.update(month_data.keys())
        
        # Create rows for DataFrame
        rows = []
        for month_key in sorted(monthly_data.keys()):
            row = {'month': month_key}
            for feature in sorted(all_features):
                row[feature] = monthly_data[month_key].get(feature, 0)
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Add month name and sort
        if not df.empty:
            df['month_name'] = df['month'].apply(
                lambda x: datetime.strptime(x, '%Y-%m').strftime('%B %Y')
            )
            df = df.sort_values('month').reset_index(drop=True)
        
        return df
    
    def calculate_feature_improvement_trends(self, trend_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Calculate improvement/degradation trends for each feature.
        
        Args:
            trend_df: DataFrame from get_monthly_negative_trends
            
        Returns:
            Dictionary with trend analysis for each feature
        """
        if trend_df.empty:
            return {}
        
        feature_trends = {}
        feature_columns = [col for col in trend_df.columns if col not in ['month', 'month_name']]
        
        for feature in feature_columns:
            values = trend_df[feature].values
            
            # Calculate trend metrics
            total_negative = values.sum()
            avg_monthly = values.mean()
            
            # Calculate trend direction (linear regression slope)
            x = range(len(values))
            if len(values) > 1:
                # Simple linear regression
                n = len(values)
                sum_x = sum(x)
                sum_y = sum(values)
                sum_xy = sum(xi * yi for xi, yi in zip(x, values))
                sum_x2 = sum(xi * xi for xi in x)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                # Determine trend
                if slope > 0.1:
                    trend = "Worsening"
                elif slope < -0.1:
                    trend = "Improving"
                else:
                    trend = "Stable"
            else:
                slope = 0
                trend = "Insufficient Data"
            
            # Calculate percentage change (first 3 months vs last 3 months)
            first_half = values[:len(values)//2].mean() if len(values) > 3 else values[0] if len(values) > 0 else 0
            second_half = values[len(values)//2:].mean() if len(values) > 3 else values[-1] if len(values) > 0 else 0
            
            if first_half > 0:
                percentage_change = ((second_half - first_half) / first_half) * 100
            else:
                percentage_change = 0 if second_half == 0 else 100
            
            feature_trends[feature] = {
                'total_negative_reviews': int(total_negative),
                'avg_monthly_negative': round(avg_monthly, 2),
                'trend_direction': trend,
                'slope': round(slope, 3),
                'percentage_change': round(percentage_change, 2),
                'recent_months_avg': round(second_half, 2),
                'early_months_avg': round(first_half, 2),
                'highest_month': trend_df.loc[trend_df[feature].idxmax(), 'month_name'] if total_negative > 0 else None,
                'highest_count': int(values.max()),
                'lowest_count': int(values.min())
            }
        
        return feature_trends
    
    def export_trend_analysis(self, trend_df: pd.DataFrame, 
                             feature_trends: Dict[str, Dict[str, Any]], 
                             output_dir: str = 'output',
                             generate_visualizations: bool = True,
                             open_in_browser: bool = True) -> None:
        """
        Export trend analysis to files and optionally generate visualizations.
        
        Args:
            trend_df: Monthly trends DataFrame
            feature_trends: Feature trend analysis
            output_dir: Output directory
            generate_visualizations: Whether to generate visualization plots
            open_in_browser: Whether to open HTML dashboard in browser
        """
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Export monthly data to CSV
        monthly_csv = os.path.join(output_dir, 'monthly_negative_trends.csv')
        trend_df.to_csv(monthly_csv, index=False)
        
        # Export trend analysis to JSON
        trend_json = os.path.join(output_dir, 'feature_trend_analysis.json')
        with open(trend_json, 'w', encoding='utf-8') as f:
            data_to_export = {
                'analysis_date': datetime.now().isoformat(),
                'feature_trends': feature_trends,
                'summary': {
                    'total_features_analyzed': len(feature_trends),
                    'improving_features': len([f for f in feature_trends.values() if f['trend_direction'] == 'Improving']),
                    'worsening_features': len([f for f in feature_trends.values() if f['trend_direction'] == 'Worsening']),
                    'stable_features': len([f for f in feature_trends.values() if f['trend_direction'] == 'Stable'])
                }
            }
            # Convert all numpy/pandas types to JSON-serializable types
            serializable_data = convert_for_json(data_to_export)
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        # Generate visualizations if requested
        saved_plots = []
        feature_chart_results = {}
        if generate_visualizations:
            try:
                from src.analysis.feature_charts import FeatureBarChartVisualizer
                
                # Generate feature-specific bar charts only
                print("Generating feature-specific bar charts...")
                feature_visualizer = FeatureBarChartVisualizer(output_dir)
                feature_chart_results = feature_visualizer.generate_all_feature_charts(
                    trend_df, feature_trends, top_n=5)
                
                if feature_chart_results['individual_charts']:
                    print(f"Generated {len(feature_chart_results['individual_charts'])} individual feature charts")
                else:
                    print("No visualizations were generated.")
                    
            except ImportError as e:
                print(f"Visualization libraries not available: {e}")
                print("Install matplotlib and seaborn to generate visualizations.")
            except Exception as e:
                print(f"Error generating visualizations: {e}")
                import traceback
                traceback.print_exc()
        
        # Generate HTML dashboard
        try:
            from src.analysis.html_dashboard import HTMLDashboardGenerator
            
            print("Generating HTML dashboard...")
            html_generator = HTMLDashboardGenerator(output_dir)
            html_path = html_generator.generate_html_dashboard(trend_df, feature_trends, saved_plots)
            
            if html_path:
                print(f"✅ HTML dashboard generated: {os.path.basename(html_path)}")
                
                # Open in browser if requested
                if open_in_browser:
                    html_generator.open_in_browser(html_path)
            
        except ImportError as e:
            print(f"HTML dashboard generator not available: {e}")
        except Exception as e:
            print(f"Error generating HTML dashboard: {e}")
        
        print(f"Trend analysis exported to {output_dir}")
    
    def print_trend_summary(self, feature_trends: Dict[str, Dict[str, Any]]) -> None:
        """
        Print a summary of trend analysis to console.
        
        Args:
            feature_trends: Feature trend analysis dictionary
        """
        print("\n" + "="*80)
        print("FEATURE TREND ANALYSIS SUMMARY")
        print("="*80)
        
        if not feature_trends:
            print("No trend data available.")
            return
        
        # Sort features by total negative reviews
        sorted_features = sorted(
            feature_trends.items(), 
            key=lambda x: x[1]['total_negative_reviews'], 
            reverse=True
        )
        
        print(f"Analysis covers {len(feature_trends)} features")
        print()
        
        # Show top problematic features
        print("TOP FEATURES BY NEGATIVE REVIEWS:")
        for i, (feature, data) in enumerate(sorted_features[:10], 1):
            trend_icon = "📈" if data['trend_direction'] == "Worsening" else "📉" if data['trend_direction'] == "Improving" else "📊"
            print(f"{i:2d}. {feature} {trend_icon}")
            print(f"     Total: {data['total_negative_reviews']} | "
                  f"Monthly Avg: {data['avg_monthly_negative']} | "
                  f"Trend: {data['trend_direction']} ({data['percentage_change']:+.1f}%)")
        
        print()
        
        # Show improvement/degradation summary
        improving = [f for f, data in feature_trends.items() if data['trend_direction'] == 'Improving']
        worsening = [f for f, data in feature_trends.items() if data['trend_direction'] == 'Worsening']
        stable = [f for f, data in feature_trends.items() if data['trend_direction'] == 'Stable']
        
        print("TREND SUMMARY:")
        print(f"📉 Improving Features ({len(improving)}): {', '.join(improving[:5])}")
        if len(improving) > 5:
            print(f"    ... and {len(improving) - 5} more")
        
        print(f"📈 Worsening Features ({len(worsening)}): {', '.join(worsening[:5])}")
        if len(worsening) > 5:
            print(f"    ... and {len(worsening) - 5} more")
        
        print(f"📊 Stable Features ({len(stable)}): {', '.join(stable[:5])}")
        if len(stable) > 5:
            print(f"    ... and {len(stable) - 5} more")
        
        print("="*80)
    
    def get_feature_monthly_comparison(self, trend_df: pd.DataFrame, 
                                     feature_name: str) -> Dict[str, Any]:
        """
        Get detailed monthly comparison for a specific feature.
        
        Args:
            trend_df: Monthly trends DataFrame
            feature_name: Name of the feature to analyze
            
        Returns:
            Dictionary with detailed monthly data for the feature
        """
        if trend_df.empty or feature_name not in trend_df.columns:
            return {}
        
        monthly_data = []
        for _, row in trend_df.iterrows():
            monthly_data.append({
                'month': row['month'],
                'month_name': row['month_name'],
                'negative_count': row[feature_name]
            })
        
        return {
            'feature': feature_name,
            'monthly_data': monthly_data,
            'total_negative': trend_df[feature_name].sum(),
            'peak_month': trend_df.loc[trend_df[feature_name].idxmax(), 'month_name'],
            'peak_count': trend_df[feature_name].max(),
            'lowest_month': trend_df.loc[trend_df[feature_name].idxmin(), 'month_name'],
            'lowest_count': trend_df[feature_name].min()
        }
