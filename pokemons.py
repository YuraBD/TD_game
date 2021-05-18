import arcade
import time
import os
from math import ceil

from pokelinkedque import PokeQueue
import arcade.gui
from arcade.gui import UIManager
from poke_chs import choose_random_pokes
import schedule

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 960
SCREEN_TITLE = "TD game"
POKEMON_SCALING = 2
TOWER_SCALING = 0.3
RIGHT_FACING = 1
LEFT_FACING = 0
MUSIC_VOLUME = 0.5


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


class Tower(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = TOWER_SCALING
        self.hp = 1000
        self.texture = arcade.load_texture("tower.png")
        self.destroyed_texture = arcade.load_texture("destroyed_tower.png")
        self.destroyed = False

    def draw_hp(self):
        arcade.draw_text(str(self.hp), self.center_x-20, self.center_y + 10, arcade.color.BLACK, 14)


class Pokemon(arcade.Sprite):
    def __init__(self, sprites_path, friendly, name, stats = [0,0,0]):
        super().__init__()
        self.hp = stats[0]
        self.attack = stats[1]
        self.cost = stats[2]
        self.job = None
        self.attacking_tower = False

        self.name = name

        if friendly:
            self.character_face_direction = RIGHT_FACING
            self.move_direction = 1
        else:
            self.character_face_direction = LEFT_FACING
            self.move_direction = -1
        self.cur_texture = 0
        self.scale = POKEMON_SCALING

        self.walk_textures = list()
        for image_name in ("front_default", "back_default"):
            texture = load_texture_pair(f"{sprites_path}/{image_name}.png")
            self.walk_textures.append(texture)

        frame = self.cur_texture
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

        self.fight_textures = list()
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
        frame = self.cur_texture
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

    def update_fight(self, enemy):
        if self.cur_fight_texture > 2:
            self.cur_fight_texture = 0
        if self.cur_fight_texture == 2:
            enemy.hp -= self.attack
        frame = self.cur_fight_texture
        self.texture = self.fight_textures[frame]
        self.cur_fight_texture +=1

    def update(self):
        self.change_x = 15
        self.update_animation()
        self.center_x += self.change_x * self.move_direction

    def draw_hp(self):
        arcade.draw_text(str(self.hp), self.center_x-10, self.center_y+75, arcade.color.WHITE, 14)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
        self.cursor = Cursor(96, 96)
        self.available_pokes = list()
        self.available_enemy_pokes = list()
        arcade.set_background_color([201, 255, 229])
        self.background = None
        self.fighting_pokes = list()

        self.music_list = list()
        self.current_song_index = 0
        self.current_player = None
        self.music = None

        self.coins = 1000

        self.lines = list()

        self.towers = list()

        self.attacking_pokes = list()

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
        for _ in range(5):
            self.lines.append([PokeQueue(), PokeQueue()])
            self.towers.append(Tower())

        self.background = arcade.load_texture("background.png")
        choose_random_pokes(5, "friendly_sprites")
        # choose_random_pokes(10, "enemy_sprites")
        for i in range(5):
            with open(f"friendly_sprites/{i}/stats.txt", 'r') as stats_file:
                stats = stats_file.readlines()
                stats = [int(stat.strip()) for stat in stats[1:]]
                self.available_pokes.append([f"friendly_sprites/{i}", stats])
        # for i in range(10):
        #     self.available_enemy_pokes.append(f"enemy_sprites/{i}")
        for i in range(5):
            poke = Pokemon(self.available_pokes[i][0], False, "right", self.available_pokes[i][1])
            poke.center_x = SCREEN_WIDTH // 2 + 400
            poke.center_y = 96 + 192*i
            poke.job = schedule.every(0.5).seconds.do(poke.update)
            self.lines[i][1].add_poke(poke)

        self.music_list = ["pokemon_battle_theme.mp3"]
        self.current_song_index = 0
        self.play_song()

    def check_pokes(self):
        for i, line in enumerate(self.lines):
            try:
                friend = line[0].get_first_poke()
                enemy = line[1].get_first_poke()
                collision = arcade.check_for_collision(friend, enemy)
                if collision and not enemy.attacking_tower:
                    line[0].remove_poke()
                    line[1].remove_poke()
                    self.fighting_pokes.append([friend, enemy, line])
                    schedule.cancel_job(friend.job)
                    schedule.cancel_job(enemy.job)
                    diff = max(friend.get_points())[0] - min(enemy.get_points())[0]
                    friend.center_x -= ceil(diff//2) + 5
                    enemy.center_x += ceil(diff//2) + 5
                    friend.texture = friend.walk_textures[0][1]
                    enemy.texture = enemy.walk_textures[0][0]
                    friend.job = schedule.every(0.5).seconds.do(friend.update_fight, enemy = enemy)
                    enemy.job = schedule.every(0.5).seconds.do(enemy.update_fight, enemy = friend)
                elif collision and enemy.attacking_tower:
                    line[0].remove_poke()
                    line[1].remove_poke()
                    self.fighting_pokes.append([friend, enemy, line])
                    schedule.cancel_job(friend.job)
                    diff = max(friend.get_points())[0] - min(enemy.get_points())[0]
                    friend.center_x -= diff + 5
                    friend.texture = friend.walk_textures[0][1]
                    friend.job = schedule.every(0.5).seconds.do(friend.update_fight, enemy = enemy)
            except KeyError:
                pass
            
            try:
                friend = line[0].get_first_poke()
                if min(friend.get_points())[0] >= SCREEN_WIDTH:
                    line[0].remove_poke()
                    self.coins += friend.cost // 3
            except KeyError:
                pass

            try:
                tower = self.towers[i]
                enemy = line[1].get_first_poke()
                if arcade.check_for_collision(enemy, tower):
                    self.attacking_pokes.append([enemy, tower])
                    schedule.cancel_job(enemy.job)
                    enemy.attacking_tower = True
                    diff = max(tower.get_points())[0] - min(enemy.get_points())[0]
                    enemy.center_x += diff + 5
                    enemy.texture = enemy.walk_textures[0][0]
                    enemy.job = schedule.every(0.5).seconds.do(enemy.update_fight, enemy = tower)
            except KeyError:
                pass

        return None

    def check_attacking_pokes(self):
        for enemy, tower in self.attacking_pokes:
            if tower.hp <= 0:
                tower.texture = tower.destroyed_texture

    def check_fighting_pokes(self):
        for friend, enemy, line in self.fighting_pokes:
            if friend.hp <= 0 and enemy.hp <= 0:
                self.fighting_pokes.remove([friend, enemy, line])
                schedule.cancel_job(friend.job)
                schedule.cancel_job(enemy.job)
            elif friend.hp <= 0:
                self.fighting_pokes.remove([friend, enemy, line])
                schedule.cancel_job(friend.job)
                schedule.cancel_job(enemy.job)
                enemy.job = schedule.every(0.5).seconds.do(enemy.update)
                line[1].insert_poke(enemy)
            elif enemy.hp <= 0:
                self.fighting_pokes.remove([friend, enemy, line])
                schedule.cancel_job(friend.job)
                schedule.cancel_job(enemy.job)
                friend.job = schedule.every(0.5).seconds.do(friend.update)
                self.coins += enemy.cost
                line[0].insert_poke(friend)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(212, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)

        for i in range(1, 5):
            arcade.draw_line(0 , 192*i, SCREEN_WIDTH, 192*i, arcade.color.BLACK, 1)

        for line in self.lines:
            line[0].draw()
            line[1].draw()

        for poke_1, poke_2, _ in self.fighting_pokes:
            poke_1.draw()
            poke_1.draw_hp()
            poke_2.draw()
            poke_2.draw_hp()

        for i in range(5):
            arcade.draw_rectangle_outline(202, 96 + 192*i, 20, 192, arcade.color.BLACK, 1)

            poke = Pokemon(self.available_pokes[i][0], True, "left")
            poke.center_x = 96
            poke.center_y = 96 + 192*i
            poke.draw()
        if self.cursor.poke:
            arcade.draw_rectangle_outline(self.cursor.x, self.cursor.y, 192, 192, arcade.color.BLACK, 3)
        else:
            arcade.draw_rectangle_filled(self.cursor.x, self.cursor.y, 20, 192, arcade.color.BLACK)

        for i in range(5):
            with open(f"{self.available_pokes[i][0]}/stats.txt", 'r') as stats_file:
                stats = stats_file.readlines()
                stats = [stat.strip() for stat in stats]
            arcade.draw_text(stats[0], 5, 192*(i+1) - 20, arcade.color.BLACK, 14)
            arcade.draw_text(f"HP: {stats[1]}, Attack: {stats[2]}", 5, 192*i, arcade.color.BLACK, 14)
            arcade.draw_text(f"Price: {stats[3]}", 5, 192*(i+1)-40, arcade.color.BLACK, 14)
        arcade.draw_rectangle_filled(SCREEN_WIDTH-60, SCREEN_HEIGHT- 12, 120, 24, arcade.color.WHITE)
        arcade.draw_text(f"Coins: {self.coins}", SCREEN_WIDTH-118, SCREEN_HEIGHT-21, arcade.color.BLACK, 14)


        for i, tower in enumerate(self.towers):
            tower.center_x = 452
            tower.center_y = 96 + 192*i
            tower.draw()
            tower.draw_hp()


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
                poke = Pokemon(self.cursor.spawn_poke[0], True, "left", self.cursor.spawn_poke[1])
                if self.coins >= poke.cost:
                    poke.center_x = SCREEN_WIDTH // 2 - 400
                    poke.center_y = self.cursor.y
                    poke.job = schedule.every(0.5).seconds.do(poke.update)
                    self.lines[(self.cursor.y - 96)//192][0].add_poke(poke)
                    self.coins -= poke.cost
        elif key == arcade.key.P:
            poke = Pokemon(self.cursor.spawn_poke[0], False, "left", self.cursor.spawn_poke[1])
            poke.center_x = SCREEN_WIDTH // 2 + 400
            poke.center_y = self.cursor.y
            poke.job = schedule.every(0.5).seconds.do(poke.update)
            self.lines[(self.cursor.y - 96)//192][1].add_poke(poke)
        elif key == arcade.key.O:
            self.lines = list()
            for _ in range(5):
                self.lines.append([PokeQueue(), PokeQueue()])


    def on_update(self, delta_time):
        position = self.music.get_stream_position(self.current_player)

        if position == 0.0:
            self.advance_song()
            self.play_song()
        schedule.run_pending()
        self.check_pokes()
        self.check_fighting_pokes()
        self.check_attacking_pokes()


def main():
    time.time()
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()