"""
HTML dashboard generator for trend analysis.
"""
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import base64
import webbrowser


class HTMLDashboardGenerator:
    """Generator for interactive HTML dashboards."""
    
    def __init__(self, output_dir: str = 'output'):
        """Initialize the HTML generator."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string for embedding in HTML."""
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return ""
    
    def generate_html_dashboard(self, trend_df: pd.DataFrame,
                              feature_trends: Dict[str, Dict[str, Any]],
                              image_paths: List[str] = None) -> str:
        """
        Generate a comprehensive HTML dashboard.
        
        Args:
            trend_df: DataFrame with monthly trend data
            feature_trends: Feature trend analysis data
            image_paths: List of paths to visualization images
            
        Returns:
            Path to generated HTML file
        """
        # Calculate summary statistics
        total_features = len(feature_trends)
        total_negative_reviews = sum(data['total_negative_reviews'] for data in feature_trends.values())
        improving_count = sum(1 for data in feature_trends.values() if data['trend_direction'] == 'Improving')
        worsening_count = sum(1 for data in feature_trends.values() if data['trend_direction'] == 'Worsening')
        stable_count = sum(1 for data in feature_trends.values() if data['trend_direction'] == 'Stable')
        
        # Get top features
        top_features = sorted(
            feature_trends.items(),
            key=lambda x: x[1]['total_negative_reviews'],
            reverse=True
        )[:10]
        
        # Get improving and worsening features
        improving_features = [(f, d) for f, d in feature_trends.items() if d['trend_direction'] == 'Improving']
        worsening_features = [(f, d) for f, d in feature_trends.items() if d['trend_direction'] == 'Worsening']
        
        # Sort by improvement percentage
        improving_features.sort(key=lambda x: x[1]['percentage_change'])
        worsening_features.sort(key=lambda x: x[1]['percentage_change'], reverse=True)
        
        # Encode images if provided
        encoded_images = {}
        if image_paths:
            for img_path in image_paths:
                if os.path.exists(img_path):
                    img_name = os.path.basename(img_path).replace('.png', '')
                    encoded_images[img_name] = self.encode_image_to_base64(img_path)
        
        # Generate HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Satisfaction Trend Analysis Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            text-align: center;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .feature-list {{
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .feature-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
            transition: background-color 0.3s ease;
        }}
        
        .feature-item:hover {{
            background-color: #f8f9fa;
        }}
        
        .feature-name {{
            font-weight: 500;
            flex: 1;
        }}
        
        .feature-count {{
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 10px;
        }}
        
        .trend-badge {{
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.7em;
            font-weight: bold;
        }}
        
        .improving {{
            background: #2ecc71;
            color: white;
        }}
        
        .worsening {{
            background: #e74c3c;
            color: white;
        }}
        
        .stable {{
            background: #95a5a6;
            color: white;
        }}
        
        .visualization-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .viz-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .viz-card img {{
            width: 100%;
            border-radius: 10px;
        }}
        
        .monthly-data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .monthly-data-table th,
        .monthly-data-table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        .monthly-data-table th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        .monthly-data-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .progress-bar {{
            background-color: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            height: 20px;
            margin-top: 5px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            color: white;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            h1 {{
                font-size: 2em;
            }}
            
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Customer Satisfaction Trend Analysis</h1>
            <p class="subtitle">Feature-based Negative Review Tracking Dashboard</p>
            <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </header>
        
        <div class="dashboard-grid">
            <!-- Summary Statistics -->
            <div class="card">
                <h3>📈 Overview Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{total_features}</div>
                        <div class="stat-label">Features Analyzed</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{total_negative_reviews:,}</div>
                        <div class="stat-label">Total Negative Reviews</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{improving_count}</div>
                        <div class="stat-label">Improving Features</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{worsening_count}</div>
                        <div class="stat-label">Worsening Features</div>
                    </div>
                </div>
            </div>
            
            <!-- Top Problematic Features -->
            <div class="card">
                <h3>🔥 Most Problematic Features</h3>
                <div class="feature-list">
                    {"".join([f'''
                    <div class="feature-item">
                        <span class="feature-name">{feature[:40] + "..." if len(feature) > 40 else feature}</span>
                        <span class="feature-count">{data["total_negative_reviews"]}</span>
                        <span class="trend-badge {data["trend_direction"].lower()}">{data["trend_direction"]}</span>
                    </div>
                    ''' for feature, data in top_features])}
                </div>
            </div>
            
            <!-- Improving Features -->
            <div class="card">
                <h3>📉 Most Improved Features</h3>
                <div class="feature-list">
                    {("".join([f'''
                    <div class="feature-item">
                        <span class="feature-name">{feature[:40] + "..." if len(feature) > 40 else feature}</span>
                        <span style="color: #2ecc71; font-weight: bold;">{data["percentage_change"]:.1f}%</span>
                        <span class="trend-badge improving">Improving</span>
                    </div>
                    ''' for feature, data in improving_features[:8]]) if improving_features else '<p style="text-align: center; color: #7f8c8d;">No improving features found</p>')}
                </div>
            </div>
            
            <!-- Worsening Features -->
            <div class="card">
                <h3>📈 Features Needing Attention</h3>
                <div class="feature-list">
                    {("".join([f'''
                    <div class="feature-item">
                        <span class="feature-name">{feature[:40] + "..." if len(feature) > 40 else feature}</span>
                        <span style="color: #e74c3c; font-weight: bold;">+{data["percentage_change"]:.1f}%</span>
                        <span class="trend-badge worsening">Worsening</span>
                    </div>
                    ''' for feature, data in worsening_features[:8]]) if worsening_features else '<p style="text-align: center; color: #7f8c8d;">No worsening features found</p>')}
                </div>
            </div>
        </div>
        
        <!-- Monthly Data Table -->
        <div class="card">
            <h3>📅 Monthly Breakdown (Top 6 Features)</h3>
            {self._generate_monthly_table(trend_df)}
        </div>
        
        <!-- Visualizations -->
        <div class="visualization-grid">
            {"".join([f'''
            <div class="viz-card">
                <h3>{self._get_viz_title(name)}</h3>
                <img src="{img_data}" alt="{self._get_viz_title(name)}" />
            </div>
            ''' for name, img_data in encoded_images.items() if img_data])}
        </div>
        
        <div class="footer">
            <p>🤖 Generated by AI-Powered Review Analysis Platform</p>
            <p>Data sources: Play Store, App Store, RSS feeds, and more</p>
        </div>
    </div>
    
    <script>
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Animate progress bars
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {{
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {{
                    bar.style.width = width;
                }}, 500);
            }});
            
            // Add click handlers for feature items
            const featureItems = document.querySelectorAll('.feature-item');
            featureItems.forEach(item => {{
                item.addEventListener('click', function() {{
                    const featureName = this.querySelector('.feature-name').textContent;
                    alert(`Feature: ${{featureName}}\\n\\nClick to view detailed analysis (feature not implemented yet)`);
                }});
            }});
        }});
    </script>
</body>
</html>
        """
        
        # Save HTML file
        html_path = os.path.join(self.output_dir, 'trend_analysis_dashboard.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def _generate_monthly_table(self, trend_df: pd.DataFrame) -> str:
        """Generate HTML table for monthly data."""
        if trend_df.empty:
            return "<p>No monthly data available.</p>"
        
        # Get top 6 features by total
        feature_cols = [col for col in trend_df.columns if col not in ['month', 'month_name']]
        totals = {col: trend_df[col].sum() for col in feature_cols}
        top_features = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:6]
        top_feature_names = [f[0] for f in top_features if f[1] > 0]
        
        if not top_feature_names:
            return "<p>No feature data available.</p>"
        
        # Generate table HTML
        table_html = '<table class="monthly-data-table"><thead><tr><th>Month</th>'
        
        # Add headers for top features
        for feature in top_feature_names:
            short_name = feature[:20] + "..." if len(feature) > 20 else feature
            table_html += f'<th>{short_name}</th>'
        
        table_html += '</tr></thead><tbody>'
        
        # Add data rows
        for _, row in trend_df.iterrows():
            table_html += f'<tr><td><strong>{row["month_name"]}</strong></td>'
            for feature in top_feature_names:
                count = row[feature]
                table_html += f'<td>{count}</td>'
            table_html += '</tr>'
        
        # Add total row
        table_html += '<tr style="background-color: #f8f9fa; font-weight: bold;"><td>TOTAL</td>'
        for feature in top_feature_names:
            total = trend_df[feature].sum()
            table_html += f'<td>{total}</td>'
        table_html += '</tr>'
        
        table_html += '</tbody></table>'
        return table_html
    
    def _get_viz_title(self, img_name: str) -> str:
        """Get display title for visualization."""
        titles = {
            'monthly_trends': '📈 Monthly Trends',
            'feature_comparison': '📊 Feature Comparison',
            'trend_direction_pie': '🥧 Trend Direction Distribution',
            'monthly_heatmap': '🔥 Monthly Heatmap',
            'top_features_detailed': '🔍 Detailed Feature Analysis',
            'trend_analysis_dashboard': '🎯 Complete Dashboard'
        }
        return titles.get(img_name, img_name.replace('_', ' ').title())
    
    def open_in_browser(self, html_path: str) -> None:
        """Open the HTML dashboard in default browser."""
        try:
            # Convert to absolute path and use file:// protocol
            abs_path = os.path.abspath(html_path)
            file_url = f"file:///{abs_path.replace(os.sep, '/')}"
            
            print(f"Opening dashboard in browser: {file_url}")
            webbrowser.open(file_url)
            print("✅ Dashboard opened in default browser!")
            
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print(f"📁 Please manually open: {os.path.abspath(html_path)}")
