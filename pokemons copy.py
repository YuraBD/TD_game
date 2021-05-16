import arcade
import time
import os
from math import ceil

#from pyglet.window.key import Y
from pokelinkedque import PokeQueue
import arcade.gui
from arcade.gui import UIManager
from poke_chs import choose_random_pokes

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 960
SCREEN_TITLE = "TD game"
POKEMON_SCALING = 2
RIGHT_FACING = 1
LEFT_FACING = 0
MUSIC_VOLUME = 0.2

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
    def __init__(self, sprites_path, friendly, name, hp = 0, attack = 0):
        super().__init__()
        self.hp = hp
        self.attack = attack
        self.is_fighting = False
        self.name = name
        #self.last_update = None
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

        self.fight_textures = []
        self.cur_fight_texture = 0
        for image_name in ('chopping', 'punching','front_default'):
            if friendly:
                texture = arcade.load_texture(f'{sprites_path}/{image_name}.png', flipped_horizontally=True)
            else:
                texture = arcade.load_texture(f'{sprites_path}/{image_name}.png')
            self.fight_textures.append(texture)


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

    def update_fight(self, delta_time):
        self.cur_fight_texture +=1
        if self.cur_fight_texture > 2:
            self.cur_fight_texture = 0
        frame = self.cur_fight_texture
        self.texture = self.fight_textures[frame]

    def update(self, delta_time):
        self.change_x = 15
        self.update_animation()
        self.center_x += self.change_x * self.move_direction
        # if self.move_direction == 1:
        #     poke_list = ENEMY_POKE_QUEUE
        # else:
        #     poke_list = FRIENDLY_POKE_QUEUE
        # for poke in poke_list:
        #     if arcade.check_for_collision(self, poke):
        #         arcade.unschedule(self.update)
        #         arcade.unschedule(poke.update)
        #         if self.move_direction == 1:
        #             self.texture = self.walk_textures[0][1]
        #             poke.texture = poke.walk_textures[0][0]
        #         else:
        #             self.texture = self.walk_textures[0][0]
        #             poke.texture = poke.walk_textures[0][1]


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
        self.cursor = Cursor(96, 96)
        self.available_pokes = []
        self.available_enemy_pokes = []
        arcade.set_background_color([201, 255, 229])
        self.background = None

        self.music_list = []
        self.current_song_index = 0
        self.current_player = None
        self.music = None

    def advance_song(self):
        """ Advance our pointer to the next song. This does NOT start the song. """
        self.current_song_index += 1
        if self.current_song_index >= 0:
            self.current_song_index = 0

    def play_song(self):
        """ Play the song. """
        self.music = arcade.Sound(self.music_list[self.current_song_index], streaming=True)
        self.current_player = self.music.play(MUSIC_VOLUME)

    def setup(self):
        self.background = arcade.load_texture("background.jpg")
        choose_random_pokes(5, "friendly_sprites")
        # choose_random_pokes(10, "enemy_sprites")
        for i in range(5):
            self.available_pokes.append(f"friendly_sprites/{i}")
        # for i in range(10):
        #     self.available_enemy_pokes.append(f"enemy_sprites/{i}")
        for i in range(5):
            poke = Pokemon(self.available_pokes[i], False, "right")
            poke.center_x = SCREEN_WIDTH // 2
            poke.center_y = 96 + 192*i
            arcade.schedule(poke.update, 0.5)
            LINES[i][1].add_poke(poke)

        self.music_list = ["pokemon_battle_theme.mp3"]
        # Array index of what to play
        self.current_song_index = 0
        # Play the song
        self.play_song()

    def check_collision(self):
        for line in LINES:
            try:
                friend = line[0].get_first_poke()
                enemy = line[1].get_first_poke()
                if arcade.check_for_collision(friend, enemy) and not friend.is_fighting and not enemy.is_fighting:
                    arcade.unschedule(friend.update)
                    arcade.unschedule(enemy.update)
                    friend.is_fighting = True
                    enemy.is_fighting = True
                    diff = max(friend.get_points())[0] - min(enemy.get_points())[0]
                    friend.center_x -= diff
                    enemy.center_x += diff
                    friend.texture = friend.walk_textures[0][1]
                    enemy.texture = enemy.walk_textures[0][0]
                    arcade.schedule(friend.update_fight, 0.5)
                    arcade.schedule(enemy.update_fight, 0.5)
            except KeyError:
                continue
        return None

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(212, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)

        for i in range(1, 5):
            arcade.draw_line(0 , 192*i, SCREEN_WIDTH, 192*i, arcade.color.BLACK, 1)

        self.check_collision()

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
        # for line in LINES:
        #     try:
        #         if arcade.check_for_collision(line[0].get_first_poke(), line[1].get_first_poke()):
        #             friend = line[0].get_first_poke()
        #             enemy = line[1].get_first_poke()
        #             arcade.unschedule(friend.update)
        #             arcade.unschedule(enemy.update)
        #     except KeyError:
        #         continue
        position = self.music.get_stream_position(self.current_player)

        # The position pointer is reset to 0 right after we finish the song.
        # This makes it very difficult to figure out if we just started playing
        # or if we are doing playing.
        if position == 0.0:
            self.advance_song()
            self.play_song()

def main():
    time.time()
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()