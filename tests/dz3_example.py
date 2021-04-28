import arcade
import time
import os
from pokelinkedque import PokeQueue
import requests
import urllib

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 960
SCREEN_TITLE = "TD game"
POKEMON_SCALING = 2
RIGHT_FACING = 1
LEFT_FACING = 0

LINES = []
for _ in range(5):
    LINES.append((PokeQueue(), PokeQueue()))


def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class Pokemon(arcade.Sprite):
    def __init__(self, sprites_path, friendly, name):
        super().__init__()
        self.name = name
        if friendly:
            self.character_face_direction = RIGHT_FACING
            self.move_direction = 1
        else:
            self.character_face_direction = LEFT_FACING
            self.move_direction = -1
        self.cur_texture = 0
        self.scale = POKEMON_SCALING

        self.walk_textures = []
        for image_name in ("front_default", "back_default"):
            texture = load_texture_pair(f"{sprites_path}/{image_name}.png")
            self.walk_textures.append(texture)
            print(texture[0].height, texture[0].width)

        frame = self.cur_texture
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

    def update_animation(self, delta_time: float = 1/60):
        if self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        self.cur_texture += 1
        if self.cur_texture > 1:
            self.cur_texture = 0
        frame = self.cur_texture
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

    def update(self, delta_time):
        self.change_x = 15
        self.update_animation()
        self.center_x += self.change_x * self.move_direction


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
        arcade.set_background_color([201, 255, 229])

    def setup(self):
        for i in range(5):
            poke = Pokemon("sprites", True, "left")
            poke.center_x = SCREEN_WIDTH // 2 - 400
            poke.center_y = 96 + 192*i
            arcade.schedule(poke.update, 0.5)
            LINES[i][0].add_poke(poke)

            poke = Pokemon("sprites", False, "right")
            poke.center_x = SCREEN_WIDTH // 2 + 400
            poke.center_y = 96 + 192*i
            arcade.schedule(poke.update, 0.5)
            LINES[i][1].add_poke(poke)

    def on_draw(self):
        arcade.start_render()
        for i in range(1, 5):
            arcade.draw_line(0 , 192*i, SCREEN_WIDTH, 192*i, arcade.color.BLACK, 1)
        for line in LINES:
            line[0].draw()
            line[1].draw()


def get_images():
    """Get poke sprites from PokeAPI"""
    r = requests.get(f'http://pokeapi.co/api/v2/pokemon/25/')
    response = r.json()
    for image_name in ('front_default', 'back_default'):
        save_image(response, ['sprites', image_name], f'sprites/{image_name}.png')


def save_image(response:dict, keys:list, path:str):
    """Save images from url"""
    address = response[keys[0]][keys[1]]
    with urllib.request.urlopen(address) as url:
        output = open(path, "wb")
        output.write(url.read())
        output.close()


def main():
    """Main method"""
    try:
        os.mkdir("sprites")
    except FileExistsError:
        pass
    get_images()
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()