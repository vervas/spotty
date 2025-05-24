#!/usr/bin/env python3
"""
Main module for Spotty - Home Assistant NFC Bridge
"""

import argparse
import logging
import os
import signal
import sys
import time
import yaml
import requests
import json
from .nfc_reader import PN532Reader
from .ha_client import HomeAssistantClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("spotty")

# Default configuration
DEFAULT_CONFIG = {
    "device": "/dev/ttyAMA0",
    "ha_url": "http://supervisor/core",
    "scan_interval": 0.5,
    "log_level": "INFO",
    "token_file": "/config/spotty_token.txt"
}

class SpottyService:
    """Main service class for Spotty NFC bridge"""
    
    def __init__(self, config_path=None):
        """Initialize the service"""
        self.running = False
        self.config = DEFAULT_CONFIG.copy()
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config and isinstance(user_config, dict):
                        self.config.update(user_config)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Set log level
        log_level = getattr(logging, self.config["log_level"].upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Initialize components
        self.nfc_reader = None
        self.ha_client = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def initialize(self):
        """Initialize components"""
        try:
            # Initialize NFC reader
            logger.info(f"Initializing NFC reader on {self.config['device']}")
            self.nfc_reader = PN532Reader(self.config["device"])
            
            # Initialize Home Assistant client
            logger.info(f"Connecting to Home Assistant at {self.config['ha_url']}")
            
            # When running as an add-on, no token is needed
            token = self._get_token()
            self.ha_client = HomeAssistantClient(
                self.config["ha_url"], 
                token
            )
            
            # Test Home Assistant connection
            if not self.ha_client.test_connection():
                logger.error("Failed to connect to Home Assistant. Check URL and token.")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    def _get_token(self):
        """Get the Home Assistant long-lived access token"""
        # Check if running as a Home Assistant add-on
        is_addon = os.path.exists("/var/run/s6/services")
        
        if is_addon:
            # When running as an add-on, use the SUPERVISOR_TOKEN environment variable
            logger.info("Running as Home Assistant add-on, using SUPERVISOR_TOKEN")
            supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
            if supervisor_token:
                return supervisor_token
            else:
                logger.warning("SUPERVISOR_TOKEN environment variable not found")
            
        # Running standalone or SUPERVISOR_TOKEN not found, try to get token from file
        token_file = self.config.get("token_file", "/config/spotty_token.txt")
        
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"Error reading token file: {e}")
        
        if not is_addon:  # Only show these warnings if not running as an add-on
            logger.warning(f"Token file not found: {token_file}")
            logger.warning("Please create a long-lived access token in Home Assistant")
            logger.warning(f"and save it to {token_file}")
        return None
    
    def run(self):
        """Main service loop"""
        if not self.initialize():
            logger.error("Failed to initialize. Exiting.")
            return 1
        
        logger.info("Spotty NFC bridge started")
        self.running = True
        
        try:
            while self.running:
                # Read NFC tag
                uid = self.nfc_reader.read_tag(timeout=self.config["scan_interval"])
                
                if uid:
                    tag_id = "_".join([hex(i) for i in uid])
                    logger.info(f"Tag detected: {tag_id}")
                    
                    # Send to Home Assistant
                    success = self.ha_client.tag_scanned(f"nfc_{tag_id}")
                    if success:
                        logger.info(f"Tag {tag_id} registered with Home Assistant")
                    else:
                        logger.error(f"Failed to register tag {tag_id} with Home Assistant")
                    
                    # Prevent multiple reads of the same tag
                    time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            return 1
        finally:
            # Cleanup
            if self.nfc_reader:
                self.nfc_reader.cleanup()
            
            logger.info("Spotty NFC bridge stopped")
        
        return 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Spotty - Home Assistant NFC Bridge")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    service = SpottyService(args.config)
    return service.run()

if __name__ == "__main__":
    sys.exit(main())
