"""
Installation script for the Review Analysis System.
Installs required dependencies and sets up the environment.
"""
import subprocess
import sys
import os


def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main installation function."""
    print("Installing Review Analysis System dependencies...")
    
    # Core dependencies that should work
    core_packages = [
        "pandas>=2.0.0",
        "textblob>=0.17.0",
        "google-play-scraper>=1.2.0",
        "requests>=2.28.0",
        "feedparser>=6.0.0",
        "PyYAML>=6.0",
        "beautifulsoup4>=4.11.0",
        "certifi>=2022.0.0",
        "python-dateutil>=2.8.0",
        "joblib>=1.2.0",
        "numpy>=1.24.0",
        "six>=1.16.0",
        "soupsieve>=2.4.0",
        "colorama>=0.4.6",
        "urllib3>=1.26.0",
        "charset-normalizer>=3.0.0",
        "idna>=3.4"
    ]
    
    # Optional dependencies
    optional_packages = [
        "newspaper3k>=0.2.8",
        "lxml[html_clean]>=4.9.0",
        "snscrape>=0.7.0",
        "nltk>=3.8.0",
        "Pillow>=9.0.0",
        "regex>=2023.0.0",
        "jieba3k>=0.35.0",
        "cssselect>=1.2.0",
        "PySocks>=1.7.0",
        "click>=8.1.0",
        "filelock>=3.12.0",
        "tqdm>=4.64.0"
    ]
    
    print("Installing core dependencies...")
    failed_core = []
    for package in core_packages:
        print(f"Installing {package}...")
        if not install_package(package):
            failed_core.append(package)
            print(f"Failed to install {package}")
    
    print("\nInstalling optional dependencies...")
    failed_optional = []
    for package in optional_packages:
        print(f"Installing {package}...")
        if not install_package(package):
            failed_optional.append(package)
            print(f"Failed to install {package} (optional)")
    
    print("\n" + "="*60)
    print("INSTALLATION SUMMARY")
    print("="*60)
    
    if not failed_core:
        print("✓ All core dependencies installed successfully!")
    else:
        print("✗ Some core dependencies failed to install:")
        for package in failed_core:
            print(f"  - {package}")
    
    if failed_optional:
        print("\n⚠ Some optional dependencies failed to install:")
        for package in failed_optional:
            print(f"  - {package}")
        print("\nThe system will work with reduced functionality.")
    
    print("\nSetting up TextBlob...")
    try:
        import textblob
        textblob.download_corpora()
        print("✓ TextBlob corpora downloaded successfully!")
    except:
        print("⚠ TextBlob corpora download failed. Run 'python -m textblob.download_corpora' manually.")
    
    print("\nInstallation complete!")
    print("You can now run the system using:")
    print("  python main_minimal.py  (recommended)")
    print("  python test_basic.py    (for testing)")


if __name__ == "__main__":
    main()
