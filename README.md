# GoogleImageLoader

This application enables you to automatically download images from google using the selenium chrome driver.
In order to use this application you need to have installed the Google Chrome webbrowser on your machine.

The packages that need to be installed in order to run the application are:

* numpy
* requests
* selenium

## Usage

To use the GoogleImageLoader you have to run:

`python GoogleImageLoader -n <number_of_images> -k <["key1", .., "keyN"]>`

The argument *-n* determines how many images will maximally be downloaded for each search - key.
It will download the maximal available images from the Google image search-page.
The argument *-k* determines the search-keys that are used for an image-search each.
The images to each search key will be saved into a folder in *~/GoogleImageLoads/key1_YYYY-MM-DD*.

## Example

`python GoogleImageLoader -n 100 -k "football" "volleyball"`

Assuming todays date is 2021-09-24, this will save 100 images each in the folders:

* ~/GoogleImageLoads/football_2021-09-24
* ~/GoogleImageLoads/volleyball_2021-09-24
