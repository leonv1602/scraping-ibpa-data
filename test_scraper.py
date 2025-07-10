#!/usr/bin/env python3
"""
Test Script for PHEI Yield Curve Scraper
========================================

Simple test script to validate scraper functionality before deployment.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add current directory to path to import scraper
sys.path.insert(0, '.')

try:
    from scrape_yield_curve_github import PHEIYieldCurveScraper, YieldCurveProcessor, DataExporter, Config
    print("✅ Successfully imported scraper modules")
except ImportError as e:
    print(f"❌ Failed to import scraper modules: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic scraper functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test scraper initialization
        scraper = PHEIYieldCurveScraper(timeout=10)
        print("✅ Scraper initialization: OK")
        
        # Test processor initialization
        processor = YieldCurveProcessor()
        print("✅ Processor initialization: OK")
        
        # Test configuration
        assert hasattr(Config, 'BASE_URL')
        assert hasattr(Config, 'MONTH_MAPPING')
        print("✅ Configuration: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_data_fetching():
    """Test data fetching from PHEI website."""
    print("\n🌐 Testing data fetching...")
    
    try:
        scraper = PHEIYieldCurveScraper(timeout=15)
        
        # Fetch data
        html_text, df_list = scraper.fetch_webpage(Config.BASE_URL)
        
        # Validate response
        assert isinstance(html_text, str)
        assert len(html_text) > 1000  # Should be substantial HTML
        assert isinstance(df_list, list)
        assert len(df_list) >= 2  # Should have at least 2 tables
        
        print(f"✅ Data fetching: OK ({len(df_list)} tables)")
        
        # Test date extraction
        date = scraper.extract_date(html_text)
        assert isinstance(date, str)
        assert len(date.split('-')) == 3  # Should be day-month-year format
        
        print(f"✅ Date extraction: OK ({date})")
        
        return True, html_text, df_list
        
    except Exception as e:
        print(f"❌ Data fetching test failed: {e}")
        return False, None, None

def test_data_processing(df_list):
    """Test data processing functionality."""
    print("\n📊 Testing data processing...")
    
    try:
        processor = YieldCurveProcessor()
        
        # Process yield curve data
        yield_df = processor.process_yield_curve_data(df_list)
        
        # Validate processed data
        assert not yield_df.empty
        assert 'IBPA_Yield' in yield_df.columns
        assert len(yield_df) >= Config.MIN_TENORS
        assert yield_df['IBPA_Yield'].min() >= Config.MIN_YIELD
        assert yield_df['IBPA_Yield'].max() <= Config.MAX_YIELD
        
        print(f"✅ Yield curve processing: OK ({len(yield_df)} tenors)")
        
        # Test spot rate calculation
        spot_rates = processor.calculate_spot_rates(yield_df)
        assert len(spot_rates) == len(yield_df)
        
        print("✅ Spot rate calculation: OK")
        
        # Test forward rate calculation
        forward_rates = processor.calculate_forward_rates(spot_rates, yield_df.index.values)
        assert len(forward_rates) == len(yield_df) - 1
        
        print("✅ Forward rate calculation: OK")
        
        return True, yield_df
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False, None

def test_data_export(yield_df):
    """Test data export functionality."""
    print("\n💾 Testing data export...")
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            exporter = DataExporter(temp_path)
            
            # Test JSON export
            test_data = {
                'metadata': {'test': True},
                'yield_curve': yield_df.reset_index().to_dict('records')
            }
            
            success_json = exporter.export_to_json(test_data, 'test')
            assert success_json
            
            json_file = temp_path / 'test.json'
            assert json_file.exists()
            
            # Validate JSON content
            with open(json_file, 'r') as f:
                loaded_data = json.load(f)
                assert 'metadata' in loaded_data
                assert 'yield_curve' in loaded_data
            
            print("✅ JSON export: OK")
            
            # Test CSV export
            success_csv = exporter.export_to_csv(yield_df, 'test')
            assert success_csv
            
            csv_file = temp_path / 'test.csv'
            assert csv_file.exists()
            
            print("✅ CSV export: OK")
            
        return True
        
    except Exception as e:
        print(f"❌ Data export test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 PHEI Yield Curve Scraper Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed")
        return 1
    
    # Test data fetching
    success, html_text, df_list = test_data_fetching()
    if not success:
        print("\n❌ Data fetching tests failed")
        print("💡 This might be due to network issues or website changes")
        return 1
    
    # Test data processing
    success, yield_df = test_data_processing(df_list)
    if not success:
        print("\n❌ Data processing tests failed")
        return 1
    
    # Test data export
    if not test_data_export(yield_df):
        print("\n❌ Data export tests failed")
        return 1
    
    # All tests passed
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Scraper is ready for GitHub Actions deployment")
    print("=" * 50)
    
    # Print summary
    print(f"\n📊 Test Results Summary:")
    print(f"   • Yield curve tenors: {len(yield_df)}")
    print(f"   • Yield range: {yield_df['IBPA_Yield'].min():.4f} - {yield_df['IBPA_Yield'].max():.4f}")
    print(f"   • Data source: {Config.BASE_URL}")
    print(f"   • Configuration: Valid")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
