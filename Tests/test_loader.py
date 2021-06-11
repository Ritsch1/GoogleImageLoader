import unittest
import os
from GoogleImageLoader import Google_Image_Loader

class GoogleImageLoaderTest(unittest.TestCase):

    def test_init_list_two_keys(self):
        """
        Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ["Hello World", "Nice to meet you"]
        gil = Google_Image_Loader.Loader(search_keys)
        self.assertIsInstance(gil, Google_Image_Loader.Loader)

    def test_init_tuple_one_key(self):
        """
         Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ("Hello World", "Nice to meet you")
        gil = Google_Image_Loader.Loader(search_keys)
        self.assertIsInstance(gil, Google_Image_Loader.Loader)

    def test_init_tuple_no_key(self):
        """
            Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ()
        self.assertRaises(ValueError, Google_Image_Loader.Loader(search_keys))

    def test_init_list_no_key(self):
        """
            Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = []
        self.assertRaises(ValueError, Google_Image_Loader.Loader(search_keys))

    def test_init_tuple_empty_key(self):
        """
            Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = ("")
        self.assertRaises(ValueError, Google_Image_Loader.Loader(search_keys))

    def test_init_tuple_empty_key(self):
        """
            Testing the __init__ method of the Google_Image_Loader - class
        """
        search_keys = [""]
        self.assertRaises(ValueError, Google_Image_Loader.Loader(search_keys))

if __name__ == '__main__':
    unittest.main()