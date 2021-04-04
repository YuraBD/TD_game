import requests
import cairosvg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def show_image():
    img = mpimg.imread('pokemon.png')
    imgplot = plt.imshow(img)
    plt.show()


def get_pokemon(poke_id: int) -> str:
    r = requests.get(
        f'http://pokeapi.co/api/v2/pokemon/{poke_id}/')
    response = r.json()
    image = response['sprites']['other']['dream_world']['front_default']
    return image


def svg_to_png(url):
    svg = url
    png = 'pokemon.png'
    cairosvg.svg2png(url= svg, write_to= png)


def main():
    svg_to_png(get_pokemon(563))
    show_image()


if __name__ == "__main__":
    main()