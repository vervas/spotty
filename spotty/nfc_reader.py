#!/usr/bin/env python3
"""
NFC Reader module for interfacing with PN532 hardware
"""

import logging
import time

# Use mock GPIO pins to avoid hardware access issues
from gpiozero import Device
from gpiozero.pins.mock import MockFactory

# Set the pin factory to mock before importing pn532
Device.pin_factory = MockFactory()

# Now import the PN532 library
from pn532 import PN532_UART

logger = logging.getLogger("spotty.nfc_reader")

class PN532Reader:
    """Class for interfacing with PN532 NFC reader via UART"""
    
    def __init__(self, port, baudrate=115200, timeout=1):
        """Initialize the PN532 reader"""
        self.port = port
        self.pn532 = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the PN532 reader"""
        try:
            # Initialize the PN532 using UART
            logger.info(f"Initializing PN532 on {self.port}")
            # Use the same parameters as the example code
            self.pn532 = PN532_UART(self.port, debug=False, reset=20)
            
            # Get firmware version to check connection
            ic, ver, rev, support = self.pn532.get_firmware_version()
            logger.info(f"Found PN532 with firmware version: {ver}.{rev}")
            
            # Configure PN532 to communicate with MiFare cards
            self.pn532.SAM_configuration()
            logger.info("PN532 configured for reading")
                
        except Exception as e:
            logger.error(f"Error initializing PN532: {e}")
            raise
    
    def read_tag(self, timeout=0.5):
        """Read a passive target (ISO14443A card/tag)"""
        try:
            # Check if a card is available to read
            uid = self.pn532.read_passive_target(timeout=timeout)
            
            # Return None if no card is available
            if uid is None:
                return None
                
            logger.debug(f"Found card with UID: {[hex(i) for i in uid]}")
            return uid
            
        except Exception as e:
            logger.error(f"Error reading tag: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        # The pn532 library doesn't have a specific cleanup method
        # but we could add one if needed in the future
        self.pn532 = None
        logger.info("PN532 reader cleaned up")

