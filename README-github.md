# 🇮🇩 PHEI Yield Curve Data Scraper

[![Scrape PHEI Data](https://github.com/YOUR_USERNAME/scraping-ibpa-data/actions/workflows/scrape-yield-curve.yml/badge.svg)](https://github.com/YOUR_USERNAME/scraping-ibpa-data/actions/workflows/scrape-yield-curve.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Automated scraper for Indonesian government bond yield curve data from PHEI (Pusat Harga Efek Indonesia), optimized for GitHub Actions automation.

## 🚀 Features

- **🔄 Automated Daily Scraping**: Runs automatically via GitHub Actions
- **📊 Advanced Calculations**: Spot rates and forward rates using bootstrapping
- **💾 Multiple Export Formats**: JSON, CSV output for easy processing
- **🛡️ Robust Error Handling**: Comprehensive validation and fallback mechanisms
- **📈 GitHub Integration**: Automatic commits, summaries, and dashboards
- **⚡ Fast Execution**: Optimized for minimal dependencies and quick runs
- **🌐 Dashboard**: Optional GitHub Pages deployment for data visualization

## 📅 Automated Schedule

The scraper runs automatically:
- **Daily** at 9:00 AM Jakarta time (02:00 UTC)
- **Weekdays** at 2:00 PM Jakarta time (07:00 UTC)
- **On demand** via workflow dispatch
- **On code changes** to scraper files

## 🏗️ Project Structure

```
├── scrape_yield_curve_github.py    # Main scraper script (GitHub Actions optimized)
├── .github/workflows/
│   └── scrape-yield-curve.yml      # GitHub Actions workflow
├── data/
│   ├── daily/                      # Daily scraped data
│   └── historical/                 # Historical data archive
├── requirements-github.txt         # Minimal dependencies for Actions
├── config.ini                      # Configuration file
└── README-github.md               # This file
```

## 🛠️ Quick Start

### 1. GitHub Repository Setup

1. **Fork or clone** this repository
2. **Enable GitHub Actions** in your repository settings
3. **Set up GitHub Pages** (optional) for the dashboard:
   - Go to Settings → Pages
   - Source: GitHub Actions
4. **Run the workflow** manually or wait for the scheduled run

### 2. Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/scraping-ibpa-data.git
cd scraping-ibpa-data

# Install dependencies
pip install -r requirements-github.txt

# Run the scraper locally
python scrape_yield_curve_github.py --output-dir data --debug
```

### 3. Manual Workflow Trigger

Go to **Actions** → **PHEI Yield Curve Data Scraper** → **Run workflow**

Options:
- `debug`: Enable debug logging
- `timeout`: Request timeout in seconds (default: 30)

## 📊 Output Data

### JSON Output
```json
{
  "metadata": {
    "date": "10-Juli-2025",
    "formatted_date": "2025-07-10",
    "scrape_timestamp": "2025-07-10T09:00:00",
    "source_url": "https://www.phei.co.id/Data/HPW-dan-Imbal-Hasil",
    "tenor_count": 12,
    "status": "success"
  },
  "yield_curve": [
    {
      "Tenor Year": 1.0,
      "IBPA_Yield": 0.0625,
      "Spot_Rate": 0.0625,
      "Forward_Rate": null
    }
  ],
  "key_metrics": {
    "Current 10Y Yield": "0.0720",
    "Average Spot Rate": "0.0680",
    "Average Forward Rate": "0.0695",
    "Yield Range": "0.0145",
    "Steepness (10Y-2Y)": "125bp"
  }
}
```

### CSV Output
| Tenor Year | IBPA_Yield | Spot_Rate | Forward_Rate |
|------------|------------|-----------|--------------|
| 1.0        | 0.0625     | 0.0625    | NaN          |
| 2.0        | 0.0650     | 0.0651    | 0.0675       |
| 5.0        | 0.0700     | 0.0702    | 0.0721       |
| 10.0       | 0.0720     | 0.0723    | 0.0745       |

## 🔧 Configuration

Edit `config.ini` to customize:

```ini
[scraper]
base_url = https://www.phei.co.id/Data/HPW-dan-Imbal-Hasil
timeout = 30

[data_validation]
min_yield = 0.0001
max_yield = 0.5
min_tenors = 3

[output]
export_json = true
export_csv = true

[github_actions]
auto_commit = true
enable_summary = true
```

## 📈 GitHub Actions Workflow

The workflow includes:

1. **🛒 Checkout** - Get latest code
2. **🐍 Python Setup** - Install Python 3.11
3. **📦 Dependencies** - Install minimal requirements
4. **🔍 Scraping** - Run the scraper with error handling
5. **📋 Validation** - Validate output data quality
6. **📊 Summary** - Generate GitHub Actions summary
7. **💾 Commit** - Auto-commit data to repository
8. **📤 Artifacts** - Upload data as artifacts
9. **🌐 Deploy** - Optional GitHub Pages dashboard

## 🎯 Key Features for GitHub Actions

### ⚡ Optimized Performance
- **Minimal dependencies**: Only essential packages
- **Fast startup**: ~30-60 second install time
- **Efficient scraping**: Single request with robust parsing
- **Smart caching**: Pip cache for faster subsequent runs

### 🛡️ Robust Error Handling
- **Network timeouts**: Configurable request timeouts
- **Data validation**: Comprehensive data quality checks
- **Graceful failures**: Detailed error reporting
- **Retry logic**: Built-in retry mechanisms

### 📊 GitHub Integration
- **Action summaries**: Rich markdown summaries in workflow
- **Outputs**: Structured outputs for downstream jobs
- **Artifacts**: Automatic artifact uploads with retention
- **Status badges**: Workflow status in README

### 📁 Data Management
- **Automatic commits**: Auto-commit scraped data
- **Organized structure**: Date-based file organization
- **Historical tracking**: Git-based data versioning
- **Artifact retention**: 30-day artifact storage

## 🔍 Monitoring & Debugging

### View Workflow Runs
1. Go to **Actions** tab in your repository
2. Click on **PHEI Yield Curve Data Scraper**
3. Select a workflow run to see details

### Debug Failed Runs
```bash
# Enable debug mode in workflow dispatch
debug: true

# Or run locally with debug
python scrape_yield_curve_github.py --debug
```

### Check Data Quality
```bash
# Validate latest JSON file
python -c "
import json
with open('data/daily/LATEST_FILE.json') as f:
    data = json.load(f)
    print(f'Tenors: {len(data[\"yield_curve\"])}')
    print(f'Date: {data[\"metadata\"][\"date\"]}')
"
```

## 📊 Dashboard (Optional)

If GitHub Pages is enabled, view your data dashboard at:
`https://YOUR_USERNAME.github.io/scraping-ibpa-data/`

The dashboard provides:
- 📈 Real-time yield curve visualization
- 📊 Key metrics display
- 📅 Historical data access
- 🔄 Automatic updates

## 🔧 Customization

### Modify Scraping Schedule
Edit `.github/workflows/scrape-yield-curve.yml`:

```yaml
on:
  schedule:
    # Custom schedule (cron format)
    - cron: '0 1 * * *'  # Daily at 1 AM UTC
```

### Add Custom Metrics
Extend `export_data['key_metrics']` in the script:

```python
export_data['key_metrics']['Custom_Metric'] = calculate_custom_metric(yield_curve_df)
```

### Change Output Format
Modify the exporter to add new formats:

```python
# Add Excel export
exporter.export_to_excel(yield_curve_df, filename_base)
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality
4. **Update** documentation
5. **Submit** a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PHEI** (Pusat Harga Efek Indonesia) for providing the data
- **GitHub Actions** for the automation platform
- **Indonesian Bond Market** community
- **Claude Sonnet 4** for assistance in generating this documentation


## 📞 Support

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and community support
- **Wiki**: For detailed documentation

---

**Made with ❤️ for the Indonesian financial data community**

[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/scraping-ibpa-data.svg?style=social&label=Star)](https://github.com/YOUR_USERNAME/scraping-ibpa-data)
[![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/scraping-ibpa-data.svg?style=social&label=Fork)](https://github.com/YOUR_USERNAME/scraping-ibpa-data/fork)
