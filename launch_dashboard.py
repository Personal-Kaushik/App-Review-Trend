"""
Launch script for the Interactive Web Dashboard.
Run this if you want to start only the dashboard server using existing data.
"""
import os
import sys
import argparse
from web_dashboard import create_and_run_dashboard


def main():
    """Launch the web dashboard."""
    parser = argparse.ArgumentParser(description='Launch Interactive Review Analysis Dashboard')
    parser.add_argument('--output-dir', '-o', default='output', 
                       help='Directory containing analysis data (default: output)')
    parser.add_argument('--port', '-p', type=int, default=5000,
                       help='Port to run the server on (default: 5000)')
    
    args = parser.parse_args()
    
    # Check if output directory exists
    if not os.path.exists(args.output_dir):
        print(f"❌ Output directory '{args.output_dir}' not found!")
        print("🔍 Please run the main analysis first or specify correct output directory")
        print("📋 Example: python launch_dashboard.py -o /path/to/your/output")
        return
    
    # Check if analysis data exists
    required_files = ['analysis_summary.json']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(args.output_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Required analysis files not found in '{args.output_dir}':")
        for file in missing_files:
            print(f"   - {file}")
        print("\n🔍 Please run the main analysis first:")
        print("   python main.py")
        return
    
    print("🚀 Launching Interactive Web Dashboard")
    print(f"📁 Using data from: {os.path.abspath(args.output_dir)}")
    print(f"🌐 Server will start on port: {args.port}")
    print("=" * 50)
    
    try:
        create_and_run_dashboard(args.output_dir, args.port)
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")


if __name__ == "__main__":
    main()
