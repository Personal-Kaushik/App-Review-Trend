#!/usr/bin/env python3
"""
Azure Function Debug Helper - Create a simple test URL to debug the deployed function
"""

print("🔍 DEBUGGING DEPLOYED AZURE FUNCTION")
print("=" * 60)
print()

print("STEP 1: Check Azure Function Logs")
print("- Go to Azure Portal")
print("- Navigate to your Function App")
print("- Go to 'Functions' → 'http_trigger' → 'Monitor'")
print("- Look for our custom log messages:")
print("  • '=== CUSTOM PYTHON HTTP TRIGGER FUNCTION STARTED ==='")
print("  • '=== STARTING APP REVIEW ANALYSIS ==='")
print()

print("STEP 2: Test the Deployed Function URL")
print("Use this URL format (replace YOUR_FUNCTION_APP_NAME):")
print("https://YOUR_FUNCTION_APP_NAME.azurewebsites.net/api/http_trigger")
print()

print("STEP 3: Check What Azure is Actually Running")
print("In Azure Portal → Function App → Development Tools → Console")
print("Run these commands:")
print("  cd site/wwwroot")
print("  dir")
print("  type function_app.py")
print("  type HttpTriggerFunction/function.json")
print()

print("STEP 4: Force Redeploy if Needed")
print("If the files are wrong in Azure, you need to redeploy:")
print("- Make sure you're deploying from the RIGHT folder")
print("- Azure needs the folder structure with host.json")
print()

print("🚨 MOST LIKELY ISSUES:")
print("1. Azure is running old cached code")
print("2. Deployment didn't include our changes")
print("3. Wrong folder was deployed")
print("4. Azure is still using the v1 programming model")
print()

print("💡 QUICK TEST:")
print("Add ?debug=true to your Function URL")
print("This should trigger our logging and help identify the issue")
