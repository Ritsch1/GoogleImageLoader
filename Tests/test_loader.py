import unittest
from os import listdir, rmdir
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

    def test_create_image_dirs_no_search_keys(self):
        """
        Testing the create_image_dirs method of the Loader - class
        """
        search_keys = []
        self.assertTrue(set(search_keys).issubset(set(listdir())))

    def test_create_image_dirs_one_search_key_list(self):
        """
        Testing the create_image_dirs method of the Loader - class
        """
        # Arrange
        search_keys = ["Dogs"]
        gil = Google_Image_Loader.Loader(search_keys)
        # Act
        gil.create_image_dirs()
        # Assert
        self.assertTrue(set(search_keys).issubset(set(listdir())))
        # Cleaning
        for s in search_keys:
            rmdir(s)

    def test_create_image_dirs_two_search_keys_tuple(self):
        # Arrange
        search_keys = ("Cats", "Unicorns")
        gil = Google_Image_Loader.Loader(search_keys)
        # Act
        gil.create_image_dirs()
        # Assert
        self.assertTrue(set(search_keys).issubset(set(listdir())))
        # Cleaning
        for s in search_keys:
            rmdir(s)

if __name__ == '__main__':
    unittest.main()