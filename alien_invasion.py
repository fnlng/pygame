import pygame
from pygame.sprite import Group
import time

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
import game_function as gf


def run_game():
    due = time.time()
    pygame.init()
    ai_settings = Settings()

    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height)
    )
    pygame.display.set_caption("Alien Invasion")
    # 创建play按钮
    play_button = Button(ai_settings=ai_settings, screen=screen, msg="Play")
    # 创建一个用于存储游戏统计信息的实例，并创建记分牌
    stats = GameStats(ai_settings=ai_settings)
    sb = Scoreboard(ai_settings=ai_settings, screen=screen, stats=stats)
    # 创建一艘飞船
    ship = Ship(ai_settings=ai_settings, screen=screen)
    # 创建一个用于存储子弹的编组
    bullets = Group()
    bullet_type = 0
    # 创建外星人群
    aliens = Group()

    gf.create_fleet(ai_settings=ai_settings, screen=screen, ship=ship, aliens=aliens)

    while True:
        gf.update_screen(ai_settings=ai_settings, screen=screen, stats=stats, scoreboard=sb,
                         ship=ship, aliens=aliens, bullets=bullets,
                         play_button=play_button)
        gf.check_events(ai_settings=ai_settings, screen=screen, stats=stats, play_button=play_button, scoreboard=sb,
                        ship=ship, aliens=aliens, bullets=bullets)
        if stats.game_active:
            ship.update()

            due = gf.fire_bullet(ai_settings=ai_settings, screen=screen,
                                 ship=ship, bullets=bullets, due=due, bullet_type=bullet_type)
            gf.update_bullets(ai_settings=ai_settings, screen=screen,
                              stats=stats, scoreboard=sb,
                              ship=ship, aliens=aliens, bullets=bullets)
            gf.update_aliens(ai_settings=ai_settings, stats=stats, screen=screen, scoreboard=sb,
                             ship=ship, aliens=aliens, bullets=bullets)

            # gf.check_events(ai_settings=ai_settings, screen=screen, stats=stats, play_button=play_button, scoreboard=sb,
            #                 ship=ship, aliens=aliens, bullets=bullets)


run_game()
