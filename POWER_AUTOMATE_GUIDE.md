# Power Automate Integration Guide

## Overview
This guide explains how to integrate your Azure Function App with Power Automate to send console logs via email.

## Azure Function Endpoints

### 1. Console Logs Endpoint
- **URL**: `https://your-function-app.azurewebsites.net/api/console_logs`
- **Methods**: GET, POST
- **Purpose**: Receive console logs and format them for email

### Parameters for GET Request:
- `logs` (required): The console log content
- `application` (optional): Name of the application (default: "Unknown App")
- `severity` (optional): Log severity level (default: "INFO")

### Parameters for POST Request:
Send JSON body with:
```json
{
    "logs": "your console log content here",
    "application": "Your App Name",
    "severity": "ERROR"
}
```

## Power Automate Flow Setup

### Step 1: Create HTTP Request Trigger
1. Create a new Power Automate flow
2. Add "When a HTTP request is received" trigger
3. Configure the request schema (optional):
```json
{
    "type": "object",
    "properties": {
        "logs": {
            "type": "string"
        },
        "application": {
            "type": "string"
        },
        "severity": {
            "type": "string"
        }
    }
}
```

### Step 2: Add HTTP Action to Call Azure Function
1. Add "HTTP" action
2. Configure:
   - **Method**: GET or POST
   - **URI**: `https://your-function-app.azurewebsites.net/api/console_logs`
   - **Headers**: `Content-Type: application/json` (for POST)
   - **Body** (for POST): 
   ```json
   {
       "logs": "@{triggerBody()?['logs']}",
       "application": "@{triggerBody()?['application']}",
       "severity": "@{triggerBody()?['severity']}"
   }
   ```

### Step 3: Parse JSON Response
1. Add "Parse JSON" action
2. Use the response body from the HTTP action
3. Sample schema:
```json
{
    "type": "object",
    "properties": {
        "success": {
            "type": "boolean"
        },
        "timestamp": {
            "type": "string"
        },
        "application": {
            "type": "string"
        },
        "severity": {
            "type": "string"
        },
        "logs": {
            "type": "string"
        },
        "email_body_html": {
            "type": "string"
        },
        "email_subject": {
            "type": "string"
        }
    }
}
```

### Step 4: Send Email
1. Add "Send an email (V2)" action (Office 365 Outlook or Gmail)
2. Configure:
   - **To**: Your recipient email
   - **Subject**: `@{body('Parse_JSON')?['email_subject']}`
   - **Body**: `@{body('Parse_JSON')?['email_body_html']}`
   - **Is HTML**: Yes

## Example URLs for Testing

### GET Request Example:
```
https://your-function-app.azurewebsites.net/api/console_logs?logs=Error occurred&application=MyApp&severity=ERROR
```

### POST Request Example:
```bash
curl -X POST https://your-function-app.azurewebsites.net/api/console_logs \
  -H "Content-Type: application/json" \
  -d '{
    "logs": "Application error occurred at 2024-07-24",
    "application": "MyApp",
    "severity": "ERROR"
  }'
```

## Response Format
The Azure Function returns a JSON response that includes:
- `success`: Boolean indicating if the operation was successful
- `timestamp`: When the logs were processed
- `application`: The application name
- `severity`: The log severity
- `logs`: The original log content
- `email_body_html`: Formatted HTML email body
- `email_subject`: Suggested email subject line

## Security Considerations
1. Consider adding authentication to your Azure Function
2. Validate and sanitize input data
3. Set up proper CORS policies if needed
4. Monitor function usage and costs

## Troubleshooting
- Check Azure Function logs in the portal
- Verify the function app is running
- Test endpoints using the provided test script
- Ensure Power Automate has proper permissions
