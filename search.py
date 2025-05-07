from playwright.sync_api import sync_playwright
import threading
import os
import subprocess
import sys

class WebSearcher:
    def __init__(self):
        # Check if browsers are installed when initializing
        self.browsers_installed = self._check_browsers_installed()
        
    def search(self, query, callback=None):
        """
        Perform a web search using Playwright and return the results.
        
        Args:
            query (str): The search query
            callback (function): Optional callback function to receive results
            
        Returns:
            dict: Search results
        """
        # Create a thread to run the search asynchronously
        thread = threading.Thread(target=self._search_thread, args=(query, callback))
        thread.daemon = True
        thread.start()
        return thread
    
    def _search_thread(self, query, callback):
        """
        Thread function to perform the actual search
        """
        try:
            results = self._perform_search(query)
            if callback:
                callback(results)
            return results
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            if callback:
                callback({"error": error_msg})
            return {"error": error_msg}
    
    def _check_browsers_installed(self):
        """
        Check if Playwright browsers are installed
        
        Returns:
            bool: True if browsers are installed, False otherwise
        """
        try:
            # Try to launch a browser with a very short timeout
            with sync_playwright() as p:
                browser = p.chromium.launch()
                browser.close()
            return True
        except Exception:
            return False
    
    def _install_browsers(self):
        """
        Attempt to install Playwright browsers
        
        Returns:
            bool: True if installation was successful, False otherwise
        """
        try:
            # Use subprocess to run the installation command
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install browsers: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during browser installation: {e}")
            return False
            
    def _perform_search(self, query):
        """
        Perform the actual web search using Playwright
        """
        # Check if browsers are installed
        if not self.browsers_installed:
            # Try to install browsers
            installation_success = self._install_browsers()
            if installation_success:
                self.browsers_installed = True
            else:
                installation_command = f"{sys.executable} -m playwright install chromium"
                error_message = (
                    f"Playwright browsers are not installed. Please run the following command:\n\n"
                    f"    {installation_command}\n\n"
                    f"Then restart the application."
                )
                return {"error": error_message}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Search using Baidu
                page.goto('https://www.baidu.com')
                search_box = page.locator('#kw')
                search_box.fill(query)
                search_box.press('Enter')
                page.wait_for_timeout(2000)  # Wait for results to load
                
                # Extract search results
                results = page.locator('.c-container').all()
                search_info = ''
                for result in results[:5]:  # Get first 5 results
                    if result.locator('.content-right_8Zs40').count() > 0:
                        content = result.locator('.content-right_8Zs40').text_content()
                        search_info += content.strip() + '\n\n'
                    elif result.locator('.content-right').count() > 0:
                        content = result.locator('.content-right').text_content()
                        search_info += content.strip() + '\n\n'
                    else:
                        content = result.text_content()
                        search_info += content.strip() + '\n\n'
                
                # Format the results
                search_data = {
                    'query': query,
                    'results': search_info
                }
                
                browser.close()
                return search_data
        except Exception as e:
            # Check if the error is related to browser installation
            error_str = str(e)
            if "Executable doesn't exist" in error_str or "Looks like Playwright was just installed" in error_str:
                installation_command = f"{sys.executable} -m playwright install chromium"
                error_message = (
                    f"Search error: {error_str}\n\n"
                    f"Please run the following command to install Playwright browsers:\n\n"
                    f"    {installation_command}\n\n"
                    f"Then restart the application."
                )
                return {"error": error_message}
            else:
                return {"error": f"Search error: {error_str}"}
    