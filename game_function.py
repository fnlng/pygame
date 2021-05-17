import sys
import time

from bullet import *
from alien import Alien


def start_game(ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    # 重置游戏设置
    ai_settings.initialize_dynamic_settings()

    # 隐藏光标
    pygame.mouse.set_visible(False)

    # 重置游戏统计信息
    stats.reset_stats()
    stats.game_active = True

    # 重置记分牌图像
    scoreboard.prep_image()

    # 清空外星人列表和子弹列表
    aliens.empty()
    bullets.empty()

    # 创建一群新的外星人，并让飞船居中
    create_fleet(ai_settings=ai_settings, screen=screen, ship=ship, aliens=aliens)
    ship.center_ship()


def quit_game(stats):
    try:
        with open("./record.txt", 'w') as f:
            f.write(str(stats.high_score))
    except IOError:
        print('File is not accessible.')
    sys.exit()


def start_high_level(ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    bullets.empty()
    ai_settings.increase_speed()

    # 提高等级
    stats.level += 1
    scoreboard.prep_level()
    create_fleet(ai_settings, screen, ship, aliens)


def check_keydown_events(event, ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    # elif event.key == pygame.K_SPACE:
    #     new_bullet = Bullet(ai_settings, screen, ship)
    #     bullets.add(new_bullet)
    elif event.key == pygame.K_p:
        start_game(ai_settings=ai_settings, screen=screen, stats=stats, scoreboard=scoreboard, ship=ship, aliens=aliens, bullets=bullets)
    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
        quit_game(stats)


def check_keyup_events(event, ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, play_button, scoreboard, ship, aliens, bullets):
    """响应按键和鼠标事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game(stats)

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats, scoreboard, ship, aliens, bullets)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings=ai_settings, screen=screen, stats=stats, play_button=play_button, scoreboard=scoreboard,
                              ship=ship, aliens=aliens, bullets=bullets,
                              mouse_x=mouse_x, mouse_y=mouse_y)


def check_play_button(ai_settings, screen, stats, play_button, scoreboard, ship, aliens, bullets, mouse_x, mouse_y):
    """在玩家单击play按钮时开始新游戏"""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings=ai_settings, screen=screen, stats=stats, scoreboard=scoreboard,
                   ship=ship, aliens=aliens, bullets=bullets)


def fire_bullet(ai_settings, screen, ship, bullets, due, bullet_type):
    if time.time() - due >= 0.3:
        if bullet_type == 0:
            new_bullet = nomal_Bullet(ai_settings, screen, ship)
        elif bullet_type == 1:
            new_bullet = swift_Bullet(ai_settings, screen, ship)
        else:
            new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)
        due = time.time()
    return due


def update_bullets(ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    """更新子弹的位置，并删除已消失的子弹"""
    # 更新子弹的位置
    bullets.update()
    # 删除已消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings=ai_settings, screen=screen, stats=stats, scoreboard=scoreboard, ship=ship, aliens=aliens, bullets=bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    """检测是否有子弹击中了外星人"""
    # 如果是这样，就删除相应的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for alien in collisions.values():
            stats.score += ai_settings.alien_points*len(alien)
            scoreboard.prep_score()
        check_high_score(stats=stats, scoreboard=scoreboard)

    if len(aliens) == 0:
        start_high_level(ai_settings, screen, stats, scoreboard, ship, aliens, bullets)


def check_high_score(stats, scoreboard):
    """检查是否诞生了新的最高分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        scoreboard.prep_high_score()


def get_number_aliens_x(ai_settings, alien_width):
    """计算每行可容纳多少个外星人"""
    available_space_x = ai_settings.screen_width - 2*alien_width
    number_aliens_x = int(available_space_x / (2*alien_width))
    return number_aliens_x


def get_number_aliens_y(ai_settings, ship_height, alien_height):
    available_space_y = (ai_settings.screen_height - (3*alien_height) - ship_height)
    number_rows = int(available_space_y / (2*alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """创建一个外星人并将其放在当前行"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2*alien_width*alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 1.5*alien.rect.height*row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """创建外星人群"""
    # 创建一个外星人，并计算一行可容纳多少个外星人
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_aliens_y = get_number_aliens_y(ai_settings, ship.rect.height, alien.rect.height)
    for row_number in range(number_aliens_y):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def check_fleet_edges(ai_settings, aliens):
    """有外星人到达边缘时采取相应的措施"""
    for alien in aliens:
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """将外星人整体下移，并改变它们的方向"""
    for alien in aliens:
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def check_aliens_bottom(ai_settings, stats, screen, scoreboard, ship, aliens, bullets):
    """检查是否有外星人到达了屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到一样处理
            ship_hit(ai_settings, stats, screen, scoreboard, ship, aliens, bullets)
            break


def update_aliens(ai_settings, stats, screen, scoreboard, ship, aliens, bullets):
    """检查是否有外星人到达屏幕边缘
    然后更新所有外星人的位置
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # 检查外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, scoreboard, ship, aliens, bullets)

    # 检查外星人是否到达屏幕底端
    check_aliens_bottom(ai_settings, stats, screen, scoreboard, ship, aliens, bullets)


def ship_hit(ai_settings, stats, screen, scoreboard, ship, aliens, bullets):
    """响应被外星人撞到的飞船"""
    if stats.ships_left > 0:
        # 将ships_left减1
        stats.ships_left -= 1

        # 更新记分牌
        scoreboard.prep_ships()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并将飞船放到屏幕底端中央
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # 暂停
        time.sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def update_screen(ai_settings, screen, stats, scoreboard, ship, aliens, bullets, play_button):
    """更新屏幕上的图像，并切换到新屏幕"""
    screen.fill(ai_settings.bg_color)

    # 在飞船和外星人后面重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    ship.blitme()

    scoreboard.show_score()

    # 如果游戏处于非活跃状态，就绘制Play按钮
    if not stats.game_active:
        play_button.draw_button()

    # 让最近绘制的屏幕可见
    pygame.display.flip()

