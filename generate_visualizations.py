"""
Standalone visualization script for creating trend analysis charts.
"""
import os
import sys
import pandas as pd
import json
from typing import Dict, Any, Optional

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def load_trend_data(output_dir: str = 'output') -> tuple:
    """
    Load trend data from exported files.
    
    Args:
        output_dir: Directory containing the trend analysis files
        
    Returns:
        Tuple of (trend_df, feature_trends) or (None, None) if files not found
    """
    monthly_csv = os.path.join(output_dir, 'monthly_negative_trends.csv')
    trend_json = os.path.join(output_dir, 'feature_trend_analysis.json')
    
    if not os.path.exists(monthly_csv):
        print(f"Monthly trends CSV not found at: {monthly_csv}")
        return None, None
    
    if not os.path.exists(trend_json):
        print(f"Feature trends JSON not found at: {trend_json}")
        return None, None
    
    # Load CSV data
    trend_df = pd.read_csv(monthly_csv)
    
    # Load JSON data
    with open(trend_json, 'r', encoding='utf-8') as f:
        trend_data = json.load(f)
    
    feature_trends = trend_data.get('feature_trends', {})
    
    return trend_df, feature_trends


def generate_visualizations_from_files(output_dir: str = 'output') -> None:
    """
    Generate visualizations from existing trend analysis files.
    
    Args:
        output_dir: Directory containing the trend analysis files
    """
    print("Loading trend analysis data...")
    
    trend_df, feature_trends = load_trend_data(output_dir)
    
    if trend_df is None or feature_trends is None:
        print("Could not load trend data. Please run trend analysis first.")
        return
    
    try:
        from src.analysis.visualization import TrendVisualizer
        
        print("Creating visualizations...")
        visualizer = TrendVisualizer(output_dir)
        
        # Generate all visualizations
        saved_plots = visualizer.generate_all_visualizations(trend_df, feature_trends)
        
        if saved_plots:
            print(f"\n✅ Successfully generated {len(saved_plots)} visualizations:")
            for plot_path in saved_plots:
                print(f"   📊 {os.path.basename(plot_path)}")
        else:
            print("❌ No visualizations were generated.")
        
        print(f"\n📁 All files saved to: {os.path.abspath(output_dir)}")
        
    except ImportError as e:
        print(f"❌ Visualization libraries not available: {e}")
        print("📦 Please install required packages:")
        print("   pip install matplotlib seaborn")
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")


def create_custom_visualization(output_dir: str = 'output', 
                              chart_type: str = 'dashboard') -> None:
    """
    Create a specific type of visualization.
    
    Args:
        output_dir: Directory containing the trend analysis files
        chart_type: Type of chart ('dashboard', 'trends', 'comparison', 'pie', 'heatmap', 'detailed')
    """
    trend_df, feature_trends = load_trend_data(output_dir)
    
    if trend_df is None or feature_trends is None:
        print("Could not load trend data.")
        return
    
    try:
        from src.analysis.visualization import TrendVisualizer
        
        visualizer = TrendVisualizer(output_dir)
        
        chart_functions = {
            'dashboard': visualizer.create_dashboard,
            'trends': visualizer.plot_monthly_trends,
            'comparison': visualizer.plot_feature_comparison_bar,
            'pie': visualizer.plot_trend_direction_pie,
            'heatmap': visualizer.plot_improvement_heatmap,
            'detailed': visualizer.plot_top_features_detailed
        }
        
        if chart_type not in chart_functions:
            print(f"Unknown chart type: {chart_type}")
            print(f"Available types: {list(chart_functions.keys())}")
            return
        
        print(f"Creating {chart_type} visualization...")
        
        if chart_type == 'dashboard':
            saved_path = chart_functions[chart_type](trend_df, feature_trends)
        elif chart_type == 'detailed':
            saved_path = chart_functions[chart_type](trend_df, feature_trends)
        else:
            if chart_type in ['trends', 'heatmap']:
                saved_path = chart_functions[chart_type](trend_df)
            else:
                saved_path = chart_functions[chart_type](feature_trends)
        
        if saved_path:
            print(f"✅ Saved: {os.path.basename(saved_path)}")
        
    except ImportError as e:
        print(f"❌ Visualization libraries not available: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function for standalone visualization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate trend analysis visualizations')
    parser.add_argument('--output-dir', '-o', default='output',
                       help='Output directory containing trend data (default: output)')
    parser.add_argument('--chart-type', '-t', 
                       choices=['dashboard', 'trends', 'comparison', 'pie', 'heatmap', 'detailed', 'all'],
                       default='all',
                       help='Type of chart to generate (default: all)')
    
    args = parser.parse_args()
    
    print("🎨 Trend Analysis Visualization Generator")
    print("=" * 50)
    
    if not os.path.exists(args.output_dir):
        print(f"❌ Output directory does not exist: {args.output_dir}")
        return
    
    if args.chart_type == 'all':
        generate_visualizations_from_files(args.output_dir)
    else:
        create_custom_visualization(args.output_dir, args.chart_type)
    
    print("\n✨ Visualization generation complete!")


if __name__ == "__main__":
    main()
