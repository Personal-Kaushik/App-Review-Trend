import azure.functions as func
import logging
import json
from datetime import datetime
import html
import pandas as pd
import os
from src.analysis.analyzer import ReviewAnalyzer
from src.models.review import Review

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger", methods=["GET", "POST"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('=== CUSTOM PYTHON HTTP TRIGGER FUNCTION STARTED ===')
    logging.info(f'Request method: {req.method}')
    logging.info(f'Request URL: {req.url}')
    logging.info(f'Request params: {dict(req.params)}')

    try:
        # FORCE OVERRIDE: Always return HTML unless specifically requested otherwise
        # This ensures Power Automate gets HTML regardless of parameters
        force_html = req.params.get('force_html', 'true')  # Default to HTML
        action = req.params.get('action')
        name = req.params.get('name')
        
        logging.info(f'Action parameter: {action}')
        logging.info(f'Name parameter: {name}')
        logging.info(f'Force HTML: {force_html}')
        
        # Only return the old message if explicitly requested with force_html=false
        if force_html.lower() == 'false' and name:
            logging.info(f'Returning personalized greeting for: {name}')
            return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
        else:
            logging.info('Returning app review analysis (default behavior)')
            # Return app review analysis for ALL other cases
            return get_app_review_analysis_html()
            
    except Exception as e:
        logging.error(f"Error in http_trigger: {str(e)}")
        return func.HttpResponse(
            f"<html><body><h1>Error</h1><p>An error occurred: {html.escape(str(e))}</p></body></html>",
            status_code=500,
            mimetype="text/html"
        )

def get_app_review_analysis_html() -> func.HttpResponse:
    """
    Generate HTML report of app review analysis with categories
    """
    logging.info('=== STARTING APP REVIEW ANALYSIS ===')
    try:
        # Load the existing analyzed data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'output', 'reviews_analysis.csv')
        logging.info(f'Looking for CSV file at: {csv_path}')
        
        if not os.path.exists(csv_path):
            logging.warning(f'CSV file not found at: {csv_path}')
            return func.HttpResponse(
                "<html><body><h1>No Data Available</h1><p>No review analysis data found.</p></body></html>",
                status_code=404,
                mimetype="text/html"
            )
        
        logging.info('CSV file found, reading data...')
        # Read the CSV data
        df = pd.read_csv(csv_path)
        logging.info(f'Loaded {len(df)} rows from CSV')
        
        # Convert to Review objects for analysis
        reviews = []
        for _, row in df.iterrows():
            review = Review(
                id=row.get('id', ''),
                source=row.get('source', ''),
                text=row.get('text', ''),
                title=row.get('title', ''),
                author=row.get('author', ''),
                rating=row.get('rating'),
                date=pd.to_datetime(row.get('date')) if pd.notna(row.get('date')) else None,
                url=row.get('url', ''),
                sentiment=row.get('sentiment', ''),
                category=row.get('category', '')
            )
            reviews.append(review)
        
        logging.info(f'Converted to {len(reviews)} Review objects')
        
        # Initialize analyzer and get summary
        analyzer = ReviewAnalyzer()
        logging.info('Getting analysis summary...')
        summary = analyzer.get_analysis_summary(reviews)
        
        # Get top issues
        logging.info('Getting top issues...')
        top_issues = analyzer.get_top_issues(reviews, top_n=10)
        
        # Generate HTML report
        logging.info('Generating HTML report...')
        html_content = generate_html_report(summary, top_issues, reviews)
        
        logging.info('=== APP REVIEW ANALYSIS COMPLETED SUCCESSFULLY ===')
        return func.HttpResponse(
            html_content,
            status_code=200,
            mimetype="text/html"
        )
        
    except Exception as e:
        logging.error(f"Error generating analysis: {str(e)}")
        logging.error(f"Exception type: {type(e).__name__}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return func.HttpResponse(
            f"<html><body><h1>Error</h1><p>Failed to generate analysis: {html.escape(str(e))}</p></body></html>",
            status_code=500,
            mimetype="text/html"
        )

def generate_html_report(summary: dict, top_issues: list, reviews: list) -> str:
    """
    Generate simple category report for Power Automate consumption
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Calculate total negative reviews for percentage calculation
    negative_reviews = [r for r in reviews if r.sentiment == 'Negative']
    total_negative = len(negative_reviews)
    
    # Build category distribution HTML - only categories with percentages and numbers
    category_rows = ""
    # Sort categories by count (descending)
    sorted_categories = sorted(summary['category_distribution'].items(), key=lambda x: x[1], reverse=True)
    
    for category, count in sorted_categories:
        if category and category != 'Others':  # Skip empty or 'Others' category
            percentage = (count / total_negative * 100) if total_negative > 0 else 0
            category_rows += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{html.escape(category)}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{count}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{percentage:.1f}%</td>
            </tr>"""
    
    # Generate simple HTML report with only categories
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>App Review Categories</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #0078d4; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 8px; border: 1px solid #ddd; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>App Review Categories</h2>
            <p>Generated: {timestamp}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th style="text-align: center;">Count</th>
                    <th style="text-align: center;">Percentage</th>
                </tr>
            </thead>
            <tbody>
                {category_rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html_report

@app.route(route="console_logs", methods=["GET", "POST"])
def console_logs_handler(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle console logs sent from Power Automate
    Accepts logs via GET parameters or POST body
    Returns formatted response for Power Automate email integration
    """
    logging.info('Console logs handler triggered')
    
    try:
        # Get logs from different sources
        logs_data = None
        source = "unknown"
        
        if req.method == "GET":
            # Get logs from query parameters
            logs_data = req.params.get('logs')
            application = req.params.get('application', 'Unknown App')
            severity = req.params.get('severity', 'INFO')
            source = "GET parameters"
            
        elif req.method == "POST":
            # Get logs from POST body
            try:
                req_body = req.get_json()
                if req_body:
                    logs_data = req_body.get('logs')
                    application = req_body.get('application', 'Unknown App')
                    severity = req_body.get('severity', 'INFO')
                    source = "POST body"
                else:
                    # Try to get from form data or plain text
                    logs_data = req.get_body().decode('utf-8')
                    application = req.params.get('application', 'Unknown App')
                    severity = req.params.get('severity', 'INFO')
                    source = "POST body (text)"
            except Exception as e:
                logging.error(f"Error parsing POST body: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": "Failed to parse request body", "details": str(e)}),
                    status_code=400,
                    mimetype="application/json"
                )
        
        if not logs_data:
            return func.HttpResponse(
                json.dumps({"error": "No logs data provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Process and format the logs
        formatted_response = format_logs_for_email(logs_data, application, severity, source)
        
        # Log the received data for debugging
        logging.info(f"Received logs from {source} for application: {application}")
        
        return func.HttpResponse(
            json.dumps(formatted_response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in console_logs_handler: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def format_logs_for_email(logs_data, application, severity, source):
    """
    Format console logs for email body consumption by Power Automate
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Escape HTML characters to prevent injection
    safe_logs = html.escape(str(logs_data))
    safe_application = html.escape(str(application))
    
    # Create structured response for Power Automate
    email_body = f"""
    <html>
    <body>
    <h2>Console Logs Alert</h2>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <tr><td><strong>Timestamp:</strong></td><td>{timestamp}</td></tr>
        <tr><td><strong>Application:</strong></td><td>{safe_application}</td></tr>
        <tr><td><strong>Severity:</strong></td><td>{severity}</td></tr>
        <tr><td><strong>Source:</strong></td><td>{source}</td></tr>
    </table>
    
    <h3>Log Details:</h3>
    <div style="background-color: #f5f5f5; padding: 10px; font-family: monospace; white-space: pre-wrap; border: 1px solid #ddd;">
{safe_logs}
    </div>
    </body>
    </html>
    """
    
    # Return structured data for Power Automate
    return {
        "success": True,
        "timestamp": timestamp,
        "application": application,
        "severity": severity,
        "logs": logs_data,
        "email_body_html": email_body.strip(),
        "email_subject": f"Console Logs Alert - {application} ({severity})",
        "source": source
    }