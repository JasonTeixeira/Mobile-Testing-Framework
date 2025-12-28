"""
Appium Driver Manager
Handles creating and managing Appium drivers for iOS and Android
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from typing import Optional
import yaml
from pathlib import Path
from loguru import logger


class DriverManager:
    """
    Manages Appium driver creation and configuration.
    
    Handles the differences between iOS and Android setup,
    capabilities, and connection details.
    """
    
    def __init__(self, config_path: str = "config/capabilities.yaml"):
        """
        Initialize with config file path.
        
        Args:
            config_path: Path to YAML config file with capabilities
        """
        self.config_path = Path(config_path)
        self.driver: Optional[webdriver.Remote] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                logger.info(f"Loaded config from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}")
            self.config = {}
    
    def create_android_driver(
        self,
        app_path: Optional[str] = None,
        device_name: Optional[str] = None,
        custom_caps: Optional[dict] = None
    ) -> webdriver.Remote:
        """
        Create Android driver with UiAutomator2.
        
        Args:
            app_path: Path to .apk file (optional if testing installed app)
            device_name: Specific device to use (optional)
            custom_caps: Additional capabilities to override defaults
        
        Returns:
            Configured Appium driver for Android
        """
        logger.info("Creating Android driver...")
        
        # Start with config file capabilities
        caps = self.config.get('android', {}).copy()
        
        # Override with method parameters
        if app_path:
            caps['app'] = app_path
        if device_name:
            caps['deviceName'] = device_name
        if custom_caps:
            caps.update(custom_caps)
        
        # Set defaults if not specified
        caps.setdefault('platformName', 'Android')
        caps.setdefault('automationName', 'UiAutomator2')
        caps.setdefault('deviceName', 'Android Emulator')
        caps.setdefault('newCommandTimeout', 300)
        
        # UiAutomator2 options
        options = UiAutomator2Options()
        options.load_capabilities(caps)
        
        # Connect to Appium server
        appium_url = caps.get('appiumUrl', 'http://localhost:4723')
        
        try:
            self.driver = webdriver.Remote(
                command_executor=appium_url,
                options=options
            )
            logger.success(f"Android driver created: {device_name or 'default device'}")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to create Android driver: {e}")
            raise
    
    def create_ios_driver(
        self,
        app_path: Optional[str] = None,
        device_name: Optional[str] = None,
        custom_caps: Optional[dict] = None
    ) -> webdriver.Remote:
        """
        Create iOS driver with XCUITest.
        
        Args:
            app_path: Path to .app or .ipa file
            device_name: Specific device/simulator to use
            custom_caps: Additional capabilities to override defaults
        
        Returns:
            Configured Appium driver for iOS
        """
        logger.info("Creating iOS driver...")
        
        # Start with config file capabilities
        caps = self.config.get('ios', {}).copy()
        
        # Override with method parameters
        if app_path:
            caps['app'] = app_path
        if device_name:
            caps['deviceName'] = device_name
        if custom_caps:
            caps.update(custom_caps)
        
        # Set defaults if not specified
        caps.setdefault('platformName', 'iOS')
        caps.setdefault('automationName', 'XCUITest')
        caps.setdefault('deviceName', 'iPhone 14')
        caps.setdefault('newCommandTimeout', 300)
        
        # XCUITest options
        options = XCUITestOptions()
        options.load_capabilities(caps)
        
        # Connect to Appium server
        appium_url = caps.get('appiumUrl', 'http://localhost:4723')
        
        try:
            self.driver = webdriver.Remote(
                command_executor=appium_url,
                options=options
            )
            logger.success(f"iOS driver created: {device_name or 'default device'}")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to create iOS driver: {e}")
            raise
    
    def create_driver(
        self,
        platform: str,
        app_path: Optional[str] = None,
        device_name: Optional[str] = None,
        custom_caps: Optional[dict] = None
    ) -> webdriver.Remote:
        """
        Create driver for specified platform.
        
        Args:
            platform: 'android' or 'ios'
            app_path: Path to app file
            device_name: Specific device to use
            custom_caps: Additional capabilities
        
        Returns:
            Configured Appium driver
        """
        platform = platform.lower()
        
        if platform == 'android':
            return self.create_android_driver(app_path, device_name, custom_caps)
        elif platform == 'ios':
            return self.create_ios_driver(app_path, device_name, custom_caps)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def quit_driver(self):
        """Safely quit the driver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver quit successfully")
            except Exception as e:
                logger.warning(f"Error quitting driver: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures driver cleanup."""
        self.quit_driver()
