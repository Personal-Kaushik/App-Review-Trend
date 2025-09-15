"""
Feature-specific visualization module for creating individual bar charts per feature.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import os

# Set the style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class FeatureBarChartVisualizer:
    """Class for creating individual bar charts for each feature."""
    
    def __init__(self, output_dir: str = 'output'):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save plots
        """
        self.output_dir = output_dir
        self.feature_charts_dir = os.path.join(output_dir, 'feature_charts')
        os.makedirs(self.feature_charts_dir, exist_ok=True)
        
        # Configure matplotlib for better plots
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
    
    def create_feature_bar_chart(self, feature_name: str, trend_df: pd.DataFrame, 
                                save_path: Optional[str] = None) -> str:
        """
        Create a bar chart for a specific feature showing month-wise issue count.
        
        Args:
            feature_name: Name of the feature
            trend_df: DataFrame with monthly trend data
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved plot
        """
        if trend_df.empty or feature_name not in trend_df.columns:
            print(f"No data available for feature: {feature_name}")
            return ""
        
        # Get data for this feature
        months = trend_df['month_name']
        values = trend_df[feature_name]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Create bar chart with gradient colors
        bars = ax.bar(months, values, 
                     color='#667eea', 
                     alpha=0.8,
                     edgecolor='#4c63d2',
                     linewidth=1.5)
        
        # Add value labels on top of bars
        for bar, value in zip(bars, values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                       f'{int(value)}', ha='center', va='bottom', 
                       fontweight='bold', fontsize=11)
        
        # Customize the plot
        ax.set_title(f'Monthly Negative Reviews: {feature_name}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Negative Reviews', fontsize=14, fontweight='bold')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add trend line
        if len(values) > 1:
            x_numeric = range(len(values))
            z = np.polyfit(x_numeric, values, 1)
            p = np.poly1d(z)
            ax.plot(months, p(x_numeric), "--", alpha=0.8, color='red', linewidth=2,
                   label=f'Trend (slope: {z[0]:.2f})')
            ax.legend()
        
        # Style improvements
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor('#f8f9fa')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add summary statistics
        total_reviews = int(values.sum())
        avg_monthly = values.mean()
        max_month = months[values.idxmax()] if total_reviews > 0 else 'N/A'
        max_count = int(values.max())
        
        summary_text = f"""Summary Statistics:
Total Negative Reviews: {total_reviews}
Average per Month: {avg_monthly:.1f}
Peak Month: {max_month} ({max_count} reviews)"""
        
        ax.text(0.02, 0.98, summary_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            # Clean feature name for filename
            clean_name = "".join(c for c in feature_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_name = clean_name.replace(' ', '_')[:50]  # Limit filename length
            save_path = os.path.join(self.feature_charts_dir, f'{clean_name}_monthly_chart.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return save_path
    
    def create_top_features_individual_charts(self, trend_df: pd.DataFrame,
                                            feature_trends: Dict[str, Dict[str, Any]],
                                            top_n: int = 5) -> List[str]:
        """
        Create individual bar charts for the top N features.
        
        Args:
            trend_df: DataFrame with monthly trend data
            feature_trends: Feature trend analysis data
            top_n: Number of top features to create charts for
            
        Returns:
            List of paths to saved charts
        """
        if trend_df.empty or not feature_trends:
            print("No data available for creating feature charts.")
            return []
        
        # Get top features by total negative reviews
        sorted_features = sorted(
            feature_trends.items(),
            key=lambda x: x[1]['total_negative_reviews'],
            reverse=True
        )[:top_n]
        
        print(f"Creating individual bar charts for top {top_n} features...")
        
        saved_charts = []
        for i, (feature, data) in enumerate(sorted_features, 1):
            print(f"  {i}/{top_n}: Creating chart for '{feature}'...")
            chart_path = self.create_feature_bar_chart(feature, trend_df)
            if chart_path:
                saved_charts.append(chart_path)
        
        print(f"Created {len(saved_charts)} individual feature charts")
        return saved_charts
    
    def create_combined_top_features_chart(self, trend_df: pd.DataFrame,
                                         feature_trends: Dict[str, Dict[str, Any]],
                                         top_n: int = 5,
                                         save_path: Optional[str] = None) -> str:
        """
        Create a combined chart showing all top features in subplots.
        
        Args:
            trend_df: DataFrame with monthly trend data
            feature_trends: Feature trend analysis data
            top_n: Number of top features to show
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved combined chart
        """
        if trend_df.empty or not feature_trends:
            print("No data available for creating combined chart.")
            return ""
        
        # Get top features
        sorted_features = sorted(
            feature_trends.items(),
            key=lambda x: x[1]['total_negative_reviews'],
            reverse=True
        )[:top_n]
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        axes = axes.flatten()
        
        months = trend_df['month_name']
        
        for i, (feature, data) in enumerate(sorted_features):
            if i >= len(axes):
                break
                
            ax = axes[i]
            values = trend_df[feature]
            
            # Create bar chart
            bars = ax.bar(months, values, color='#667eea', alpha=0.8)
            
            # Add value labels
            for bar, value in zip(bars, values):
                if value > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                           f'{int(value)}', ha='center', va='bottom', fontsize=9)
            
            # Customize subplot
            title = feature if len(feature) <= 40 else feature[:37] + "..."
            ax.set_title(f'{title}\n(Total: {data["total_negative_reviews"]})', 
                        fontsize=12, fontweight='bold')
            ax.set_ylabel('Negative Reviews')
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add trend line
            if len(values) > 1:
                x_numeric = range(len(values))
                z = np.polyfit(x_numeric, values, 1)
                p = np.poly1d(z)
                ax.plot(months, p(x_numeric), "--", alpha=0.8, color='red', linewidth=1.5)
        
        # Remove empty subplots
        for i in range(len(sorted_features), len(axes)):
            fig.delaxes(axes[i])
        
        plt.suptitle('Top 5 Features: Monthly Negative Review Trends', 
                    fontsize=18, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Save the plot
        if save_path is None:
            save_path = os.path.join(self.output_dir, 'top_5_features_combined_chart.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return save_path
    
    def generate_all_feature_charts(self, trend_df: pd.DataFrame,
                                  feature_trends: Dict[str, Dict[str, Any]],
                                  top_n: int = 5) -> Dict[str, List[str]]:
        """
        Generate all feature-specific charts.
        
        Args:
            trend_df: DataFrame with monthly trend data
            feature_trends: Feature trend analysis data
            top_n: Number of top features to create individual charts for
            
        Returns:
            Dictionary with chart types and their file paths
        """
        print("Generating feature-specific bar charts...")
        
        results = {
            'individual_charts': [],
            'combined_chart': ''
        }
        
        try:
            # Create individual charts for top features
            individual_charts = self.create_top_features_individual_charts(
                trend_df, feature_trends, top_n)
            results['individual_charts'] = individual_charts
            
            # Create combined chart
            combined_chart = self.create_combined_top_features_chart(
                trend_df, feature_trends, top_n)
            results['combined_chart'] = combined_chart
            
            print(f"✅ Generated {len(individual_charts)} individual charts")
            print(f"✅ Generated 1 combined chart")
            
        except Exception as e:
            print(f"Error generating feature charts: {e}")
        
        return results
