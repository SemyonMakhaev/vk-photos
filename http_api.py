#!/usr/bin/env python3
"""
This program downloads photos from
selected album from vk.com.
"""
import sys

from argparse import ArgumentParser
from os import path, mkdir
from logging import warning, error

from requests import post, get


def main():
    """
    Requests to vk.com sending for albums getting.
    Offering to select an album from a list for user.
    Loading of photos and saving to the folder.
    """
    owner_id = argument_parse()
    albums = get_albums(owner_id)

    if len(albums) == 0:
        print("This owner has no one public album.")
        sys.exit(0)

    album_id, album_name = select_album(albums)
    photos = get_photos(owner_id, album_id)
    folder = save_photos(album_name, photos)

    print("Photos were saved in {}".format(folder))


def argument_parse():
    """Arguments parsing."""
    parser = ArgumentParser(prog="python3 http-api.py", \
        description="Downoading of photos from a selected album from vk.com", \
        epilog="(c) Semyon Makhaev, 2016. All rights reserved.")
    parser.add_argument("owner_id", type=int, \
        help="The ID of owner of photos on vk.com.")
    args = parser.parse_args()
    return args.owner_id


def get_albums(owner_id):
    """Returns a server reply."""
    request = "https://api.vk.com/method/photos.getAlbums?owner_id={}".format(owner_id)
    answer = post(request).json()

    if "error" in answer:
        error("Incorrect owner ID.")
        sys.exit(0)

    return answer["response"]


def select_album(albums):
    """
    Takes a dict with albums names as keys and IDs as values.
    Returns selected album ID and name.
    """
    idx = 1
    numbers = {}

    print("Albums of this user:")
    for album in albums:
        numbers[idx] = album
        print("{}) {}".format(idx, album["title"]))
        idx += 1

    while True:
        try:
            number = int(input("Select an album. Its number: "))
            if number < 1 or number >= idx:
                print("Sorry, try again")
            else:
                return numbers[number]["aid"], numbers[number]["title"]

        except ValueError:
            print("Please, write an album number.")


def get_photos(owner_id, album_id):
    """Photos downloading."""
    request = "https://api.vk.com/method/photos.get?owner_id={}&album_id={}".format(\
                                                                owner_id, album_id)
    photos = post(request).json()["response"]

    # Choising the best quality.
    for photo in photos:
        if "src_xxxbig" in photo.keys():
            yield get_photo(photo["src_xxxbig"])

        elif "src_xxbig" in photo.keys():
            yield get_photo(photo["src_xxbig"])

        elif "src_xbig" in photo.keys():
            yield get_photo(photo["src_xbig"])

        elif "src_big" in photo.keys():
            yield get_photo(photo["src_big"])

        elif "src" in photo.keys():
            yield get_photo(photo["src"])

        elif "src_small" in photo.keys():
            yield get_photo(photo["src_small"])

        else:
            warning("Photo doesnt exist.")


def get_photo(url):
    """Returns a bytes of photo."""
    return get(url).content


def save_photos(name, photos):
    """Create a folder and save photos there."""
    print(name)
    folder_name = folder_choice(name)

    print("Loading...")

    img = "img"
    jpg = ".jpg"
    number = 0
    for photo in photos:
        with open(folder_name + path.sep + img + str(number) + jpg, mode='wb') \
                                                    as photo_file:
            photo_file.write(photo)

        number += 1

    return folder_name



def folder_choice(name):
    """Chosing of the folder name."""
    while True:
        try:
            if path.exists(name):
                print("The folder {} already exists".format(name))
                confirm = input("Are you sure to reuse it? [Y/N]")
                if confirm.lower() == "y":
                    return name

            mkdir(name)
            return name

        except OSError:
            print("Cannot create folder {}".format(name))
            name = input("Please, chose other name or path: ")


if __name__ == '__main__':
    main()
