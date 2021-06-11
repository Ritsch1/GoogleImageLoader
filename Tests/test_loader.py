import unittest
import os
from shutil import rmtree
from GoogleImageLoader import Google_Image_Loader

# Directory path where directories of the search-keys and within them the images will be saved
PREFIX = os.path.join(os.path.expanduser("~"), "GoogleImageLoads")

class LoaderTest(unittest.TestCase):

    def test_init_list_two_keys(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ["Hello Mars", "Nice to meet you too"]
        gil = Google_Image_Loader.Loader(search_keys)
        self.assertIsInstance(gil, Google_Image_Loader.Loader)

    def test_init_tuple_one_key(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ("Hello World", "Nice to meet you")
        gil = Google_Image_Loader.Loader(search_keys)
        self.assertIsInstance(gil, Google_Image_Loader.Loader)

    def test_init_tuple_one_key_zero_images(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ("Hello World", "Nice to meet you")
        num_images = 0
        self.assertRaises(ValueError, Google_Image_Loader.Loader, search_keys, num_images)

    def test_init_tuple_one_key_negative_images(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ("Hello World", "Nice to meet you")
        num_images = -1
        self.assertRaises(ValueError, Google_Image_Loader.Loader, search_keys, num_images)


    def test_init_tuple_no_key(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ()
        self.assertRaises(ValueError, Google_Image_Loader.Loader, search_keys)

    def test_init_list_no_key(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = []
        self.assertRaises(ValueError, Google_Image_Loader.Loader, search_keys)

    def test_init_tuple_empty_key(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ("")
        self.assertRaises(ValueError, Google_Image_Loader.Loader, search_keys)

    def test_init_tuple_empty_key(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = [""]
        self.assertRaises(ValueError, Google_Image_Loader.Loader, search_keys)

    def test_create_image_dirs_one_search_key_list(self):
        """
        Testing the create_image_dirs method of the Loader - class
        """
        # Arrange
        global PREFIX
        search_keys = ["Dogs"]
        gil = Google_Image_Loader.Loader(search_keys)
        # Act
        gil.create_image_dirs()
        # Assert
        self.assertTrue(set(search_keys).issubset(set(os.listdir(PREFIX))))
        # Cleaning
        rmtree(PREFIX)

    def test_create_image_dirs_two_search_keys_tuple(self):
        """
        Testing the create_image_dirs method of the Loader - class
        """
        # Arrange
        global PREFIX
        search_keys = ("Cats", "Unicorns")
        gil = Google_Image_Loader.Loader(search_keys)
        # Act
        gil.create_image_dirs()
        # Assert
        self.assertTrue(set(search_keys).issubset(set(os.listdir(PREFIX))))
        # Cleaning
        rmtree(PREFIX)

    def test_reformat_search_keys_one_key_whitespaces(self):
        """
        Testing the reformat_search_keys method of the Loader - class
        """
        # Arrange
        search_key = tuple([" fluffy Dogs "])
        # Act
        gil = Google_Image_Loader.Loader(search_key)
        formatted_search_keys = gil.reformat_search_keys()
        # Assert
        self.assertEqual(gil.search_keys, ["fluffy+Dogs"])

    def test_page_scroll(self):
        """
        Testing the scroll_through_google_images method of the Loader - class
        """
        # Arrange
        search_keys = ["fluffy Gods", "fluffy Hawks"]
        # Act
        gil = Google_Image_Loader.Loader(search_keys)
        gil.reformat_search_keys()
        gil.scroll_through_google_images()
        # Number of page source codes should be equal to the number of search-keys
        # Assert
        self.assertEqual(len(gil.page_sources), len(search_keys))

    def test_extract_picture_urls(self):
        """
        Testing the extract_picture_url method of the Loader - class
        """
        # Arrange
        search_keys = ["fluffy Gods", "fluffy Hawks"]
        # Act
        gil = Google_Image_Loader.Loader(search_keys)
        gil.reformat_search_keys()
        gil.scroll_through_google_images()
        gil.extract_picture_urls()

        # Count number of image urls in both image - url queues.
        # It should equal twice the maximal number of images to retrieve if this number is not too high.
        num_image_urls = 0
        for s in gil.search_keys:
            while not gil.image_urls[s].empty():
                gil.image_urls[s].get()
                num_image_urls += 1
        # Assert
        self.assertEqual(len(search_keys) * gil.num_images, num_image_urls,)

    def test_image_download(self):
        """
        Testing the download_images method of the Loader - class.
        """
        # Arrange
        global PREFIX
        search_keys = ["fluffy Gods", "fluffy Hawks"]
        # Act
        gil = Google_Image_Loader.Loader(search_keys)
        gil.reformat_search_keys()
        gil.create_image_dirs()
        gil.scroll_through_google_images()
        url_queue = gil.extract_picture_urls()
        gil.download_images(url_queue=url_queue)

        #Assert that pictures have been saved
        self.assertTrue(len(os.listdir(os.path.join(PREFIX,gil.search_keys[0]))) > 0 and
                        len(os.listdir(os.path.join(PREFIX,gil.search_keys[1]))) > 0)
        # Cleaning
        #rmtree(PREFIX)

if __name__ == '__main__':
    unittest.main()