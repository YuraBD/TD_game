import requests
import random
import urllib
import os
import shutil


def get_images(id, path):
    """Get poke sprites from PokeAPI"""
    r = requests.get(f'http://pokeapi.co/api/v2/pokemon/{id}/')
    response = r.json()
    for image_name in ('front_default', 'back_default'):
        save_image(response, ['sprites', image_name], f'{path}/{image_name}.png')


def save_image(response:dict, keys:list, path:str):
    """Save images from url"""
    address = response[keys[0]][keys[1]]
    with urllib.request.urlopen(address) as url:
        output = open(path, "wb")
        output.write(url.read())
        output.close()


def choose_random_pokes(num):
    ids = random.sample(range(1, 500), num)
    try:
        os.mkdir("sprites")
    except FileExistsError:
        shutil.rmtree("sprites")
        os.mkdir("sprites")
    for i in range(num):
        os.mkdir(f"sprites/{i}")
        get_images(ids[i], f"sprites/{i}")
