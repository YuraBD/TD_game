import requests
import random
import urllib
import os
import shutil
from PIL import Image


def get_images_and_stats(id, path, stats):
    """Get poke sprites from PokeAPI"""
    r = requests.get(f'http://pokeapi.co/api/v2/pokemon/{id}/')
    response = r.json()
    stats.append(get_stats(id, path, response))
    for image_name in ('front_default', 'back_default'):
        save_image(response, ['sprites', image_name], f'{path}/{image_name}.png')
        add_fight_anim(path)


def get_stats(id, path, response):
    name = response["name"]
    hp = response["weight"]
    attack = response["stats"][0]["base_stat"]
    return [name, hp, attack]

def add_fight_anim(path):
    current_pokemon_state = Image.open(f'{path}/front_default.png')
    chopping_pokemon = current_pokemon_state.rotate(315)
    punching_pokemon = current_pokemon_state.rotate(45)
    chopping_pokemon.save(f'{path}/chopping.png')
    punching_pokemon.save(f'{path}/punching.png')


def save_image(response:dict, keys:list, path:str):
    """Save images from url"""
    address = response[keys[0]][keys[1]]
    with urllib.request.urlopen(address) as url:
        output = open(path, "wb")
        output.write(url.read())
        output.close()


def choose_random_pokes(num, path):
    ids = random.sample(range(1, 500), num)
    try:
        os.mkdir(path)
    except FileExistsError:
        shutil.rmtree(path)
        os.mkdir(path)
    stats = []
    for i in range(num):
        os.mkdir(f"{path}/{i}")
        get_images_and_stats(ids[i], f"{path}/{i}", stats)
    max_hp = max(stats, key = lambda x: x[1])[1]
    max_attack = max(stats, key = lambda x: x[2])[2]
    for i in range(num):
        with open(f"{path}/{i}/stats.txt", 'w') as stats_file:
            name = stats[i][0]
            hp = 200 + round((stats[i][1]/max_hp)*300)
            attack = stats[i][2]
            price = round(1000*(hp/500 + attack/max_attack)/2)
            stats_file.write(f"name {name}\nhp {hp}\nattack {attack}\nprice {price}")


choose_random_pokes(5, "friendly_sprites")