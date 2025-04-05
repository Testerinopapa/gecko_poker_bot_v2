#!/usr/bin/env python3
"""
Test script for the GeckoBot main function
"""

import os
import sys
from logger import get_logger

def main():
    """Test the main function"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get logger
    logger = get_logger()
    
    # Debug print
    print(f"Logger initialized with session ID: {logger.session_id}")
    print(f"Log directory: {logger.log_dir}")
    print(f"Log directory exists: {os.path.exists(logger.log_dir)}")
    
    # Log some messages
    logger.info("Starting test_main.py")
    
    # Save session data
    logger.save_session_data()
    
    # Debug print
    print(f"Session data saved to: {os.path.join(logger.log_dir, f'geckobot_{logger.session_id}_data.json')}")
    print(f"File exists: {os.path.exists(os.path.join(logger.log_dir, f'geckobot_{logger.session_id}_data.json'))}")
    
    # Check if files were created
    log_files = os.listdir('logs')
    print(f"Log files: {log_files}")
    
    # Print success message
    print("Test completed successfully!")

if __name__ == "__main__":
    main()
