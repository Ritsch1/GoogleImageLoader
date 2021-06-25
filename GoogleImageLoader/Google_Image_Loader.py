import os
import time
import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request
import datetime
import requests
import threading

class Loader:
    """
    The central class to perform the loading of the google - images.
    """

    def __init__(self, search_keys:[str], num_images:int=20):
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
            #Remove duplicate search_keys
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

    def create_central_dir(self):
        """
        Create the central folder that contains all subfolders to search - queries and contains the
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

    def download_images(self, image_urls: list):
        """
        Download all images given their urls and load them into the corresponding directory.

        params:
            image_urls: A list of queues containing the image_urls for the different search - keys.
            The first item in the queue is always the search - key for later inference of
            the download directory.
        """
        # Initialize as many threads as there are search_keys
        threads = []
        try:
            for i in range(len(self.search_keys)):
                threads.append(threading.Thread(target=self.worker, args=(image_urls[i],), daemon=True))
                threads[i].start()
        except:
            raise ConnectionError("Failed to download the images. Please check your network connection.")

        # Terminate threads
        for t in threads:
            t.join()

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
            image_urls: A list of lists where every sublist contains the image_urls for the
            different search - keys.
            The first item in a sublist is always the search - key for later inference of
            the download directory.
        """
        page_reload_wait = 0.5
        options = webdriver.ChromeOptions()
        # Suppress terminal output from selenium
        options.add_argument("--log-level=3")
        options.add_argument("headless")
        # List of queues storing image_urls
        image_urls = [[]] * len(self.search_keys)
        for i, search_key in enumerate(self.search_keys):
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
                    except:
                        break
                else:
                    old_height = new_height

            # for google image result website logic
            is_first_image = True
            # Get all image results (class with multiple words separated by whitespaces are actually several
            # classes, use css_selector instead and prefix every class with a dot, like below
            images = driver.find_elements_by_css_selector('.isv-r.PNCib.MSM1fd.BUooTd')
            # The first element in the queue is the search - key, for later building the download_dir
            image_urls[i].append(search_key)
            # Go back to the top of the page, such that the little icon bar is not
            # hiding the images and the images are thus clickable
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)

            # Click and infer the original image - url (with the original size) from each image result
            for image in images[:self.num_images]:
                image.click()
                if is_first_image:
                    image_urls[i].append(driver.find_elements_by_class_name('n3VNCb')[0].get_attribute("src"))
                    is_first_image = False
                else:
                    image_urls[i].append(driver.find_elements_by_class_name('n3VNCb')[1].get_attribute("src"))

            driver.close()

        return image_urls

    def worker(self, url_list: list):
        """
        Initiates a worker thread to download images from the web and saving them to disk.
        This way network - delays and I/O - blocks can be mitigated and the code can be sped up.

        params:
            url_list: List that contains all image urls for one search - key, while the first
            item in the list is the search - key for inference of the download directory.
        """
        # Set download directory
        search_key = url_list[0]
        download_dir = os.path.join(self.DIRECTORY_PREFIX, search_key + "_" + str(datetime.date.today()))
        counter = 1
        while counter < len(url_list):
            url = url_list[counter]
            # If url is actually an image-uri and not a image e.g. jpeg, process it differently
            # This type of data will be saved as png
            if url[:4] == "data":
                img_data = urllib.request.urlopen(url)
                with open(os.path.join(download_dir, search_key + "_" + str(counter) + ".jpg"), 'wb') as f:
                    f.write(img_data.file.read())

            # Normal image data e.g. jpeg or png
            # This type of data will be saved as jpeg by default
            else:
                img_data = requests.get(url).content
                with open(os.path.join(download_dir, search_key + "_" + str(counter) + ".jpg"), 'wb') as handler:
                    handler.write(img_data)

            counter += 1