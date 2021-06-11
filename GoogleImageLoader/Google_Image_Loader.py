from os import mkdir
import datetime

class Loader:
    """
    The central class to perform the loading of the google - images.
    """

    def __init__(self, search_keys:[str]):
        """Initialize instance of the Google_Image_Loader class

        Args:
            search_keys : List of search keys for which images shall be downloaded.
                          If the list is empty, a ValueError is raised.
        """
        if type(search_keys) != list and type(search_keys) != tuple:
            raise ValueError(f"provided search_keys - value {search_keys} is not an iterable.")

        else:
            # Removing empty strings
            search_keys = [s for s in search_keys if len(s) > 0]
            if len(search_keys) == 0:
                raise ValueError("No search_key was provided.")
            #Remove duplicate search_keys
            search_keys = list(set(search_keys))
            self.search_keys = search_keys

    def create_image_dirs(self):
        """
        Creates the image directories for the search-keys.
        """
        for search_key in self.search_keys:
            mkdir(path=search_key)

    def reformat_search_keys(self):
        """
        Reformat the search-keys to match format in the http get-query.
        For example: "dogs big fluffy" -> "dogs+big+fluffy"
        """
        #Remove trailing/leading whitespaces and swap whitespace with +
        self.search_keys = [s.strip().replace(" ","+") for s in self.search_keys]