"""
Visualization module for trend analysis and review data.
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


class TrendVisualizer:
    """Class for creating visualizations of trend analysis data."""
    
    def __init__(self, output_dir: str = 'output'):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save plots
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure matplotlib for better plots
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
    
    def plot_monthly_trends(self, trend_df: pd.DataFrame, 
                           top_features: int = 8,
                           save_path: Optional[str] = None) -> str:
        """
        Create a line plot showing monthly trends for top features.
        
        Args:
            trend_df: DataFrame with monthly trend data
            top_features: Number of top features to display
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved plot
        """
        if trend_df.empty:
            print("No data available for plotting monthly trends.")
            return ""
        
        # Get top features by total negative reviews
        feature_cols = [col for col in trend_df.columns if col not in ['month', 'month_name']]
        totals = {col: trend_df[col].sum() for col in feature_cols}
        top_feature_names = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:top_features]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot lines for each top feature
        for feature, total in top_feature_names:
            if total > 0:  # Only plot features with data
                ax.plot(trend_df['month_name'], trend_df[feature], 
                       marker='o', linewidth=2.5, label=f'{feature} (Total: {total})')
        
        ax.set_title('Monthly Negative Review Trends by Feature', fontsize=16, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Number of Negative Reviews', fontsize=12)
        
        # Improve x-axis labels
        ax.tick_params(axis='x', rotation=45)
        
        # Add legend
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Add grid and styling
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            save_path = os.path.join(self.output_dir, 'monthly_trends.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_feature_comparison_bar(self, feature_trends: Dict[str, Dict[str, Any]],
                                   top_n: int = 15,
                                   save_path: Optional[str] = None) -> str:
        """
        Create a horizontal bar chart comparing features by total negative reviews.
        
        Args:
            feature_trends: Feature trend analysis data
            top_n: Number of features to show
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved plot
        """
        if not feature_trends:
            print("No feature trend data available for plotting.")
            return ""
        
        # Prepare data
        features = []
        totals = []
        trends = []
        
        sorted_features = sorted(
            feature_trends.items(),
            key=lambda x: x[1]['total_negative_reviews'],
            reverse=True
        )[:top_n]
        
        for feature, data in sorted_features:
            features.append(feature)
            totals.append(data['total_negative_reviews'])
            trends.append(data['trend_direction'])
        
        # Create color map based on trend direction
        colors = []
        for trend in trends:
            if trend == 'Improving':
                colors.append('#28a745')  # Green
            elif trend == 'Worsening':
                colors.append('#dc3545')  # Red
            else:
                colors.append('#6c757d')  # Gray
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.barh(features, totals, color=colors, alpha=0.8)
        
        # Add value labels on bars
        for i, (bar, total) in enumerate(zip(bars, totals)):
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{total}', ha='left', va='center', fontweight='bold')
        
        ax.set_title('Total Negative Reviews by Feature', fontsize=16, fontweight='bold')
        ax.set_xlabel('Number of Negative Reviews', fontsize=12)
        ax.set_ylabel('Features', fontsize=12)
        
        # Add legend for colors
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#28a745', label='Improving'),
            Patch(facecolor='#dc3545', label='Worsening'),
            Patch(facecolor='#6c757d', label='Stable')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        # Styling
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_facecolor('#f8f9fa')
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            save_path = os.path.join(self.output_dir, 'feature_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_trend_direction_pie(self, feature_trends: Dict[str, Dict[str, Any]],
                                save_path: Optional[str] = None) -> str:
        """
        Create a pie chart showing the distribution of trend directions.
        
        Args:
            feature_trends: Feature trend analysis data
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved plot
        """
        if not feature_trends:
            print("No feature trend data available for plotting.")
            return ""
        
        # Count trend directions
        trend_counts = {'Improving': 0, 'Worsening': 0, 'Stable': 0, 'Insufficient Data': 0}
        
        for feature, data in feature_trends.items():
            trend = data['trend_direction']
            trend_counts[trend] = trend_counts.get(trend, 0) + 1
        
        # Filter out categories with zero counts
        trend_counts = {k: v for k, v in trend_counts.items() if v > 0}
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = {'Improving': '#28a745', 'Worsening': '#dc3545', 
                 'Stable': '#6c757d', 'Insufficient Data': '#ffc107'}
        
        wedges, texts, autotexts = ax.pie(
            trend_counts.values(),
            labels=trend_counts.keys(),
            colors=[colors.get(k, '#6c757d') for k in trend_counts.keys()],
            autopct='%1.1f%%',
            startangle=90,
            explode=[0.05 if k == 'Worsening' else 0 for k in trend_counts.keys()]
        )
        
        ax.set_title('Feature Trend Direction Distribution', fontsize=16, fontweight='bold')
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            save_path = os.path.join(self.output_dir, 'trend_direction_pie.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_improvement_heatmap(self, trend_df: pd.DataFrame,
                                save_path: Optional[str] = None) -> str:
        """
        Create a heatmap showing monthly negative review counts by feature.
        
        Args:
            trend_df: DataFrame with monthly trend data
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved plot
        """
        if trend_df.empty:
            print("No data available for plotting heatmap.")
            return ""
        
        # Prepare data for heatmap
        feature_cols = [col for col in trend_df.columns if col not in ['month', 'month_name']]
        
        # Select top features to avoid cluttered heatmap
        totals = {col: trend_df[col].sum() for col in feature_cols}
        top_features = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:12]
        selected_features = [f[0] for f in top_features if f[1] > 0]
        
        if not selected_features:
            print("No features with data for heatmap.")
            return ""
        
        # Create heatmap data
        heatmap_data = trend_df[['month_name'] + selected_features].set_index('month_name')
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sns.heatmap(heatmap_data.T, annot=True, cmap='Reds', fmt='d', 
                   cbar_kws={'label': 'Negative Reviews'}, ax=ax)
        
        ax.set_title('Monthly Negative Reviews Heatmap by Feature', fontsize=16, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Features', fontsize=12)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            save_path = os.path.join(self.output_dir, 'monthly_heatmap.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_top_features_detailed(self, trend_df: pd.DataFrame,
                                  feature_trends: Dict[str, Dict[str, Any]],
                                  top_n: int = 6,
                                  save_path: Optional[str] = None) -> str:
        """
        Create a detailed subplot showing trends for top features.
        
        Args:
            trend_df: DataFrame with monthly trend data
            feature_trends: Feature trend analysis data
            top_n: Number of top features to show
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved plot
        """
        if trend_df.empty or not feature_trends:
            print("No data available for detailed feature plots.")
            return ""
        
        # Get top features
        sorted_features = sorted(
            feature_trends.items(),
            key=lambda x: x[1]['total_negative_reviews'],
            reverse=True
        )[:top_n]
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, (feature, data) in enumerate(sorted_features):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            # Plot the trend line
            values = trend_df[feature].values
            months = trend_df['month_name'].values
            
            ax.plot(months, values, marker='o', linewidth=2.5, color='#1f77b4')
            ax.fill_between(months, values, alpha=0.3, color='#1f77b4')
            
            # Styling
            ax.set_title(f'{feature}\n({data["trend_direction"]}, {data["percentage_change"]:+.1f}%)',
                        fontsize=12, fontweight='bold')
            ax.set_ylabel('Negative Reviews')
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Add trend line
            x_numeric = range(len(values))
            z = np.polyfit(x_numeric, values, 1)
            p = np.poly1d(z)
            ax.plot(months, p(x_numeric), "--", alpha=0.8, color='red')
        
        # Remove empty subplots
        for i in range(len(sorted_features), len(axes)):
            fig.delaxes(axes[i])
        
        plt.suptitle('Detailed Monthly Trends for Top Features', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            save_path = os.path.join(self.output_dir, 'top_features_detailed.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_dashboard(self, trend_df: pd.DataFrame,
                        feature_trends: Dict[str, Dict[str, Any]],
                        save_path: Optional[str] = None) -> str:
        """
        Create a comprehensive dashboard with multiple visualizations.
        
        Args:
            trend_df: DataFrame with monthly trend data
            feature_trends: Feature trend analysis data
            save_path: Custom save path (optional)
            
        Returns:
            Path to saved dashboard
        """
        if trend_df.empty or not feature_trends:
            print("No data available for creating dashboard.")
            return ""
        
        try:
            # Create a large figure with subplots
            fig = plt.figure(figsize=(20, 16))
            
            # 1. Monthly trends (top left)
            ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
            
            # Get top 6 features for line plot
            feature_cols = [col for col in trend_df.columns if col not in ['month', 'month_name']]
            totals = {col: trend_df[col].sum() for col in feature_cols}
            top_features = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:6]
            
            for feature, total in top_features:
                if total > 0:
                    ax1.plot(trend_df['month_name'], trend_df[feature], 
                            marker='o', linewidth=2, label=f'{feature[:15]}...' if len(feature) > 15 else feature)
            
            ax1.set_title('Monthly Negative Review Trends', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Negative Reviews')
            ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # 2. Feature comparison bar (top right)
            ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
            
            top_10_features = sorted(
                feature_trends.items(),
                key=lambda x: x[1]['total_negative_reviews'],
                reverse=True
            )[:10]
            
            features = [f[0][:20] + '...' if len(f[0]) > 20 else f[0] for f, _ in top_10_features]
            totals_list = [data['total_negative_reviews'] for _, data in top_10_features]
            colors = ['#dc3545' if data['trend_direction'] == 'Worsening' 
                     else '#28a745' if data['trend_direction'] == 'Improving' 
                     else '#6c757d' for _, data in top_10_features]
            
            bars = ax2.barh(features, totals_list, color=colors, alpha=0.8)
            ax2.set_title('Top Features by Total Negative Reviews', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Total Negative Reviews')
            
            # 3. Trend direction pie (bottom left)
            ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2)
            
            trend_counts = {'Improving': 0, 'Worsening': 0, 'Stable': 0}
            for feature, data in feature_trends.items():
                trend = data['trend_direction']
                if trend in trend_counts:
                    trend_counts[trend] += 1
            
            # Filter out zero counts
            trend_counts = {k: v for k, v in trend_counts.items() if v > 0}
            colors_pie = {'Improving': '#28a745', 'Worsening': '#dc3545', 'Stable': '#6c757d'}
            
            if trend_counts:  # Only create pie chart if there's data
                ax3.pie(trend_counts.values(), labels=trend_counts.keys(),
                       colors=[colors_pie.get(k, '#6c757d') for k in trend_counts.keys()],
                       autopct='%1.1f%%', startangle=90)
                ax3.set_title('Trend Direction Distribution', fontsize=14, fontweight='bold')
            
            # 4. Summary statistics (bottom right)
            ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2)
            ax4.axis('off')
            
            # Calculate summary statistics
            total_features = len(feature_trends)
            total_negative_reviews = sum(data['total_negative_reviews'] for data in feature_trends.values())
            improving_count = sum(1 for data in feature_trends.values() if data['trend_direction'] == 'Improving')
            worsening_count = sum(1 for data in feature_trends.values() if data['trend_direction'] == 'Worsening')
            
            # Most problematic feature
            if feature_trends:
                worst_feature = max(feature_trends.items(), key=lambda x: x[1]['total_negative_reviews'])
                worst_feature_name = worst_feature[0]
                worst_feature_count = worst_feature[1]['total_negative_reviews']
            else:
                worst_feature_name = 'None'
                worst_feature_count = 0
            
            # Best improving feature
            best_improving_name = 'None'
            best_improvement_pct = 0
            
            for feature, data in feature_trends.items():
                if data['trend_direction'] == 'Improving':
                    if best_improving_name == 'None' or data['percentage_change'] < best_improvement_pct:
                        best_improvement_pct = data['percentage_change']
                        best_improving_name = feature
            
            summary_text = f"""ANALYSIS SUMMARY
{'='*50}

📊 Total Features Analyzed: {total_features}
📈 Total Negative Reviews: {total_negative_reviews:,}
📉 Improving Features: {improving_count}
📈 Worsening Features: {worsening_count}

🔥 Most Problematic Feature:
   {worst_feature_name[:30]}{'...' if len(worst_feature_name) > 30 else ''}
   ({worst_feature_count} negative reviews)

💚 Best Improving Feature:
   {best_improving_name[:30]}{'...' if len(best_improving_name) > 30 else ''}
   {f"({best_improvement_pct:.1f}% change)" if best_improving_name != 'None' else ''}

📅 Analysis Period: Last 12 months
📊 Data Source: Multi-platform review aggregation"""
            
            ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            
            plt.suptitle('Customer Satisfaction Trend Analysis Dashboard', 
                        fontsize=18, fontweight='bold', y=0.95)
            plt.tight_layout()
            
            # Save the dashboard
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'trend_analysis_dashboard.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
            
        except Exception as e:
            print(f"Error creating dashboard: {e}")
            import traceback
            traceback.print_exc()
            plt.close()
            return ""
    
    def generate_all_visualizations(self, trend_df: pd.DataFrame,
                                   feature_trends: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Generate all available visualizations.
        
        Args:
            trend_df: DataFrame with monthly trend data
            feature_trends: Feature trend analysis data
            
        Returns:
            List of paths to saved visualizations
        """
        print("Generating visualizations...")
        
        saved_plots = []
        
        try:
            # 1. Monthly trends line plot
            print("- Creating monthly trends plot...")
            path1 = self.plot_monthly_trends(trend_df)
            if path1:
                saved_plots.append(path1)
            
            # 2. Feature comparison bar chart
            print("- Creating feature comparison chart...")
            path2 = self.plot_feature_comparison_bar(feature_trends)
            if path2:
                saved_plots.append(path2)
            
            # 3. Trend direction pie chart
            print("- Creating trend direction pie chart...")
            path3 = self.plot_trend_direction_pie(feature_trends)
            if path3:
                saved_plots.append(path3)
            
            # 4. Monthly heatmap
            print("- Creating monthly heatmap...")
            path4 = self.plot_improvement_heatmap(trend_df)
            if path4:
                saved_plots.append(path4)
            
            # 5. Detailed top features plot
            print("- Creating detailed feature trends...")
            path5 = self.plot_top_features_detailed(trend_df, feature_trends)
            if path5:
                saved_plots.append(path5)
            
            # 6. Comprehensive dashboard
            print("- Creating comprehensive dashboard...")
            path6 = self.create_dashboard(trend_df, feature_trends)
            if path6:
                saved_plots.append(path6)
            
        except Exception as e:
            print(f"Error generating visualizations: {e}")
        
        return saved_plots
