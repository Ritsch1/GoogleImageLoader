import GoogleImageLoader.Google_Image_Loader
import os
import argparse

parser = argparse.ArgumentParser(description="Downloading images from google image search.")
parser.add_argument("--keys" ,"-k", nargs="+", help="Search - keys to download images for.")
parser.add_argument("--num_images", "-n", default="20", type=int, help="Maximum number of images to be downloaded for each search - key.")
args = parser.parse_args()

PREFIX = os.path.join(os.path.expanduser("~"), "GoogleImageLoads")
gil = GoogleImageLoader.Loader(args.keys, args.num_images)
gil.reformat_search_keys()
# If directory already exists, skip creating it
if os.path.isdir(PREFIX):
    gil.create_image_dirs()
gil.scroll_through_google_images()
url_queue = gil.extract_picture_urls()
gil.download_images(url_queue=url_queue)
print(f"Successfully downloaded images for the search - keys:\n{','.join(x for x in args.keys)}")