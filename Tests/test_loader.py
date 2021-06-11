import unittest
import os
from shutil import rmtree
from GoogleImageLoader import Google_Image_Loader

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
        search_keys = ["Dogs"]
        PREFIX = os.path.join(os.path.expanduser("~"), "GoogleImageLoads")
        gil = Google_Image_Loader.Loader(search_keys)
        # Act
        gil.create_image_dirs()
        # Assert
        self.assertTrue(set(search_keys).issubset(set(os.listdir(PREFIX))))
        # Cleaning
        rmtree(PREFIX)

    def test_create_image_dirs_two_search_keys_tuple(self):
        # Arrange
        PREFIX = os.path.join(os.path.expanduser("~"), "GoogleImageLoads")
        search_keys = ("Cats", "Unicorns")
        gil = Google_Image_Loader.Loader(search_keys)
        # Act
        gil.create_image_dirs()
        # Assert
        self.assertTrue(set(search_keys).issubset(set(os.listdir(PREFIX))))
        # Cleaning
        rmtree(PREFIX)

    def test_reformat_search_keys_two_keys_trailing_leading_whitespace(self):
        # Arrange
        search_keys = tuple([" fluffy Dogs","white Cats "])
        # Act
        gil = Google_Image_Loader.Loader(search_keys)
        gil.reformat_search_keys()
        # Assert
        self.assertEqual(gil.search_keys, ["fluffy+Dogs","white+Cats"])

    def test_reformat_search_keys_one_key_whitespaces(self):
        # Arrange
        search_key = tuple([" fluffy Dogs "])
        # Act
        gil = Google_Image_Loader.Loader(search_key)
        formatted_search_keys = gil.reformat_search_keys()
        # Assert
        self.assertEqual(gil.search_keys, ["fluffy+Dogs"])

if __name__ == '__main__':
    unittest.main()