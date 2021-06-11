class GoogleImageLoader():

    def __init__(self, search_keys: list):
        """Initialize instance of the Google_Image_Loader class

        Args:
            search_keys : List of search keys for which images shall be downloaded.
                          If the list is empty, a ValueError is raised.
        """
        if type(search_keys) != list:
            raise ValueError(f"provided search_key {search_keys} is not a list.")
        elif len(search_keys) == 0:
            raise ValueError("No search_key was provided.")
        else:
            #Remove duplicate search_keys
            search_keys = list(set(search_keys))
            self.search_keys = search_keys
