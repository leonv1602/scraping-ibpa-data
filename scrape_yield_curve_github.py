#!/usr/bin/env python3
"""
PHEI Yield Curve Data Scraper - Optimized for GitHub Actions
============================================================

This script scrapes Indonesian government bond yield curve data from PHEI website,
calculates spot rates and forward rates, and saves the results in multiple formats.

Optimized for:
- GitHub Actions automation
- Minimal dependencies
- Fast execution
- Robust error handling
- JSON and CSV output for easy processing

Author: GitHub Actions Bot
Version: 1.0
Last Updated: July 2025
"""

import json
import csv
import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import os

# Core data processing
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

# Configure logging for GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Configuration class for the scraper."""
    
    # URLs and endpoints
    BASE_URL = "https://www.phei.co.id/Data/HPW-dan-Imbal-Hasil"
    TIMEOUT = 30
    
    # Month mapping for Indonesian dates
    MONTH_MAPPING = {
        "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
        "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
        "September": "09", "Oktober": "10", "November": "11", "Desember": "12"
    }
    
    # Output configuration
    OUTPUT_DIR = "data"
    HISTORICAL_DIR = "historical"
    
    # Data validation thresholds
    MIN_YIELD = 0.0001  # 0.01%
    MAX_YIELD = 0.5     # 50%
    MIN_TENORS = 3      # Minimum number of tenor points required

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def setup_directories(base_dir: str = "data") -> Dict[str, Path]:
    """Create directory structure for outputs."""
    base_path = Path(base_dir)
    directories = {
        'main': base_path,
        'daily': base_path / 'daily',
        'historical': base_path / 'historical',
        'logs': base_path / 'logs'
    }
    
    for name, path in directories.items():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {path}")
    
    return directories

def format_date_for_path(date_str: str) -> str:
    """Convert Indonesian date format to YYYY-MM-DD."""
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            raise ValueError(f"Invalid date format: {date_str}")
        
        day, month, year = parts
        month_num = Config.MONTH_MAPPING.get(month, "01")
        return f"{year}-{month_num.zfill(2)}-{day.zfill(2)}"
    except Exception as e:
        logger.error(f"Error formatting date {date_str}: {e}")
        return datetime.now().strftime("%Y-%m-%d")

def clean_date_format(raw_date: str) -> str:
    """Clean date string by adding leading zero if needed."""
    parts = raw_date.split('-')
    if len(parts[0]) == 1:
        parts[0] = '0' + parts[0]
    return '-'.join(parts)

# =============================================================================
# DATA SCRAPING
# =============================================================================

class PHEIYieldCurveScraper:
    """Scraper class for PHEI yield curve data."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (GitHub Actions Bot) AppleWebKit/537.36'
        })
    
    def fetch_webpage(self, url: str) -> Tuple[str, List[pd.DataFrame]]:
        """Fetch webpage and extract tables."""
        try:
            logger.info(f"Fetching data from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML content
            html_content = response.content
            text_content = response.text
            
            # Extract tables using pandas
            df_list = pd.read_html(html_content)
            logger.info(f"Successfully extracted {len(df_list)} tables")
            
            return text_content, df_list
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {e}")
            raise
    
    def extract_date(self, html_text: str) -> str:
        """Extract date from PHEI HTML."""
        try:
            import re
            # Look for the specific date div
            pattern = r'<div id="dnn_ctr1477_GovernmentBondBenchmark_idIGSYC_tdTgl">'
            match = re.search(pattern, html_text)
            
            if not match:
                logger.warning("Date pattern not found, using current date")
                return datetime.now().strftime("%d-%B-%Y")
            
            start_pos = match.start()
            date_section = html_text[start_pos:start_pos + 100]
            raw_date = date_section.split(' ')[-2]
            split_pos = raw_date.find('<')
            clean_date = raw_date[:split_pos]
            
            return clean_date_format(clean_date)
            
        except Exception as e:
            logger.error(f"Error extracting date: {e}")
            return datetime.now().strftime("%d-%B-%Y")

# =============================================================================
# DATA PROCESSING
# =============================================================================

class YieldCurveProcessor:
    """Process and calculate yield curve metrics."""
    
    @staticmethod
    def process_yield_curve_data(df_list: List[pd.DataFrame]) -> pd.DataFrame:
        """Process yield curve data from scraped tables."""
        try:
            if len(df_list) < 2:
                raise ValueError("Insufficient tables for yield curve processing")
            
            # Combine first two tables (typically government bond data)
            combined_df = pd.concat([df_list[0], df_list[1]], axis=0, ignore_index=True)
            
            # Validate required columns
            required_cols = ['Tenor Year', 'Today']
            if not all(col in combined_df.columns for col in required_cols):
                raise ValueError(f"Required columns not found: {required_cols}")
            
            # Extract and clean data
            df = combined_df[required_cols].copy()
            
            # Data normalization
            df['Tenor Year'] = pd.to_numeric(df['Tenor Year'], errors='coerce') / 10
            df['Today'] = pd.to_numeric(df['Today'], errors='coerce') / 1e6
            
            # Remove invalid data
            df = df.dropna()
            df = df[df['Tenor Year'] > 0]
            df = df[df['Today'].between(Config.MIN_YIELD, Config.MAX_YIELD)]
            
            # Remove duplicates and sort
            df = df.drop_duplicates(subset=['Tenor Year']).sort_values('Tenor Year')
            
            # Rename for clarity
            df.rename(columns={'Today': 'IBPA_Yield'}, inplace=True)
            df.set_index('Tenor Year', inplace=True)
            
            if len(df) < Config.MIN_TENORS:
                raise ValueError(f"Insufficient data points: {len(df)} < {Config.MIN_TENORS}")
            
            logger.info(f"Processed yield curve: {len(df)} tenors, range {df.index.min():.1f}-{df.index.max():.1f} years")
            return df
            
        except Exception as e:
            logger.error(f"Error processing yield curve data: {e}")
            raise
    
    @staticmethod
    def calculate_spot_rates(yield_df: pd.DataFrame) -> np.ndarray:
        """Calculate spot rates using bootstrapping method."""
        try:
            yields = yield_df.values.flatten()
            tenors = yield_df.index.values
            spot_rates = yields.copy()
            
            # Bootstrap calculation
            for i in range(2, len(yields)):
                coupon_pv = 0
                current_yield = yields[i]
                current_tenor = tenors[i]
                
                # Calculate present value of coupon payments
                for j in range(1, i):
                    coupon_pv += current_yield / ((1 + spot_rates[j]) ** tenors[j])
                
                # Calculate spot rate
                numerator = 1 + current_yield - coupon_pv
                denominator = 1 + coupon_pv
                
                if denominator > 0:
                    spot_rates[i] = (numerator / denominator) ** (1 / current_tenor) - 1
                else:
                    spot_rates[i] = yields[i]
            
            logger.info(f"Calculated spot rates: range {spot_rates.min():.4f}-{spot_rates.max():.4f}")
            return spot_rates
            
        except Exception as e:
            logger.error(f"Error calculating spot rates: {e}")
            return yield_df.values.flatten()
    
    @staticmethod
    def calculate_forward_rates(spot_rates: np.ndarray, tenors: np.ndarray) -> np.ndarray:
        """Calculate forward rates from spot rates."""
        try:
            if len(spot_rates) < 2:
                return np.array([])
            
            forward_rates = []
            
            for i in range(1, len(spot_rates)):
                t1, t2 = tenors[i-1], tenors[i]
                s1, s2 = spot_rates[i-1], spot_rates[i]
                
                if t2 > t1 and (1 + s1) > 0:
                    period_diff = t2 - t1
                    if period_diff > 0:
                        forward_rate = ((1 + s2) ** t2 / (1 + s1) ** t1) ** (1 / period_diff) - 1
                        forward_rates.append(forward_rate)
                    else:
                        forward_rates.append(0)
                else:
                    forward_rates.append(0)
            
            logger.info(f"Calculated forward rates: {len(forward_rates)} periods")
            return np.array(forward_rates)
            
        except Exception as e:
            logger.error(f"Error calculating forward rates: {e}")
            return np.array([])

# =============================================================================
# DATA EXPORT
# =============================================================================

class DataExporter:
    """Export data in various formats."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def export_to_json(self, data: Dict, filename: str) -> bool:
        """Export data to JSON file."""
        try:
            filepath = self.output_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Exported JSON: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting JSON {filename}: {e}")
            return False
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """Export DataFrame to CSV file."""
        try:
            filepath = self.output_dir / f"{filename}.csv"
            df.to_csv(filepath, index=True)
            logger.info(f"Exported CSV: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting CSV {filename}: {e}")
            return False
    
    def create_github_summary(self, data: Dict, date_str: str) -> bool:
        """Create GitHub Actions job summary."""
        try:
            summary_path = Path(os.environ.get('GITHUB_STEP_SUMMARY', 'summary.md'))
            
            with open(summary_path, 'w') as f:
                f.write(f"# PHEI Yield Curve Data - {date_str}\n\n")
                f.write(f"## 📊 Data Summary\n\n")
                f.write(f"- **Date**: {date_str}\n")
                f.write(f"- **Tenors**: {data.get('tenor_count', 0)}\n")
                f.write(f"- **Yield Range**: {data.get('yield_min', 0):.4f} - {data.get('yield_max', 0):.4f}\n")
                f.write(f"- **Status**: {data.get('status', 'Unknown')}\n\n")
                
                if 'key_metrics' in data:
                    f.write(f"## 🎯 Key Metrics\n\n")
                    for metric, value in data['key_metrics'].items():
                        f.write(f"- **{metric}**: {value}\n")
                
                f.write(f"\n## 📁 Output Files\n\n")
                for file_type in ['JSON', 'CSV']:
                    f.write(f"- {file_type}: `data/daily/{date_str}_yield_curve.{file_type.lower()}`\n")
            
            logger.info(f"Created GitHub summary: {summary_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating GitHub summary: {e}")
            return False

# =============================================================================
# MAIN SCRAPING PIPELINE
# =============================================================================

def main():
    """Main scraping pipeline optimized for GitHub Actions."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PHEI Yield Curve Scraper')
    parser.add_argument('--output-dir', default='data', help='Output directory')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("PHEI Yield Curve Scraper - GitHub Actions")
    logger.info("=" * 60)
    
    try:
        # Setup directories
        directories = setup_directories(args.output_dir)
        
        # Initialize scraper
        scraper = PHEIYieldCurveScraper(timeout=args.timeout)
        processor = YieldCurveProcessor()
        exporter = DataExporter(directories['daily'])
        
        # Fetch data
        html_text, df_list = scraper.fetch_webpage(Config.BASE_URL)
        
        # Extract date
        raw_date = scraper.extract_date(html_text)
        formatted_date = format_date_for_path(raw_date)
        
        logger.info(f"Processing data for date: {raw_date} ({formatted_date})")
        
        # Process yield curve
        yield_curve_df = processor.process_yield_curve_data(df_list)
        
        # Calculate rates
        spot_rates = processor.calculate_spot_rates(yield_curve_df)
        forward_rates = processor.calculate_forward_rates(spot_rates, yield_curve_df.index.values)
        
        # Add calculated rates to DataFrame
        yield_curve_df['Spot_Rate'] = spot_rates
        
        # Pad forward rates with NaN for first period
        forward_rates_padded = np.concatenate([[np.nan], forward_rates])
        yield_curve_df['Forward_Rate'] = forward_rates_padded
        
        # Prepare export data
        export_data = {
            'metadata': {
                'date': raw_date,
                'formatted_date': formatted_date,
                'scrape_timestamp': start_time.isoformat(),
                'source_url': Config.BASE_URL,
                'tenor_count': len(yield_curve_df),
                'status': 'success'
            },
            'yield_curve': yield_curve_df.reset_index().to_dict('records'),
            'key_metrics': {
                'Current 10Y Yield': f"{yield_curve_df.loc[yield_curve_df.index >= 10, 'IBPA_Yield'].iloc[0]:.4f}" if len(yield_curve_df[yield_curve_df.index >= 10]) > 0 else "N/A",
                'Average Spot Rate': f"{np.nanmean(spot_rates):.4f}",
                'Average Forward Rate': f"{np.nanmean(forward_rates):.4f}" if len(forward_rates) > 0 else "N/A",
                'Yield Range': f"{yield_curve_df['IBPA_Yield'].max() - yield_curve_df['IBPA_Yield'].min():.4f}",
                'Steepness (10Y-2Y)': "N/A"  # Calculate if data available
            }
        }
        
        # Calculate steepness if data available
        try:
            y2 = yield_curve_df.loc[yield_curve_df.index >= 2, 'IBPA_Yield'].iloc[0]
            y10 = yield_curve_df.loc[yield_curve_df.index >= 10, 'IBPA_Yield'].iloc[0]
            export_data['key_metrics']['Steepness (10Y-2Y)'] = f"{(y10 - y2) * 10000:.0f}bp"
        except:
            pass
        
        # Export data
        filename_base = f"{formatted_date}_yield_curve"
        
        success_json = exporter.export_to_json(export_data, filename_base)
        success_csv = exporter.export_to_csv(yield_curve_df, filename_base)
        
        # Create GitHub Actions summary
        summary_data = export_data['metadata'].copy()
        summary_data.update({
            'yield_min': yield_curve_df['IBPA_Yield'].min(),
            'yield_max': yield_curve_df['IBPA_Yield'].max(),
            'key_metrics': export_data['key_metrics']
        })
        
        exporter.create_github_summary(summary_data, formatted_date)
        
        # Final summary
        execution_time = datetime.now() - start_time
        logger.info("=" * 60)
        logger.info("SCRAPING COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Date: {raw_date} ({formatted_date})")
        logger.info(f"Tenors processed: {len(yield_curve_df)}")
        logger.info(f"Execution time: {execution_time.total_seconds():.2f} seconds")
        logger.info(f"JSON export: {'✅' if success_json else '❌'}")
        logger.info(f"CSV export: {'✅' if success_csv else '❌'}")
        
        # Set GitHub Actions outputs
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"date={formatted_date}\n")
                f.write(f"tenor_count={len(yield_curve_df)}\n")
                f.write(f"status=success\n")
                f.write(f"filename={filename_base}\n")
        
        return 0
        
    except Exception as e:
        execution_time = datetime.now() - start_time
        logger.error("=" * 60)
        logger.error("SCRAPING FAILED")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        logger.error(f"Execution time: {execution_time.total_seconds():.2f} seconds")
        
        # Set GitHub Actions outputs for failure
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"status=failed\n")
                f.write(f"error={str(e)}\n")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
