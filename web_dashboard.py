"""
Enhanced web dashboard for Review Analysis with interactive features.
"""
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, jsonify, request, send_from_directory
import webbrowser
import threading
import time
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo


class InteractiveDashboard:
    """Interactive web dashboard for review analysis."""
    
    def __init__(self, output_dir: str = 'output', port: int = 5000):
        """
        Initialize the interactive dashboard.
        
        Args:
            output_dir: Directory containing analysis data
            port: Port to run the Flask server on
        """
        self.output_dir = output_dir
        self.port = port
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.data = {}
        self.trend_df = None
        self.feature_trends = {}
        
        # Create directories
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('static/images', exist_ok=True)
        
        # Setup routes
        self._setup_routes()
        
        # Load data if available
        self._load_data()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('dashboard.html', data=self.data)
        
        @self.app.route('/api/trend-data')
        def get_trend_data():
            """API endpoint for trend data."""
            if self.trend_df is not None:
                # Convert to format suitable for charts
                return jsonify(self.trend_df.to_dict('records'))
            return jsonify([])
        
        @self.app.route('/api/feature-trends')
        def get_feature_trends():
            """API endpoint for feature trends."""
            return jsonify(self.feature_trends)
        
        @self.app.route('/api/summary-stats')
        def get_summary_stats():
            """API endpoint for summary statistics."""
            if not self.feature_trends:
                return jsonify({})
            
            total_features = len(self.feature_trends)
            total_negative_reviews = sum(data['total_negative_reviews'] for data in self.feature_trends.values())
            improving_count = sum(1 for data in self.feature_trends.values() if data['trend_direction'] == 'Improving')
            worsening_count = sum(1 for data in self.feature_trends.values() if data['trend_direction'] == 'Worsening')
            stable_count = sum(1 for data in self.feature_trends.values() if data['trend_direction'] == 'Stable')
            
            return jsonify({
                'total_features': total_features,
                'total_negative_reviews': total_negative_reviews,
                'improving_count': improving_count,
                'worsening_count': worsening_count,
                'stable_count': stable_count
            })
        
        @self.app.route('/api/plotly-chart/<chart_type>')
        def get_plotly_chart(chart_type):
            """Generate Plotly charts dynamically."""
            try:
                if chart_type == 'trend_pie':
                    chart_json = self._create_trend_pie_plotly()
                else:
                    return jsonify({'error': 'Unknown chart type'})
                
                return jsonify(chart_json)
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/filter-features', methods=['POST'])
        def filter_features():
            """Filter features based on criteria."""
            try:
                filters = request.json
                trend_filter = filters.get('trend_direction', 'all')
                min_reviews = filters.get('min_reviews', 0)
                
                filtered_features = {}
                for feature, data in self.feature_trends.items():
                    # Apply trend filter
                    if trend_filter != 'all' and data['trend_direction'].lower() != trend_filter.lower():
                        continue
                    
                    # Apply minimum reviews filter
                    if data['total_negative_reviews'] < min_reviews:
                        continue
                    
                    filtered_features[feature] = data
                
                return jsonify(filtered_features)
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/feature-charts')
        def get_feature_charts():
            """API endpoint for feature chart information."""
            try:
                feature_charts_dir = os.path.join(self.output_dir, 'feature_charts')
                if os.path.exists(feature_charts_dir):
                    chart_files = [f for f in os.listdir(feature_charts_dir) if f.endswith('.png')]
                    charts_info = []
                    for chart_file in chart_files:
                        feature_name = chart_file.replace('_monthly_chart.png', '').replace('_', ' ')
                        charts_info.append({
                            'feature_name': feature_name,
                            'filename': chart_file,
                            'url': f'/static/feature_charts/{chart_file}'
                        })
                    return jsonify(charts_info)
                return jsonify([])
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/static/feature_charts/<filename>')
        def serve_feature_charts(filename):
            """Serve feature chart images."""
            feature_charts_dir = os.path.join(self.output_dir, 'feature_charts')
            return send_from_directory(feature_charts_dir, filename)
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files."""
            return send_from_directory('static', filename)
    
    def _load_data(self):
        """Load analysis data from output directory."""
        try:
            # Load trend data
            trend_csv_path = os.path.join(self.output_dir, 'monthly_trends.csv')
            if os.path.exists(trend_csv_path):
                self.trend_df = pd.read_csv(trend_csv_path)
            
            # Load feature trends
            summary_json_path = os.path.join(self.output_dir, 'analysis_summary.json')
            if os.path.exists(summary_json_path):
                with open(summary_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'trend_analysis' in data and 'feature_trends' in data['trend_analysis']:
                        self.feature_trends = data['trend_analysis']['feature_trends']
                        self.data = data
            
            print(f"Loaded data: {len(self.feature_trends)} features, trend data shape: {self.trend_df.shape if self.trend_df is not None else 'None'}")
            
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def _create_trend_pie_plotly(self):
        """Create trend direction pie chart using Plotly."""
        if not self.feature_trends:
            return {}
        
        trend_counts = {'Improving': 0, 'Worsening': 0, 'Stable': 0}
        for feature, data in self.feature_trends.items():
            trend = data['trend_direction']
            if trend in trend_counts:
                trend_counts[trend] += 1
        
        # Filter out zero counts
        trend_counts = {k: v for k, v in trend_counts.items() if v > 0}
        
        colors = {'Improving': '#28a745', 'Worsening': '#dc3545', 'Stable': '#6c757d'}
        
        fig = go.Figure(data=go.Pie(
            labels=list(trend_counts.keys()),
            values=list(trend_counts.values()),
            marker=dict(colors=[colors[k] for k in trend_counts.keys()]),
            textinfo='label+percent+value',
            textfont=dict(size=14),
            hovertemplate='<b>%{label}</b><br>' +
                         'Features: %{value}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Feature Trend Direction Distribution',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            showlegend=True,
            paper_bgcolor='white',
            font=dict(size=12)
        )
        
        return fig.to_dict()
    
    def create_dashboard_template(self):
        """Create the HTML template for the dashboard."""
        template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Review Analysis Dashboard</title>
    
    <!-- External CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <!-- Plotly -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    
    <!-- Custom CSS -->
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        
        .dashboard-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            margin: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .card-header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-radius: 15px 15px 0 0 !important;
            font-weight: bold;
        }
        
        .stat-card {
            text-align: center;
            padding: 20px;
            background: linear-gradient(45deg, #f8f9fa, #ffffff);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }
        
        .chart-container {
            min-height: 400px;
            padding: 20px;
        }
        
        .filter-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .btn-custom {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            color: white;
            border-radius: 25px;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }
        
        .btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            color: white;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
        }
        
        .spinner {
            width: 3rem;
            height: 3rem;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .navbar {
            background: linear-gradient(45deg, #667eea, #764ba2) !important;
        }
        
        .feature-item {
            padding: 10px;
            border-bottom: 1px solid #e9ecef;
            transition: background-color 0.3s ease;
            cursor: pointer;
        }
        
        .feature-item:hover {
            background-color: #f8f9fa;
        }
        
        .trend-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .badge-improving { background: #28a745; color: white; }
        .badge-worsening { background: #dc3545; color: white; }
        .badge-stable { background: #6c757d; color: white; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-chart-line me-2"></i>
                Interactive Review Dashboard
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <span class="navbar-text">
                            <i class="fas fa-clock me-1"></i>
                            Last updated: <span id="last-updated">Loading...</span>
                        </span>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="dashboard-container">
        <!-- Header -->
        <div class="text-center mb-5">
            <h1 class="display-4 text-primary">
                <i class="fas fa-analytics me-3"></i>
                Customer Satisfaction Analytics
            </h1>
            <p class="lead text-muted">Real-time Feature-based Review Trend Analysis</p>
        </div>

        <!-- Statistics Cards -->
        <div class="row mb-4" id="stats-row">
            <div class="col-md-3 mb-3">
                <div class="card stat-card">
                    <div class="stat-number" id="total-features">-</div>
                    <div class="stat-label">Features Analyzed</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card stat-card">
                    <div class="stat-number" id="total-reviews">-</div>
                    <div class="stat-label">Total Negative Reviews</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card stat-card">
                    <div class="stat-number text-success" id="improving-features">-</div>
                    <div class="stat-label">Improving Features</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card stat-card">
                    <div class="stat-number text-danger" id="worsening-features">-</div>
                    <div class="stat-label">Worsening Features</div>
                </div>
            </div>
        </div>

        <!-- Filter Panel -->
        <div class="filter-panel">
            <div class="row align-items-center">
                <div class="col-md-4">
                    <label class="form-label">Filter by Trend:</label>
                    <select class="form-select" id="trend-filter">
                        <option value="all">All Trends</option>
                        <option value="improving">Improving Only</option>
                        <option value="worsening">Worsening Only</option>
                        <option value="stable">Stable Only</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Minimum Reviews:</label>
                    <input type="number" class="form-control" id="min-reviews" value="0" min="0">
                </div>
                <div class="col-md-4">
                    <button class="btn btn-custom mt-4" onclick="applyFilters()">
                        <i class="fas fa-filter me-2"></i>Apply Filters
                    </button>
                </div>
            </div>
        </div>

        <!-- Charts Row - Only Trend Distribution -->
        <div class="row mb-4">
            <div class="col-lg-12 mb-4">
                <div class="card">
                    <div class="card-header">
                        <i class="fas fa-pie-chart me-2"></i>Trend Distribution
                    </div>
                    <div class="card-body">
                        <div id="trend-pie-chart" class="chart-container">
                            <div class="loading">
                                <div class="spinner mx-auto mb-3"></div>
                                <p>Loading distribution...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Feature Details Table -->
        <div class="card mb-4">
            <div class="card-header">
                <i class="fas fa-table me-2"></i>Feature Details
                <small class="text-muted ms-2">(Click on features for details)</small>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-primary">
                            <tr>
                                <th>Feature</th>
                                <th>Total Reviews</th>
                                <th>Trend</th>
                                <th>Change %</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="features-table-body">
                            <tr>
                                <td colspan="5" class="text-center">
                                    <div class="spinner mx-auto mb-3"></div>
                                    <p>Loading feature data...</p>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Individual Feature Charts -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-chart-bar me-2"></i>Individual Feature Charts
                <small class="text-muted ms-2">(Monthly breakdown for top features)</small>
            </div>
            <div class="card-body">
                <div id="feature-charts-container" class="row">
                    <div class="col-12 text-center">
                        <div class="spinner mx-auto mb-3"></div>
                        <p>Loading feature charts...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JavaScript -->
    <script>
        let featureData = {};
        let filteredData = {};

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            setInterval(updateTimestamp, 60000); // Update every minute
        });

        async function loadDashboardData() {
            try {
                // Load summary statistics
                const statsResponse = await fetch('/api/summary-stats');
                const stats = await statsResponse.json();
                updateStatsDisplay(stats);

                // Load feature trends
                const trendsResponse = await fetch('/api/feature-trends');
                featureData = await trendsResponse.json();
                filteredData = featureData;
                updateFeaturesTable(filteredData);

                // Load charts
                await loadAllCharts();

                // Load feature charts
                await loadFeatureCharts();

                updateTimestamp();
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                showError('Failed to load dashboard data');
            }
        }

        function updateStatsDisplay(stats) {
            document.getElementById('total-features').textContent = stats.total_features || 0;
            document.getElementById('total-reviews').textContent = (stats.total_negative_reviews || 0).toLocaleString();
            document.getElementById('improving-features').textContent = stats.improving_count || 0;
            document.getElementById('worsening-features').textContent = stats.worsening_count || 0;
        }

        async function loadAllCharts() {
            try {
                // Load trend pie chart only
                const pieResponse = await fetch('/api/plotly-chart/trend_pie');
                const pieChart = await pieResponse.json();
                if (!pieChart.error) {
                    Plotly.newPlot('trend-pie-chart', pieChart.data, pieChart.layout, {responsive: true});
                }
            } catch (error) {
                console.error('Error loading charts:', error);
                showError('Failed to load chart');
            }
        }

        async function loadFeatureCharts() {
            try {
                const response = await fetch('/api/feature-charts');
                const charts = await response.json();
                
                const container = document.getElementById('feature-charts-container');
                
                if (charts.length === 0) {
                    container.innerHTML = '<div class="col-12 text-center text-muted">No feature charts available</div>';
                    return;
                }

                container.innerHTML = charts.map(chart => `
                    <div class="col-lg-6 col-xl-4 mb-4">
                        <div class="card h-100">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0">${chart.feature_name}</h6>
                            </div>
                            <div class="card-body p-2">
                                <img src="${chart.url}" alt="${chart.feature_name} Chart" 
                                     class="img-fluid" style="width: 100%; height: auto;">
                            </div>
                        </div>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error('Error loading feature charts:', error);
                document.getElementById('feature-charts-container').innerHTML = 
                    '<div class="col-12 text-center text-danger">Failed to load feature charts</div>';
            }
        }

        function updateFeaturesTable(data) {
            const tbody = document.getElementById('features-table-body');
            
            if (Object.keys(data).length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No features match the current filters</td></tr>';
                return;
            }

            // Sort features by total negative reviews
            const sortedFeatures = Object.entries(data).sort((a, b) => b[1].total_negative_reviews - a[1].total_negative_reviews);

            tbody.innerHTML = sortedFeatures.map(([feature, info]) => `
                <tr class="feature-item" onclick="showFeatureDetails('${feature}')">
                    <td><strong>${feature}</strong></td>
                    <td>${info.total_negative_reviews.toLocaleString()}</td>
                    <td>
                        <span class="trend-badge badge-${info.trend_direction.toLowerCase()}">
                            ${info.trend_direction}
                        </span>
                    </td>
                    <td>${info.percentage_change > 0 ? '+' : ''}${info.percentage_change.toFixed(1)}%</td>
                    <td>
                        ${info.trend_direction === 'Improving' ? '<i class="fas fa-arrow-down text-success"></i>' :
                          info.trend_direction === 'Worsening' ? '<i class="fas fa-arrow-up text-danger"></i>' :
                          '<i class="fas fa-minus text-muted"></i>'}
                    </td>
                </tr>
            `).join('');
        }

        async function applyFilters() {
            const trendFilter = document.getElementById('trend-filter').value;
            const minReviews = parseInt(document.getElementById('min-reviews').value) || 0;

            try {
                const response = await fetch('/api/filter-features', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        trend_direction: trendFilter,
                        min_reviews: minReviews
                    })
                });

                filteredData = await response.json();
                updateFeaturesTable(filteredData);
                
                showSuccess('Filters applied successfully');
            } catch (error) {
                console.error('Error applying filters:', error);
                showError('Failed to apply filters');
            }
        }

        function showFeatureDetails(featureName) {
            const feature = featureData[featureName];
            if (!feature) return;

            const modal = `
                <div class="modal fade" id="featureModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header bg-primary text-white">
                                <h5 class="modal-title">
                                    <i class="fas fa-info-circle me-2"></i>Feature Details: ${featureName}
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Statistics</h6>
                                        <ul class="list-unstyled">
                                            <li><strong>Total Negative Reviews:</strong> ${feature.total_negative_reviews.toLocaleString()}</li>
                                            <li><strong>Trend Direction:</strong> 
                                                <span class="trend-badge badge-${feature.trend_direction.toLowerCase()}">
                                                    ${feature.trend_direction}
                                                </span>
                                            </li>
                                            <li><strong>Percentage Change:</strong> ${feature.percentage_change > 0 ? '+' : ''}${feature.percentage_change.toFixed(1)}%</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Insights</h6>
                                        <p class="text-muted">
                                            This feature has ${feature.trend_direction.toLowerCase() === 'improving' ? 'shown improvement' : 
                                                              feature.trend_direction.toLowerCase() === 'worsening' ? 'been declining' : 'remained stable'} 
                                            over the analysis period.
                                        </p>
                                        ${feature.trend_direction === 'Worsening' ? 
                                            '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i>This feature needs attention</div>' : ''}
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal if any
            const existingModal = document.getElementById('featureModal');
            if (existingModal) {
                existingModal.remove();
            }

            // Add new modal
            document.body.insertAdjacentHTML('beforeend', modal);
            const modalInstance = new bootstrap.Modal(document.getElementById('featureModal'));
            modalInstance.show();
        }

        function updateTimestamp() {
            const now = new Date();
            document.getElementById('last-updated').textContent = now.toLocaleString();
        }

        function showSuccess(message) {
            showToast(message, 'success');
        }

        function showError(message) {
            showToast(message, 'error');
        }

        function showToast(message, type) {
            const toastId = 'toast-' + Date.now();
            const bgClass = type === 'success' ? 'bg-success' : 'bg-danger';
            
            const toast = `
                <div class="toast align-items-center text-white ${bgClass} border-0" id="${toastId}" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'} me-2"></i>
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;

            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                toastContainer.style.zIndex = '9999';
                document.body.appendChild(toastContainer);
            }

            toastContainer.insertAdjacentHTML('beforeend', toast);
            const toastElement = document.getElementById(toastId);
            const bsToast = new bootstrap.Toast(toastElement);
            bsToast.show();

            // Auto remove after hide
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }

        // Handle window resize for responsive charts
        window.addEventListener('resize', function() {
            Plotly.Plots.resize('trend-pie-chart');
        });
    </script>
</body>
</html>"""
        
        with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def run_server(self, debug: bool = False, open_browser: bool = True):
        """
        Run the Flask server.
        
        Args:
            debug: Enable debug mode
            open_browser: Whether to open browser automatically
        """
        # Create template
        self.create_dashboard_template()
        
        def open_browser_delayed():
            time.sleep(2)  # Wait for server to start
            try:
                webbrowser.open(f'http://localhost:{self.port}')
                print(f"🌐 Dashboard opened at http://localhost:{self.port}")
            except Exception as e:
                print(f"Could not open browser: {e}")
                print(f"Please manually open: http://localhost:{self.port}")
        
        if open_browser:
            threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        print(f"🚀 Starting interactive dashboard server on port {self.port}...")
        print(f"📊 Dashboard will be available at: http://localhost:{self.port}")
        
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=debug, use_reloader=False)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")


def create_and_run_dashboard(output_dir: str = 'output', port: int = 5000):
    """
    Create and run the interactive dashboard.
    
    Args:
        output_dir: Directory containing analysis data
        port: Port to run the server on
    """
    dashboard = InteractiveDashboard(output_dir, port)
    dashboard.run_server()


if __name__ == "__main__":
    create_and_run_dashboard()
