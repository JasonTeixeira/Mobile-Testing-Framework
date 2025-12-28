"""
Base Page for Mobile Testing
Provides common mobile interactions and gestures
"""

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.webdriver.common.touch_action import TouchAction
from typing import Tuple, Optional
from loguru import logger
import time


class BasePage:
    """
    Base page with common mobile interactions.
    
    This handles things specific to mobile:
    - Swipes and scrolls
    - Tap and long press
    - Hiding keyboard
    - Waiting for elements
    """
    
    def __init__(self, driver: webdriver.Remote):
        """
        Initialize with Appium driver.
        
        Args:
            driver: Appium Remote WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.touch = TouchAction(driver)
    
    # Element Finding
    def find_element(self, locator: Tuple[str, str], timeout: int = 10):
        """
        Find element with explicit wait.
        
        Args:
            locator: Tuple of (by, value) like (AppiumBy.ID, "com.app:id/button")
            timeout: Max wait time in seconds
        
        Returns:
            WebElement if found
        
        Raises:
            TimeoutException if not found
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            logger.debug(f"Found element: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Element not found: {locator}")
            raise
    
    def find_elements(self, locator: Tuple[str, str]):
        """
        Find multiple elements.
        
        Args:
            locator: Tuple of (by, value)
        
        Returns:
            List of WebElements
        """
        return self.driver.find_elements(*locator)
    
    def is_element_present(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """
        Check if element exists without throwing exception.
        
        Args:
            locator: Element locator
            timeout: How long to wait
        
        Returns:
            True if element found, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    # Basic Interactions
    def tap(self, locator: Tuple[str, str], timeout: int = 10):
        """
        Tap/click an element.
        
        Args:
            locator: Element to tap
            timeout: Wait timeout
        """
        element = self.find_element(locator, timeout)
        element.click()
        logger.info(f"Tapped element: {locator}")
    
    def send_keys(self, locator: Tuple[str, str], text: str, timeout: int = 10):
        """
        Type text into element.
        
        Args:
            locator: Input field locator
            text: Text to type
            timeout: Wait timeout
        """
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        logger.info(f"Typed '{text}' into {locator}")
    
    def get_text(self, locator: Tuple[str, str], timeout: int = 10) -> str:
        """
        Get text from element.
        
        Args:
            locator: Element locator
            timeout: Wait timeout
        
        Returns:
            Element text content
        """
        element = self.find_element(locator, timeout)
        return element.text
    
    # Mobile-Specific Gestures
    def swipe_up(self, duration: int = 800):
        """
        Swipe up (scroll down).
        
        Args:
            duration: Swipe duration in milliseconds
        """
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.2)
        
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        logger.debug("Swiped up")
    
    def swipe_down(self, duration: int = 800):
        """
        Swipe down (scroll up).
        
        Args:
            duration: Swipe duration in milliseconds
        """
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.2)
        end_y = int(size['height'] * 0.8)
        
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        logger.debug("Swiped down")
    
    def swipe_left(self, duration: int = 800):
        """
        Swipe left.
        
        Args:
            duration: Swipe duration in milliseconds
        """
        size = self.driver.get_window_size()
        start_x = int(size['width'] * 0.8)
        start_y = size['height'] // 2
        end_x = int(size['width'] * 0.2)
        
        self.driver.swipe(start_x, start_y, end_x, start_y, duration)
        logger.debug("Swiped left")
    
    def swipe_right(self, duration: int = 800):
        """
        Swipe right.
        
        Args:
            duration: Swipe duration in milliseconds
        """
        size = self.driver.get_window_size()
        start_x = int(size['width'] * 0.2)
        start_y = size['height'] // 2
        end_x = int(size['width'] * 0.8)
        
        self.driver.swipe(start_x, start_y, end_x, start_y, duration)
        logger.debug("Swiped right")
    
    def scroll_to_element(
        self, 
        locator: Tuple[str, str], 
        max_scrolls: int = 10,
        direction: str = 'up'
    ) -> Optional[object]:
        """
        Scroll until element is visible.
        
        Args:
            locator: Element to find
            max_scrolls: Maximum scroll attempts
            direction: 'up' or 'down'
        
        Returns:
            Element if found, None otherwise
        """
        for i in range(max_scrolls):
            if self.is_element_present(locator, timeout=2):
                logger.info(f"Found element after {i} scrolls")
                return self.find_element(locator)
            
            if direction == 'up':
                self.swipe_up()
            else:
                self.swipe_down()
            
            time.sleep(0.5)  # Brief pause between scrolls
        
        logger.warning(f"Element not found after {max_scrolls} scrolls")
        return None
    
    def long_press(self, locator: Tuple[str, str], duration: int = 1000):
        """
        Long press on element.
        
        Args:
            locator: Element to long press
            duration: Press duration in milliseconds
        """
        element = self.find_element(locator)
        self.touch.long_press(element, duration=duration).perform()
        logger.info(f"Long pressed element: {locator}")
    
    def hide_keyboard(self):
        """
        Hide the on-screen keyboard if visible.
        
        Different approaches for iOS vs Android.
        """
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
                logger.debug("Keyboard hidden")
        except Exception as e:
            logger.debug(f"Could not hide keyboard: {e}")
    
    # Waiting Helpers
    def wait_for_element_visible(
        self, 
        locator: Tuple[str, str], 
        timeout: int = 10
    ):
        """
        Wait for element to be visible.
        
        Args:
            locator: Element locator
            timeout: Max wait time
        
        Returns:
            Element when visible
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    
    def wait_for_element_clickable(
        self,
        locator: Tuple[str, str],
        timeout: int = 10
    ):
        """
        Wait for element to be clickable.
        
        Args:
            locator: Element locator
            timeout: Max wait time
        
        Returns:
            Element when clickable
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    
    def wait_for_text(
        self,
        locator: Tuple[str, str],
        expected_text: str,
        timeout: int = 10
    ) -> bool:
        """
        Wait for element to contain specific text.
        
        Args:
            locator: Element locator
            expected_text: Text to wait for
            timeout: Max wait time
        
        Returns:
            True if text found, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element(locator, expected_text)
            )
            return True
        except TimeoutException:
            return False
    
    # Screenshot
    def take_screenshot(self, filename: str):
        """
        Take screenshot and save to file.
        
        Args:
            filename: Path where to save screenshot
        """
        self.driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")
    
    # App Management
    def background_app(self, seconds: int = 5):
        """
        Send app to background for specified time.
        
        Useful for testing app resumption.
        
        Args:
            seconds: Time to keep app in background
        """
        self.driver.background_app(seconds)
        logger.info(f"App backgrounded for {seconds} seconds")
    
    def reset_app(self):
        """Reset app to initial state (clears data)."""
        self.driver.reset()
        logger.info("App reset")
    
    def close_app(self):
        """Close the app."""
        self.driver.close_app()
        logger.info("App closed")
    
    def launch_app(self):
        """Launch the app."""
        self.driver.launch_app()
        logger.info("App launched")
