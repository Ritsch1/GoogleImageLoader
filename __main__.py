import GoogleImageLoader.Google_Image_Loader
import os
import argparse
import timeit


def main():
    parser = argparse.ArgumentParser(description="Downloading images from google image search.")
    parser.add_argument("--keys" ,"-k", nargs="+", help="Search - keys to download images for.")
    parser.add_argument("--num_images", "-n", default="20", type=int, help="Maximum number of images to be downloaded for each search - key.")
    args = parser.parse_args()

    PREFIX = os.path.join(os.path.expanduser("~"), "GoogleImageLoads")
    start = timeit.default_timer()
    gil = GoogleImageLoader.Loader(args.keys, args.num_images)
    gil.reformat_search_keys()
    # If central directory already exists, skip creating it
    if not os.path.isdir(PREFIX):
        gil.create_central_dir()
    # create search - key specific image folders
    gil.create_image_dirs()
    image_urls = gil.fetch_image_urls()
    gil.download_images(image_urls)

    print(f"Successfully downloaded images for the search - keys:\n{','.join(x for x in args.keys)}\nin "
          f"{timeit.default_timer()-start:.2f} s")


if __name__ == '__main__':
    main()