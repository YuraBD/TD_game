"""Example of using PokeAPI and python arcade"""
import arcade
import requests
import urllib.request
import time
import os


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "TD game"
CHARACTER_SCALING = 2
RIGHT_FACING = 1
LEFT_FACING = 0


def load_texture_pair(filename):
    """Load a texture pair, with the second being a mirror image."""
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class MyGame(arcade.Window):
    """Main application class."""
    def __init__(self):
        """Initialize class MyGame with poke and poke_list"""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
        self.poke_list = None
        self.poke = None
        arcade.set_background_color([201, 255, 229])

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.poke_list = arcade.SpriteList()
        self.poke = Pokemon()
        self.poke.last_update = time.perf_counter()
        self.poke.center_x = SCREEN_WIDTH // 2 - 400
        self.poke.center_y = SCREEN_HEIGHT // 2
        self.poke_list.append(self.poke)

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        self.poke_list.draw()

    def on_update(self, delta_time):
        """Movement and game logic"""
        self.poke_list.update()
        self.poke.change_x = 0
        self.poke_list.update_animation(delta_time)
        if time.perf_counter() - self.poke.last_update >= 0.5:
            self.poke.last_update = time.perf_counter()
            self.poke.change_x = 15
            self.poke_list.update()
            self.poke_list.update_animation(delta_time)
 

class Pokemon(arcade.Sprite):
    """Represent a pokemon"""
    def __init__(self):
        """Initialize pokemon with arcade.Sprite attributes"""
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        main_path = "sprites/front_default.png"
        self.walk_textures = []
        for image_name in ('front_default', 'back_default'):
            texture = load_texture_pair(f"sprites/{image_name}.png")
            self.walk_textures.append(texture)

    def update_animation(self, delta_time: float = 0.1):
        """Update poke sprite"""
        if self.change_x > 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
            self.change_x = 21
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        if self.change_x == 0 and self.change_y == 0:
            frame = self.cur_texture
            direction = self.character_face_direction
            self.texture = self.walk_textures[frame][direction]
            return

        self.cur_texture += 1
        if self.cur_texture > 1:
            self.cur_texture = 0



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
    time.time()
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
