import os, time, threading
from queue import Queue
import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class Loader:
    """
    The central class to perform the loading of the google - images.
    """

    def __init__(self, search_keys:[str], num_images:int=100):
        """Initialize instance of the Google_Image_Loader class

        Args:
            search_keys : List of search keys for which images shall be downloaded.
                          If the list is empty, a ValueError is raised.
            num_images: The maximum number of images to download for every search-key.
                        By default set to 100.
        """
        if type(search_keys) != list and type(search_keys) != tuple:
            raise ValueError(f"provided search_keys - value {search_keys} is not an iterable.")
        elif type(num_images) != int or num_images <= 0:
            raise ValueError(f"provided image-number value {num_images} must be positive.")
        else:
            # Removing empty strings
            search_keys = [s for s in search_keys if len(s) > 0]
            if len(search_keys) == 0:
                raise ValueError("No search_key was provided.")
            #Remove duplicate search_keys
            search_keys = list(set(search_keys))
            self.search_keys = search_keys
            self.num_images = num_images
            # Constants - do not change
            self.GOOGLE_PREFIX = "https://www.google.com/search?q="
            self.GOOGLE_SUFFIX = "&source=lnms&tbm=isch&sa=X&ei=0eZEVbj3IJG5uATalICQAQ&ved=0CAcQ_AUoAQ&biw=939&bih=591"
            # Variable to save the current stage of the google image results for different search_keys
            self.page_sources = []
            self.url = ""

    def create_image_dirs(self):
        """
        Creates the image directories for the search-keys.
        """
        PREFIX = os.path.join(os.path.expanduser("~"), "GoogleImageLoads")
        os.mkdir(path=PREFIX)
        for search_key in self.search_keys:
            os.mkdir(path=os.path.join(PREFIX, search_key))

    def reformat_search_keys(self):
        """
        Reformat the search-keys to match format in the http get-query.
        For example: "dogs big fluffy" -> "dogs+big+fluffy"
        """
        self.search_keys = [s.strip().replace(" ","+") for s in self.search_keys]

    def scroll_through_google_images(self):
        """
        This function executes scrolling through the google image search results. This
        is neccessary as google only loads new images by scrolling down. Additionally,
        the "see more" button needs to be clicked.
        """
        for search_key in self.search_keys:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            # Construct the target url to access
            self.url = self.GOOGLE_PREFIX + search_key + self.GOOGLE_SUFFIX
            # Invoke get request
            driver.get(self.url)

            # Accessing the page and scroll down / click buttons
            try:
                # Scroll down
                driver.execute_script("window.scrollTo(0,30000)")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0,60000)")
                time.sleep(2)

            except:
                print("url not valid")
                driver.quit()

            # Get the pages' current source code
            self.page_sources.append(driver.page_source)
            driver.close()

    def extract_picture_url(self):
        """
        For all
        """