"""
This module contains following functions: show_image,
get_pokemon, svg_to_png and main.
The purpose of this module is to show the ability
of PokeApi. In this case it is used to show the 
image of pokemon with id=563
"""
import requests
import cairosvg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def show_image() -> None:
    """
    This function  gets the image by its path and shows it
    in a new window.
    """
    img = mpimg.imread('pokemon.png')
    imgplot = plt.imshow(img)
    plt.show()


def get_pokemon(poke_id: int) -> str:
    """
    This function makes GET-request using the url of specific pokemon
    by its id. Returns the image URL.
    """
    r = requests.get(
        f'http://pokeapi.co/api/v2/pokemon/{poke_id}/')
    response = r.json()
    image = response['sprites']['other']['dream_world']['front_default']
    return image


def svg_to_png(url) -> None:
    """
    This function converts image in .svg format to the .png format 
    and saves it in 'pokemon.png' file.
    """
    svg = url
    png = 'pokemon.png'
    cairosvg.svg2png(url= svg, write_to= png)


def main() -> None:
    """
    The main function. Runs the program.
    """
    svg_to_png(get_pokemon(563))
    show_image()


if __name__ == "__main__":
    main()