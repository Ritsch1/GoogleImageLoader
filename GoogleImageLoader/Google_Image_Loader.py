import os
import time
import threading
import multiprocessing as mp
from queue import Queue
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request
import datetime
import requests
from bs4 import BeautifulSoup

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

    def reformat_search_keys(self):
        """
        Reformat the search-keys to match format in the http get-query.
        For example: "dogs big fluffy" -> "dogs+big+fluffy"
        """
        self.search_keys = [s.strip().replace(" ","+") for s in self.search_keys]

    def download_google_images(self):
        """
        This function executes scrolling through the google image search results. This
        is necessary as google only loads new images by scrolling down. Additionally,
        the "see more" button needs to be clicked.
        """
        page_reload_wait = 1
        options = webdriver.ChromeOptions()
        #Surpress terminal output from selenium
        options.add_argument("--log-level=3")
        # List for storing all image_urls
        image_urls = []
        for search_key in self.search_keys:
            driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
            # Construct the target url to access
            url = self.GOOGLE_PREFIX + search_key + self.GOOGLE_SUFFIX
            # Invoke get request
            driver.get(url)

            # Accessing the page and scroll down / see - more click buttons
            old_height = driver.execute_script('return document.body.scrollHeight')
            while True:
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(page_reload_wait)
                new_height = driver.execute_script('return document.body.scrollHeight')

                #if the end of the page is reached
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
            # Click and infer the original image - url (with the original size) from each image result
            for image in images[:self.num_images]:
                image.click()
                time.sleep(1)
                if is_first_image:
                    image_urls.append(driver.find_elements_by_class_name('n3VNCb')[0].get_attribute("src"))
                    is_first_image = False
                else:
                    image_urls.append(driver.find_elements_by_class_name('n3VNCb')[1].get_attribute("src"))

            # Set download directory
            download_dir = os.path.join(self.DIRECTORY_PREFIX, search_key+ "_" + str(datetime.date.today()))
            # Load all valid image - data and save it in the download directory
            for index, url in enumerate(image_urls):
                # If url is actually an image-uri and not a image e.g. jpeg, process it differently
                # This type of data will be saved as png
                if url[:4] == "data":
                    img_data = urllib.request.urlopen(url)
                    with open(os.path.join(download_dir,search_key + "_" + str(index) + ".jpg"), 'wb') as f:
                        f.write(img_data.file.read())

                # Normal image data e.g. jpeg or png
                # This type of data will be saved as jpeg by default
                else:
                    img_data = requests.get(url).content
                    with open(os.path.join(download_dir,search_key + "_" + str(index) + ".jpg"), 'wb') as handler:
                        handler.write(img_data)

            driver.close()

    def extract_picture_urls(self) -> Queue:
        """
        Extract the url of every image for each page source-codes.

        returns:
            A queue that contains all image urls and the corresponding search_key in the
            form (search_key, image_url)
        """
        # Queue for storing all picture urls
        q = Queue()
        for search_key in self.search_keys:
            # queue to insert the image urls for a specific search - key into

            # Get the page source-code for a specific search - key and parse it
            html_doc = BeautifulSoup(self.page_sources[search_key], "html.parser")
            # Only extract maximally num_images many picture - urls
            # rg_i Q4LuWd is the class identifier of the img tags of interest
            try:
                imgs = html_doc.find_all(class_="rg_i Q4LuWd", limit=self.num_images)
                for tag in imgs:
                    q.put( (search_key, tag["src"]) )

            except:
                print(f"Error while parsing the page source-code of search-key {search_key}.")

        return q

    def download_images(self, url_queue:Queue):
        """
        Download all images given their urls and load them into the corresponding directory.

        params:
            url_queue: Queue that contains all image urls in the form (search_key, image_url).
        """
        threads = []
        # Create as many threads as there are cpu-cores
        try:
            for i in range(mp.cpu_count()):
                # Initialize processes that will work in parallel on the urls in the url_queue
                threads.append(threading.Thread(target=self.worker, args=(url_queue,), daemon=True))
                # Start process
                threads[i].start()

        except:
            print("Downloading the images failed. Please check network connection.")

        # This thread/function will only continue when all items in the queue were processed by the threads
        url_queue.join()

    def worker(self, url_queue:Queue):
        """
        Initiates a worker thread to download images from the web and saving them to disk.
        This way network - delays and I/O - blocks can be mitigated and the code can be sped up.

        params:
            url_queue: Queue that contains all image urls in the form (search_key, image_url).
        """
        global DIRECTORY_PREFIX
        while True:
            key, url = url_queue.get()
            response = urllib.request.urlopen(url)
            url_queue.task_done()
            # add hash of last 5 url characters for unique filename property
            try:
                with open(os.path.join(self.DIRECTORY_PREFIX, key, str(hash(url[-5:]))+".jpeg"), 'w') as f:
                    f.write(response.file.read())
            except:
                print(f"Saving images for search-key {key} failed.")
