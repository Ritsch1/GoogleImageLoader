import os
import time
import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request
import datetime
import requests
import numpy as np


class Loader:
    """
    The central class to perform the loading of the google - images.
    """

    def __init__(self, search_keys:[str], num_images: int = 20):
        """Initialize instance of the Google_Image_Loader class

        Args:
            search_keys : List of search keys for which images shall be downloaded.
                          If the list is empty, a ValueError is raised.
            num_images: The maximum number of images to download for every search-key.
                        By default set to 20.
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
            # Remove duplicate search_keys
            search_keys = list(set(search_keys))
            self.search_keys = search_keys
            self.num_images = num_images
            # Constants - do not change
            self.GOOGLE_PREFIX = "https://www.google.com/search?q="
            self.GOOGLE_SUFFIX = "&source=lnms&tbm=isch&sa=X&ei=0eZEVbj3IJG5uATalICQAQ&ved=0CAcQ_AUoAQ&biw=939&bih=591"
            # Variable to save the current stage of the google image results for different search_keys
            self.page_sources = {}
            # Dictionary for storing the urls of images found in the page source-codes
            self.image_urls = {}
            # Directory path where directories of the search-keys and within them the images will be saved
            self.DIRECTORY_PREFIX = os.path.join(os.path.expanduser("~"), "GoogleImageLoads")
            self.TODAY = str(datetime.date.today())

    def create_central_dir(self):
        """
        Create the central folder that contains all sub - folders to search - queries and contains the
        corresponding images.
        """
        if not os.path.isdir(self.DIRECTORY_PREFIX):
            os.mkdir(self.DIRECTORY_PREFIX)

    def create_image_dirs(self):
        """
        Creates the image directories for the search-keys.
        """
        for search_key in self.search_keys:
            # Check if there is already a directory with this search - key
            new_dir = os.path.join(self.DIRECTORY_PREFIX, search_key+ "_" + str(datetime.date.today()))
            # Skip the creation if it already exists
            if not os.path.isdir(new_dir):
                os.mkdir(new_dir)

    def reformat_search_keys(self):
        """
        Reformat the search-keys to match format in the http get-query.
        For example: "dogs big fluffy" -> "dogs+big+fluffy"
        """
        self.search_keys = [s.strip().replace(" ","+") for s in self.search_keys]

    def fetch_image_urls(self) -> list:
        """
        This function executes scrolling through the google image search results. This
        is necessary as google only loads new images by scrolling down. Additionally,
        the "see more" button needs to be clicked.

        returns:
            image_urls: A list of image_url - tuples of the form (search_key, url).
            The first item in each tuple is always the search - key for later inference of
            the download directory.
        """
        page_reload_wait = 0.05

        # Set selenium chrome options
        options = webdriver.ChromeOptions()
        # Suppress terminal output from selenium
        options.add_argument("--log-level=3")
        # Run selenium without UI
        options.add_argument("headless")

        image_urls = []
        for search_key in self.search_keys:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            # Construct the target url to access
            url = self.GOOGLE_PREFIX + search_key + self.GOOGLE_SUFFIX
            # Invoke get request
            driver.get(url)

            # Accessing the page and scroll down / see - more click buttons
            old_height = driver.execute_script('return document.body.scrollHeight')
            # Click accept-cookies button if there is one
            cookie_btn = driver.find_element_by_class_name("qXTnff")
            cookie_btn.click()
            while True:
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(page_reload_wait)
                new_height = driver.execute_script('return document.body.scrollHeight')

                # If the end of the page is reached
                if new_height == old_height:
                    # try to find the "see more" button if there is one
                    try:
                        driver.find_element_by_class_name('mye4qd').click()
                        time.sleep(page_reload_wait)
                    # If there is no "see more" button, the end of the page is reached
                    except Exception as e:
                        break
                else:
                    old_height = new_height

            # for google image result website logic
            is_first_image = True
            # Get all image results (class with multiple words separated by whitespaces are actually several
            # classes, use css_selector instead and prefix every class with a dot, like below
            images = driver.find_elements_by_css_selector('.isv-r.PNCib.MSM1fd.BUooTd')
            """ 
            Go back to the top of the page, such that the little icon bar is not
            hiding the images and the images are thus clickable
            """
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)

            # Click and infer the original image - url (with the original size) from each image result
            for image in images[:self.num_images]:
                image.click()
                if is_first_image:
                    image_urls.append((search_key, driver.find_elements_by_class_name('n3VNCb')[0].get_attribute("src")))
                    is_first_image = False
                else:
                    image_urls.append((search_key, driver.find_elements_by_class_name('n3VNCb')[1].get_attribute("src")))

            driver.close()

        return image_urls

    def download_images(self, image_urls: list):
        """
        Downloads all images referenced with their urls from image_urls and persists the
        images to disc into the corresponding directory.

        params:
            image_urls: A list of image_url - tuples of the form (search_key, url).
            The first item in each tuple is always the search - key for later inference of
            the download directory.
        """

        # Instantiate as many processes as there are cpu - cores available
        pool = mp.Pool(mp.cpu_count())
        pool.map(self.worker, image_urls)

    def worker(self, image_url: tuple):
        """
        Initiates a worker process to download images from the web and saving them to disk.
        This way network - delays can be mitigated and the code can be sped up.

        params:
            image_url: A tuple of the form (search_key, url).
            The first item in each tuple is always the search - key for later inference of
            the download directory.
        """

        search_key, url = image_url
        # Set download directory
        download_dir = os.path.join(self.DIRECTORY_PREFIX, search_key + "_" + self.TODAY)

        # If url is actually an image-uri and not a image e.g. jpeg, the image must be saved as png
        if url[:4] == "data":
            img_data = urllib.request.urlopen(url)
            random_id = str(np.random.choice(self.num_images ** 2))
            with open(os.path.join(download_dir, search_key + "_" + random_id + ".jpg"), 'wb') as f:
                f.write(img_data.file.read())

        # Normal image data e.g. jpeg or png, this type of data will be saved as jpeg by default
        else:
            img_data = requests.get(url).content
            random_id = str(np.random.choice(self.num_images ** 2))
            with open(os.path.join(download_dir, search_key + "_" + random_id + ".jpg"), 'wb') as handler:
                handler.write(img_data)
