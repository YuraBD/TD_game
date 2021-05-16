import arcade
import time
import os

from pyglet.window.key import Y
from pokelinkedque import PokeQueue
from poke_chs import choose_random_pokes

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 960
SCREEN_TITLE = "TD game"
POKEMON_SCALING = 2
RIGHT_FACING = 1
LEFT_FACING = 0

FRIENDLY_POKE_QUEUE_0 = PokeQueue()
FRIENDLY_POKE_QUEUE_1 = PokeQueue()
FRIENDLY_POKE_QUEUE_2 = PokeQueue()
FRIENDLY_POKE_QUEUE_3 = PokeQueue()
FRIENDLY_POKE_QUEUE_4 = PokeQueue()
ENEMY_POKE_QUEUE_0 = PokeQueue()
ENEMY_POKE_QUEUE_1 = PokeQueue()
ENEMY_POKE_QUEUE_2 = PokeQueue()
ENEMY_POKE_QUEUE_3 = PokeQueue()
ENEMY_POKE_QUEUE_4 = PokeQueue()
LINES = []
LINES.append((FRIENDLY_POKE_QUEUE_0, ENEMY_POKE_QUEUE_0))
LINES.append((FRIENDLY_POKE_QUEUE_1, ENEMY_POKE_QUEUE_1))
LINES.append((FRIENDLY_POKE_QUEUE_2, ENEMY_POKE_QUEUE_2))
LINES.append((FRIENDLY_POKE_QUEUE_3, ENEMY_POKE_QUEUE_3))
LINES.append((FRIENDLY_POKE_QUEUE_4, ENEMY_POKE_QUEUE_4))

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class Cursor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.poke = True
        self.spawn_poke = None



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
        # else:
        #     self.change_x += 23
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
        self.cursor = Cursor(96, 96)
        self.available_pokes = []
        arcade.set_background_color([201, 255, 229])

    def setup(self):
        choose_random_pokes(5)
        for i in range(5):
            self.available_pokes.append(f"sprites/{i}")


    def on_draw(self):
        arcade.start_render()
        
        for i in range(1, 5):
            arcade.draw_line(0 , 192*i, SCREEN_WIDTH, 192*i, arcade.color.BLACK, 1)
        for line in LINES:
            line[0].draw()
            line[1].draw()
        for i in range(5):
            arcade.draw_rectangle_outline(202, 96 + 192*i, 20, 192, arcade.color.BLACK, 1)

            poke = Pokemon(self.available_pokes[i], True, "left")
            poke.center_x = 96
            poke.center_y = 96 + 192*i
            poke.draw()
        if self.cursor.poke:
            arcade.draw_rectangle_outline(self.cursor.x, self.cursor.y, 192, 192, arcade.color.BLACK, 3)
        else:
            arcade.draw_rectangle_filled(self.cursor.x, self.cursor.y, 20, 192, arcade.color.BLACK, 1)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.UP and self.cursor.y < SCREEN_HEIGHT - 192:
            self.cursor.y += 192
        elif key == arcade.key.DOWN and self.cursor.y > 192:
            self.cursor.y -= 192
        elif key == arcade.key.LEFT and not self.cursor.poke:
            self.cursor.x -= 106
            self.cursor.poke = True
        elif key == arcade.key.ENTER:
            if self.cursor.poke:
                self.cursor.x += 106
                self.cursor.poke = False
                self.cursor.spawn_poke = self.available_pokes[(self.cursor.y - 96)//192]
            else:
                poke = Pokemon(self.cursor.spawn_poke, True, "left")
                poke.center_x = SCREEN_WIDTH // 2 - 400
                poke.center_y = self.cursor.y
                arcade.schedule(poke.update, 0.5)
                LINES[(self.cursor.y - 96)//192][0].add_poke(poke)


    def on_update(self, delta_time):
        pass



def main():
    time.time()
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()