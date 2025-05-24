#!/usr/bin/env python3
"""
Home Assistant client module for communicating with the Home Assistant API
"""

import logging
import requests
import json
import os

logger = logging.getLogger("spotty.ha_client")

class HomeAssistantClient:
    """Client for interacting with the Home Assistant API"""
    
    def __init__(self, base_url, token=None, device_id="spotty_nfc_reader"):
        """Initialize the Home Assistant client
        
        When running as a Home Assistant add-on, no token is needed as we can use
        the Supervisor API which provides access to Home Assistant.
        """
        self.base_url = base_url.rstrip('/')
        self.device_id = device_id
        
        # Check if running as a Home Assistant add-on
        self.is_addon = os.path.exists("/var/run/s6/services")
        
        if self.is_addon:
            # Running as an add-on, use Supervisor API
            logger.info("Running as Home Assistant add-on, using Supervisor API")
            self.headers = {
                "Content-Type": "application/json",
                # The Supervisor API token is automatically injected by the add-on system
                "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}"
            }
        elif token:
            # Running standalone, use provided token
            logger.info("Running standalone, using provided token")
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        else:
            # No authentication available, but still try to connect
            # This might work for local unsecured Home Assistant instances
            logger.warning("No authentication token available, attempting to connect without authentication")
            self.headers = {"Content-Type": "application/json"}
    
    def test_connection(self):
        """Test the connection to Home Assistant"""
        try:
            response = requests.get(
                f"{self.base_url}/api/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Successfully connected to Home Assistant")
                return True
            else:
                logger.error(f"Failed to connect to Home Assistant: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to Home Assistant: {e}")
            return False
    
    def tag_scanned(self, tag_id):
        """Send a tag_scanned event to Home Assistant"""
        try:
            # Prepare the event data
            data = {
                "tag_id": tag_id,
                "device_id": self.device_id
            }
            
            # Send the event
            response = requests.post(
                f"{self.base_url}/api/events/tag_scanned",
                headers=self.headers,
                data=json.dumps(data),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"Successfully sent tag_scanned event for {tag_id}")
                return True
            else:
                logger.error(f"Failed to send tag_scanned event: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending tag_scanned event: {e}")
            return False
    
    def call_service(self, domain, service, service_data=None):
        """Call a service in Home Assistant"""
        try:
            # Prepare the service data
            data = service_data or {}
            
            # Call the service
            response = requests.post(
                f"{self.base_url}/api/services/{domain}/{service}",
                headers=self.headers,
                data=json.dumps(data),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"Successfully called service {domain}.{service}")
                return True
            else:
                logger.error(f"Failed to call service {domain}.{service}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error calling service {domain}.{service}: {e}")
            return False
