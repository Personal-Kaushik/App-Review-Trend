#!/usr/bin/env python3
"""
Azure Function Deployment Fixer
This creates the EXACT files Azure needs in the EXACT structure
"""
import os
import shutil

def create_azure_deployment_package():
    print("🚀 Creating Azure Function Deployment Package...")
    print("=" * 60)
    
    # Create a clean deployment folder
    deploy_dir = "azure_deploy"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Copy essential files
    files_to_copy = [
        "function_app.py",
        "host.json", 
        "requirements.txt",
        "local.settings.json"
    ]
    
    print("📁 Copying files to deployment directory...")
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"✅ Copied: {file}")
        else:
            print(f"⚠️  Missing: {file}")
    
    # Copy the src directory
    if os.path.exists("src"):
        shutil.copytree("src", os.path.join(deploy_dir, "src"))
        print("✅ Copied: src/ directory")
    
    # Copy the output directory
    if os.path.exists("output"):
        shutil.copytree("output", os.path.join(deploy_dir, "output"))
        print("✅ Copied: output/ directory")
    
    # Copy HttpTriggerFunction
    if os.path.exists("HttpTriggerFunction"):
        shutil.copytree("HttpTriggerFunction", os.path.join(deploy_dir, "HttpTriggerFunction"))
        print("✅ Copied: HttpTriggerFunction/ directory")
    
    print("\n🎯 DEPLOYMENT INSTRUCTIONS:")
    print("1. ZIP the entire 'azure_deploy' folder")
    print("2. In Azure Portal → Function App → Deployment Center")
    print("3. Choose 'ZIP Deploy' and upload the ZIP file")
    print("4. Wait for deployment to complete")
    print("5. Test the function URL immediately")
    
    print(f"\n📦 Deployment package created in: {os.path.abspath(deploy_dir)}")
    
    # List the contents
    print("\n📋 Package contents:")
    for root, dirs, files in os.walk(deploy_dir):
        level = root.replace(deploy_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')

if __name__ == "__main__":
    create_azure_deployment_package()
