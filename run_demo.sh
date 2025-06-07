#!/bin/bash

# Reddit Scraper - Complete Demo Script
# This script demonstrates all features of the Reddit Scraper

echo "🚀 Reddit Scraper - Complete Feature Demo"
echo "=========================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Please run this script from the reddit-scraper directory"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🔧 Setting up configuration..."
python run.py create-config

echo ""
echo "⚠️  IMPORTANT: Please edit config/settings.yaml with your Reddit API credentials"
echo "   1. Go to https://www.reddit.com/prefs/apps"
echo "   2. Create a new app (script type)"
echo "   3. Copy client_id and client_secret to config/settings.yaml"
echo ""
read -p "Press Enter after configuring your Reddit API credentials..."

echo ""
echo "🔍 Testing Reddit API connection..."
python run.py test-connection

echo ""
echo "🎯 Running feature demonstrations..."

echo ""
echo "1️⃣  Basic Scraping Demo"
python run.py scrape --subreddit python --posts 10

echo ""
echo "2️⃣  HTML Report Demo (with dark theme and charts)"
python run.py scrape --subreddit programming --posts 15 --output html

echo ""
echo "3️⃣  Parallel Processing Demo"
python run.py scrape --subreddit "python,datascience,programming" --posts 8 --parallel --max-workers 3

echo ""
echo "4️⃣  Content Extraction Demo"
python run.py scrape --subreddit technology --posts 10 --extract-content

echo ""
echo "5️⃣  Performance Monitoring Demo"
python run.py scrape --subreddit datascience --posts 12 --performance-monitor

echo ""
echo "6️⃣  All Features Combined Demo"
python run.py scrape --subreddit "python,programming" --posts 10 --parallel --extract-content --include-users --performance-monitor --output "json,csv,html" --min-score 5

echo ""
echo "🧪 Running Tests..."
python run_tests.py --unit

echo ""
echo "📊 Running Performance Benchmarks..."
python run_tests.py --benchmark

echo ""
echo "🎉 Demo Complete!"
echo "=================="

echo ""
echo "📁 Generated Files:"
echo "• output/html/ - Interactive HTML reports (open in browser)"
echo "• output/json/ - Structured JSON data"
echo "• output/csv/ - Spreadsheet-compatible data"
echo "• logs/ - Performance metrics and logs"
echo "• htmlcov/ - Test coverage reports"

echo ""
echo "🌟 Key Features Demonstrated:"
echo "✅ HTML reports with dark theme and interactive charts"
echo "✅ Parallel processing for 5x faster scraping"
echo "✅ Content extraction from external links"
echo "✅ Performance monitoring and optimization"
echo "✅ Comprehensive testing suite"
echo "✅ Multiple export formats"

echo ""
echo "🔗 Next Steps:"
echo "1. Open output/html/*.html files in your browser"
echo "2. Analyze data in output/csv/ with Excel/Google Sheets"
echo "3. Use output/json/ data for further processing"
echo "4. Review performance metrics in logs/"

echo ""
echo "💡 Pro Tips:"
echo "• Use --parallel for multiple subreddits"
echo "• Add --extract-content for rich data"
echo "• Enable --performance-monitor for optimization"
echo "• Try --output html for beautiful reports"

echo ""
echo "📖 For more information, see README.md"
echo "🐛 Report issues at: https://github.com/pixelbrow720/reddit-scraper"