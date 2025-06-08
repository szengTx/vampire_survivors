
import pygame
import math
import random
import sys
import os

pygame.init()


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hack and slash")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (30, 30, 30)
BLUE = (0, 120, 215)
LIGHT_BLUE = (100, 180, 255)
GRAY = (50, 50, 50)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

MAIN_MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
LEVEL_UP = 4
VICTORY = 5  


# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.original_image = pygame.image.load("images/player.png").convert_alpha()
            self.image = self.original_image
        except:
           
            self.original_image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, BLUE, (15, 15), 15)
            pygame.draw.circle(self.original_image, LIGHT_BLUE, (15, 15), 10)
            self.image = self.original_image
        
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.exp = 0
        self.level = 1
        self.next_level_exp = 50
        self.direction = 0  # 方向
        self.knife_count = 2
        self.exp_radius = 100  # 拾取经验的范围

    def update(self, keys_pressed):
        # 移动控制
        dx, dy = 0, 0
        if keys_pressed[pygame.K_UP]:
            dy = -self.speed
        if keys_pressed[pygame.K_DOWN]:
            dy = self.speed
        if keys_pressed[pygame.K_LEFT]:
            dx = -self.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx = self.speed
            
       
        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(dy, dx))
           
            self.image = pygame.transform.rotate(self.original_image, -self.direction)
            self.rect = self.image.get_rect(center=self.rect.center)
        
        
        self.rect.x += dx
        self.rect.y += dy

        self.rect.clamp_ip(screen.get_rect())

# 近战敌人
class MeleeEnemy(pygame.sprite.Sprite):
    def __init__(self, player, level=1):
        super().__init__()
        try:
            self.image = pygame.image.load("images/enemy.png").convert_alpha()
        except:
            
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.circle(self.image, RED, (12, 12), 12)
        
        self.rect = self.image.get_rect(
            center=random.choice([
                (random.randint(0, SCREEN_WIDTH), random.choice([-100, SCREEN_HEIGHT+100])),
                (random.choice([-100, SCREEN_WIDTH+100]), random.randint(0, SCREEN_HEIGHT))
            ])
        )
       
        self.base_speed = random.randint(2, 4)
        self.speed = self.base_speed + (level - 1) * 0.2  
        self.player = player
        self.health = 20 + (level - 1) * 2  # 每级增加生命值
        self.damage = 1 + (level - 1) // 5  # 每5级增加伤害

    def update(self):
        # 追踪玩家
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            self.rect.x += dx / distance * self.speed
            self.rect.y += dy / distance * self.speed

# 远程敌人
class RangedEnemy(pygame.sprite.Sprite):
    def __init__(self, player, level=1):
        super().__init__()
        try:
            self.image = pygame.image.load("images/enemy2.png").convert_alpha()
        except:
         
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, PURPLE, (15, 15), 15)
        
        self.rect = self.image.get_rect(
            center=random.choice([
                (random.randint(0, SCREEN_WIDTH), random.choice([-100, SCREEN_HEIGHT+100])),
                (random.choice([-100, SCREEN_WIDTH+100]), random.randint(0, SCREEN_HEIGHT))
            ])
        )
      
        self.base_speed = random.randint(1, 3)
        self.speed = self.base_speed + (level - 1) * 0.15  
        self.player = player
        self.health = 15 + (level - 1) * 1.5  
        self.shoot_cooldown = 0
        self.shoot_delay = max(30, 60 - (level - 1) * 2)  
        self.damage = 2 + (level - 1) // 4 

    def update(self):
        
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        distance = math.hypot(dx, dy)
        
        
        if distance < 200:
            if distance != 0:
                self.rect.x -= dx / distance * self.speed * 0.5
                self.rect.y -= dy / distance * self.speed * 0.5
        else:
            if distance != 0:
                self.rect.x += dx / distance * self.speed
                self.rect.y += dy / distance * self.speed
        
        # 射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # 射击
        if distance > 150 and self.shoot_cooldown == 0:
            self.shoot_cooldown = self.shoot_delay
            return True
        return False

# Boss敌人类
class Boss(pygame.sprite.Sprite):
    def __init__(self, player, level=10):
        super().__init__()
        try:
            self.original_image = pygame.image.load("images/boss.png").convert_alpha()
            self.image = self.original_image
            # 调整Boss大小
            self.image = pygame.transform.scale(self.image, (150, 150))
            self.original_image = self.image
        except:
           
            self.original_image = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (200, 0, 0), (60, 60), 60)
            pygame.draw.circle(self.original_image, (255, 100, 100), (60, 60), 50)
            pygame.draw.circle(self.original_image, (255, 50, 50), (60, 60), 40)
            self.image = self.original_image
        
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.speed = 2
        self.player = player
        self.health = 500 + (level - 10) * 100 
        self.shoot_cooldown = 0
        self.shoot_delay = 60  
        self.bullet_damage = 5
        self.bullet_speed = 4
        self.boss_intro_timer = 180 
        self.active = False  # 是否开始行动
        self.rotation_angle = 0  

    def update(self):
        
        if self.boss_intro_timer > 0:
            self.boss_intro_timer -= 1
           
            self.rect.y += 1
           
            self.rotation_angle = (self.rotation_angle + 2) % 360
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            if self.boss_intro_timer <= 0:
                self.active = True
            return False
        
        # 射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
       
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        distance = math.hypot(dx, dy)
        if distance != 0 and distance > 100: 
            self.rect.x += dx / distance * self.speed
            self.rect.y += dy / distance * self.speed
        
        # 射击
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = self.shoot_delay
            return True
        return False
    
    def shoot(self, bullets_group, all_sprites):
        """向四周发射弹幕"""
        directions = 12  
        for i in range(directions):
            angle = i * (360 / directions)
            
            target_x = self.rect.centerx + math.cos(math.radians(angle)) * 1000
            target_y = self.rect.centery + math.sin(math.radians(angle)) * 1000
            
            # 创建子弹
            new_bullet = Bullet(self.rect.center, (target_x, target_y), 
                               speed=self.bullet_speed, 
                               color=(255, 50, 50), 
                               size=12,
                               damage=self.bullet_damage)
            bullets_group.add(new_bullet)
            all_sprites.add(new_bullet)

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, speed=7, color=ORANGE, size=8, damage=2):
        super().__init__()
        try:
            self.image = pygame.image.load("images/bullet.png").convert_alpha()
        except:
           
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = speed
        self.damage = damage
        
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1
        self.vx = dx / distance * speed
        self.vy = dy / distance * speed
        self.lifetime = 180  # 子弹存在时间

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        
        # 边界检测
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

# 武器
class Knife(pygame.sprite.Sprite):
    def __init__(self, player, angle_offset):
        super().__init__()
        try:
            self.original_image = pygame.image.load("images/knife.png").convert_alpha()
            self.image = self.original_image
        except:
          
            self.original_image = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, GREEN, (0, 0, 15, 5))
            self.image = self.original_image
        
        self.rect = self.image.get_rect()
        self.player = player
        self.angle_offset = angle_offset
        self.distance = 50
        self.angle = 0
        self.damage = 10

    def update(self):
        # 旋转逻辑
        self.angle += 5
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(
            center=(
                self.player.rect.centerx + math.cos(math.radians(self.angle + self.angle_offset)) * self.distance,
                self.player.rect.centery + math.sin(math.radians(self.angle + self.angle_offset)) * self.distance
            )
        )

# exp
class ExpOrb(pygame.sprite.Sprite):
    def __init__(self, pos, exp_value=5):
        super().__init__()
        try:
            self.image = pygame.image.load("images/exp.png").convert_alpha()
        except:
          
            self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(self.image, YELLOW, (6, 6), 6)
            pygame.draw.circle(self.image, (255, 200, 0), (6, 6), 3)
        
        self.rect = self.image.get_rect(center=pos)
        self.exp_value = exp_value
        self.lifetime = 300  # 经验球存在时间（帧数）

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=LIGHT_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def check_click(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# 游戏管理类
class Game:
    def __init__(self):
        self.state = MAIN_MENU
        self.player = None
        self.enemies = None
        self.bullets = None
        self.knives = None
        self.exp_orbs = None
        self.all_sprites = None
        self.boss = None  # Boss
        
       
        try:
            self.background = pygame.image.load("images/background.jpg").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
          
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((20, 20, 30))
           
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                radius = random.randint(1, 2)
                pygame.draw.circle(self.background, (150, 150, 180), (x, y), radius)
        
     
        try:
            pygame.mixer.music.load("sound/bgm.mp3")
            pygame.mixer.music.set_volume(0.5)  
            self.music_playing = False
        except:
            print("警告：无法加载背景音乐文件 'bgm.mp3'")
            self.music_playing = False
        
        self.spawn_timer = 0
        self.ranged_spawn_timer = 0
        self.score = 0
        self.game_over = False
        self.last_state = PLAYING  # 用于暂停前记录状态
        self.boss_spawned = False  # Boss是否已生成
       
        button_width, button_height = 200, 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        self.new_game_btn = Button(center_x, 300, button_width, button_height, "new game")
        self.continue_btn = Button(center_x, 400, button_width, button_height, "continue")
        self.resume_btn = Button(center_x, 300, button_width, button_height, "continue")
        self.menu_btn = Button(center_x, 400, button_width, button_height, "main menu")
        self.victory_btn = Button(center_x, 400, button_width, button_height, "back to menu", GREEN)  # 胜利界面按钮
        
        # 升级按钮
        self.health_btn = Button(center_x, 250, button_width, button_height, "+health", GREEN)
        self.speed_btn = Button(center_x, 350, button_width, button_height, "+speed", BLUE)
        self.weapon_btn = Button(center_x, 450, button_width, button_height, "+weapon", YELLOW)
        
        self.init_game()
    
    def init_game(self):
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.knives = pygame.sprite.Group()
        self.exp_orbs = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.boss = None
        self.boss_spawned = False
        self.all_sprites.add(self.player)
        self.spawn_timer = 0
        self.ranged_spawn_timer = 0
        self.score = 0
        self.game_over = False
        
        # 初始化武器
        for i in range(self.player.knife_count):
            self.add_knife(i * (360 / self.player.knife_count))
    
    def add_knife(self, offset):
        new_knife = Knife(self.player, offset)
        self.knives.add(new_knife)
        self.all_sprites.add(new_knife)
        

        
    def play_music(self):
        
        if not self.music_playing:
            try:
                pygame.mixer.music.play(-1) 
                self.music_playing = True
            except:
                pass

    def check_level_up(self):
        if self.player.exp >= self.player.next_level_exp:
            self.player.level += 1
            self.player.exp -= self.player.next_level_exp
            self.player.next_level_exp = int(self.player.next_level_exp * 1.5)
            self.state = LEVEL_UP
            return True
        return False

    def spawn_boss(self):
       
        if not self.boss_spawned:
            self.boss = Boss(self.player, self.player.level)
            self.enemies.add(self.boss)
            self.all_sprites.add(self.boss)
            self.boss_spawned = True
           
            print("Boss已生成！")

    def run(self):
        running = True
        while running:
            dt = clock.tick(60) / 1000
            mouse_pos = pygame.mouse.get_pos()
            keys_pressed = pygame.key.get_pressed()

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # 主菜单事件处理
                if self.state == MAIN_MENU:
                    self.new_game_btn.check_hover(mouse_pos)
                    self.continue_btn.check_hover(mouse_pos)
                    
                    if self.new_game_btn.check_click(mouse_pos, event):
                        self.init_game()
                        self.state = PLAYING
                        self.play_music() 
                    elif self.continue_btn.check_click(mouse_pos, event):
                        self.init_game()
                        self.state = PLAYING
                        self.play_music()  
                
                # 暂停菜单事件处理
                elif self.state == PAUSED:
                    self.resume_btn.check_hover(mouse_pos)
                    self.menu_btn.check_hover(mouse_pos)
                    
                    if self.resume_btn.check_click(mouse_pos, event):
                        self.state = self.last_state
                    elif self.menu_btn.check_click(mouse_pos, event):
                        self.state = MAIN_MENU
                
                # 升级菜单
                elif self.state == LEVEL_UP:
                    self.health_btn.check_hover(mouse_pos)
                    self.speed_btn.check_hover(mouse_pos)
                    self.weapon_btn.check_hover(mouse_pos)
                    
                    if self.health_btn.check_click(mouse_pos, event):
                        self.player.max_health += 20
                        self.player.health = self.player.max_health
                        self.state = PLAYING
                    elif self.speed_btn.check_click(mouse_pos, event):
                        self.player.speed += 1
                        self.state = PLAYING
                    elif self.weapon_btn.check_click(mouse_pos, event):
                        self.player.knife_count += 1
                        # 修复bug：清除所有旧的飞刀！！！
                        for knife in self.knives:
                            knife.kill()
                        # 重新创建所有飞刀
                        for i in range(self.player.knife_count):
                            self.add_knife(i * (360 / self.player.knife_count))
                        self.state = PLAYING
                
                # 胜利界面
                elif self.state == VICTORY:
                    self.victory_btn.check_hover(mouse_pos)
                    if self.victory_btn.check_click(mouse_pos, event):
                        self.state = MAIN_MENU
            
            # 键盘esc
            if keys_pressed[pygame.K_ESCAPE]:
                if self.state == PLAYING:
                    self.last_state = self.state
                    self.state = PAUSED
                elif self.state == PAUSED:
                    self.state = self.last_state
                elif self.state == GAME_OVER:
                    self.state = MAIN_MENU
                elif self.state == VICTORY:
                    self.state = MAIN_MENU
            
            # 绘制背景
            screen.blit(self.background, (0, 0))
            
            
            if self.state == MAIN_MENU:
                self.draw_main_menu()
            elif self.state == PLAYING:
                self.update_game(dt, keys_pressed)
                self.draw_game()
            elif self.state == PAUSED:
                self.draw_game()
                self.draw_pause_menu()
            elif self.state == GAME_OVER:
                self.draw_game()
                self.draw_game_over()
            elif self.state == LEVEL_UP:
                self.draw_game()
                self.draw_level_up_menu()
            elif self.state == VICTORY:
                self.draw_game()
                self.draw_victory_screen()

            pygame.display.flip()

        pygame.quit()
        sys.exit()
    
    def update_game(self, dt, keys_pressed):
        if not self.game_over:
            # 更新玩家
            self.player.update(keys_pressed)

            # 是否需要生成Boss
            if self.player.level >= 10 and not self.boss_spawned:
                self.spawn_boss()

            # 根据玩家等级调整敌人生成速度
            level_factor = 1 + (self.player.level - 1) * 0.1  
            melee_spawn_rate = max(0.1, 0.8 / level_factor)  
            ranged_spawn_rate = max(1.0, 5.0 / level_factor) 
            
            # 生成的敌人数
            melee_spawn_count = 1 + (self.player.level - 1) // 5  
            ranged_spawn_count = 1 + (self.player.level - 1) // 10  # 每10级增加1个远程敌人

            # 生成近战
            self.spawn_timer += dt
            if self.spawn_timer >= melee_spawn_rate:
                for _ in range(melee_spawn_count):
                    self.enemies.add(MeleeEnemy(self.player, self.player.level))
                    self.all_sprites.add(self.enemies)
                self.spawn_timer = 0
            
            # 生成远程
            self.ranged_spawn_timer += dt
            if self.ranged_spawn_timer >= ranged_spawn_rate:
                for _ in range(ranged_spawn_count):
                    self.enemies.add(RangedEnemy(self.player, self.player.level))
                    self.all_sprites.add(self.enemies)
                self.ranged_spawn_timer = 0

            
            for enemy in self.enemies:
                # 修复bug：正确处理远程敌人的射击
                if isinstance(enemy, RangedEnemy):
                    if enemy.update():  
                        new_bullet = Bullet(enemy.rect.center, self.player.rect.center)
                        self.bullets.add(new_bullet)
                        self.all_sprites.add(new_bullet)
                
                elif isinstance(enemy, Boss):
                    if enemy.update(): 
                        enemy.shoot(self.bullets, self.all_sprites)
                else:
                    enemy.update()  

            # 更新子弹
            self.bullets.update()

            # 武器碰撞检测
            for enemy in self.enemies:
                for knife in self.knives:
                    if pygame.sprite.collide_circle(enemy, knife):
                        enemy.health -= knife.damage
                        if enemy.health <= 0:
                            
                            if isinstance(enemy, Boss):
                                self.state = VICTORY
                                try:
                                    pygame.mixer.music.stop()
                                    self.music_playing = False
                                except:
                                    pass
                                
                                enemy.kill()
                                self.boss = None
                            else:
                                enemy.kill()
                                self.score += 15 if isinstance(enemy, RangedEnemy) else 10
                                # 掉落经验球
                                exp_orb = ExpOrb(enemy.rect.center)
                                self.exp_orbs.add(exp_orb)
                                self.all_sprites.add(exp_orb)

            # 玩家与经验球碰撞检测
            for exp_orb in self.exp_orbs:
              
                dx = exp_orb.rect.centerx - self.player.rect.centerx
                dy = exp_orb.rect.centery - self.player.rect.centery
                distance = math.hypot(dx, dy)
                
                if distance < self.player.exp_radius:
                   
                    if distance > 5:
                        exp_orb.rect.x -= dx / distance * 5
                        exp_orb.rect.y -= dy / distance * 5
                    else:
                        self.player.exp += exp_orb.exp_value
                        self.check_level_up()
                        exp_orb.kill()

            # 玩家碰撞检测
            if pygame.sprite.spritecollide(self.player, self.enemies, False):
                for enemy in self.enemies:
                    if pygame.sprite.collide_rect(self.player, enemy):
                        self.player.health -= enemy.damage
                        if self.player.health <= 0:
                            self.game_over = True
                            self.state = GAME_OVER
                            try:
                                pygame.mixer.music.stop()  
                                self.music_playing = False
                            except:
                                pass
            
            # 子弹碰撞检测
            if pygame.sprite.spritecollide(self.player, self.bullets, True):
                self.player.health -= 2
                if self.player.health <= 0:
                    self.game_over = True
                    self.state = GAME_OVER
                    try:
                        pygame.mixer.music.stop() 
                        self.music_playing = False
                    except:
                        pass

            # 更新武器
            self.knives.update()
            
            # 更新经验球
            self.exp_orbs.update()

    def draw_main_menu(self):
        # 绘制标题
        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render("Survivor game", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title_text, title_rect)
        
        # 绘制版本信息
        version_font = pygame.font.Font(None, 24)
        version_text = version_font.render("Use UP DOWN LEFT RIGHT to move, ESC to pause", True, WHITE)
        version_rect = version_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-50))
        screen.blit(version_text, version_rect)
        
        # 绘制按钮
        self.new_game_btn.draw(screen)
        self.continue_btn.draw(screen)
        
        # 绘制游戏元素预览
        preview_font = pygame.font.Font(None, 30)
        preview_text = preview_font.render("Game Elements Preview", True, WHITE)
        preview_rect = preview_text.get_rect(center=(SCREEN_WIDTH//2, 470))
        screen.blit(preview_text, preview_rect)
        
        # 玩家预览
        try:
            player_img = pygame.image.load("images/player.png").convert_alpha()
            player_img = pygame.transform.scale(player_img, (60, 60))
        except:
            player_img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(player_img, BLUE, (30, 30), 30)
            pygame.draw.circle(player_img, LIGHT_BLUE, (30, 30), 20)
        screen.blit(player_img, (SCREEN_WIDTH//2 - 180, 500))
        
        player_text = preview_font.render("Player", True, LIGHT_BLUE)
        player_text_rect = player_text.get_rect(center=(SCREEN_WIDTH//2 - 180, 580))
        screen.blit(player_text, player_text_rect)




        
        # 近战敌人预览
        try:
            melee_img = pygame.image.load("images/enemy.png").convert_alpha()
            melee_img = pygame.transform.scale(melee_img, (50, 50))
        except:
            melee_img = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(melee_img, RED, (25, 25), 25)
        screen.blit(melee_img, (SCREEN_WIDTH//2 - 80, 500))
        
        melee_text = preview_font.render("Melee", True, RED)
        melee_text_rect = melee_text.get_rect(center=(SCREEN_WIDTH//2 - 80, 580))
        screen.blit(melee_text, melee_text_rect)
        
        # 远程敌人预览
        try:
            ranged_img = pygame.image.load("images/enemy2.png").convert_alpha()
            ranged_img = pygame.transform.scale(ranged_img, (50, 50))
        except:
            ranged_img = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(ranged_img, PURPLE, (25, 25), 25)
        screen.blit(ranged_img, (SCREEN_WIDTH//2 + 20, 500))
        
        ranged_text = preview_font.render("Ranged", True, PURPLE)
        ranged_text_rect = ranged_text.get_rect(center=(SCREEN_WIDTH//2 + 20, 580))
        screen.blit(ranged_text, ranged_text_rect)
        
        # Boss预览
        try:
            boss_img = pygame.image.load("images/boss.png").convert_alpha()
            boss_img = pygame.transform.scale(boss_img, (70, 70))
        except:
            boss_img = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(boss_img, (200, 0, 0), (35, 35), 35)
        screen.blit(boss_img, (SCREEN_WIDTH//2 + 120, 500))
        
        boss_text = preview_font.render("Boss", True, (200, 0, 0))
        boss_text_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2 + 120, 580))
        screen.blit(boss_text, boss_text_rect)

    def draw_game(self):
        
        for sprite in self.all_sprites:
            screen.blit(sprite.image, sprite.rect)
        
       
        # 绘制UI
        self.draw_ui()
        
      
        if self.boss and not self.boss.active:
            warning_font = pygame.font.Font(None, 72)
            warning_text = warning_font.render("BOSS INCOMING!", True, (255, 50, 50))
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(warning_text, warning_rect)

    def draw_pause_menu(self):
      
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 暂停标题
        pause_font = pygame.font.Font(None, 72)
        pause_text = pause_font.render("PAUSED", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        screen.blit(pause_text, pause_rect)
        
        # 绘制按钮
        self.resume_btn.draw(screen)
        self.menu_btn.draw(screen)
        
        tip_font = pygame.font.Font(None, 30)
        tip_text = tip_font.render("Press ESC to resume", True, WHITE)
        tip_rect = tip_text.get_rect(center=(SCREEN_WIDTH//2, 500))
        screen.blit(tip_text, tip_rect)

    def draw_level_up_menu(self):
    
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 升级标题
        level_font = pygame.font.Font(None, 72)
        level_text = level_font.render(f"LEVEL UP! - {self.player.level}", True, YELLOW)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(level_text, level_rect)
     
        tip_font = pygame.font.Font(None, 36)
        tip_text = tip_font.render("Choose an upgrade:", True, WHITE)
        tip_rect = tip_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        screen.blit(tip_text, tip_rect)
        
        # 绘制升级按钮
        self.health_btn.draw(screen)
        self.speed_btn.draw(screen)
        self.weapon_btn.draw(screen)
        
        
        desc_font = pygame.font.Font(None, 24)
        
        health_desc = desc_font.render(f"Max Health: {self.player.max_health} → {self.player.max_health + 20}", True, GREEN)
        health_desc_rect = health_desc.get_rect(center=(SCREEN_WIDTH//2, 290))
        screen.blit(health_desc, health_desc_rect)
        
        speed_desc = desc_font.render(f"Speed: {self.player.speed} → {self.player.speed + 1}", True, LIGHT_BLUE)
        speed_desc_rect = speed_desc.get_rect(center=(SCREEN_WIDTH//2, 390))
        screen.blit(speed_desc, speed_desc_rect)
        
        weapon_desc = desc_font.render(f"Weapons: {self.player.knife_count} → {self.player.knife_count + 1}", True, YELLOW)
        weapon_desc_rect = weapon_desc.get_rect(center=(SCREEN_WIDTH//2, 490))
        screen.blit(weapon_desc, weapon_desc_rect)

    def draw_ui(self):
      
        ui_bg = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        ui_bg.fill((30, 30, 30, 200))
        screen.blit(ui_bg, (0, 0))
        
        # 血条
        pygame.draw.rect(screen, (80, 80, 80), (20, 20, 204, 24), border_radius=5)
        health_width = 200 * (self.player.health / self.player.max_health)
        health_rect = pygame.Rect(22, 22, health_width, 20)
        pygame.draw.rect(screen, GREEN, health_rect, border_radius=4)
        
        # 血量文本
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"{self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (230, 22))
        
        # 经验条
        pygame.draw.rect(screen, (80, 80, 80), (20, 50, 204, 14), border_radius=5)
        exp_width = 200 * (self.player.exp / self.player.next_level_exp)
        exp_rect = pygame.Rect(22, 52, exp_width, 10)
        pygame.draw.rect(screen, YELLOW, exp_rect, border_radius=4)
        
        
        level_font = pygame.font.Font(None, 36)
        level_text = level_font.render(f"Level: {self.player.level}", True, WHITE)
        screen.blit(level_text, (300, 20))
        
        score_text = level_font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (300, 60))
        
        # 武器
        weapons_text = level_font.render(f"Weapons: {self.player.knife_count}", True, YELLOW)
        screen.blit(weapons_text, (500, 20))
        
        # 敌人数量
        enemies_text = level_font.render(f"Enemies: {len(self.enemies)}", True, RED)
        screen.blit(enemies_text, (700, 20))
        
        # 难度
        difficulty_text = level_font.render(f"Difficulty: {self.player.level}", True, PURPLE)
        screen.blit(difficulty_text, (700, 60))
        
        # Boss血量显示
        if self.boss and self.boss.active:
            
            pygame.draw.rect(screen, (80, 80, 80), (SCREEN_WIDTH//2 - 150, 10, 300, 20), border_radius=5)
            # 血条
            boss_health_width = 296 * (self.boss.health / (500 + (self.player.level - 10) * 100))
            boss_health_rect = pygame.Rect(SCREEN_WIDTH//2 - 148, 12, boss_health_width, 16)
            pygame.draw.rect(screen, (200, 0, 0), boss_health_rect, border_radius=4)
            
            
            boss_text = level_font.render("BOSS", True, (255, 100, 100))
            screen.blit(boss_text, (SCREEN_WIDTH//2 - 180, 12))
            
            # Boss血量数值
            boss_hp_text = font.render(f"{self.boss.health}/{(500 + (self.player.level - 10) * 100)}", True, WHITE)
            screen.blit(boss_hp_text, (SCREEN_WIDTH//2 + 160, 12))
        
        # 暂停提示
        if self.state == PLAYING:
            tip_font = pygame.font.Font(None, 24)
            tip_text = tip_font.render("ESC: Pause Game", True, LIGHT_BLUE)
            screen.blit(tip_text, (SCREEN_WIDTH - 150, 20))

    def draw_game_over(self):
      
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # 游戏结束标题
        font = pygame.font.Font(None, 72)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(text, text_rect)
        
        # 显示分数
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Final Score: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(score_text, score_rect)
        
        # 显示等级
        level_text = score_font.render(f"Level: {self.player.level}", True, LIGHT_BLUE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
        screen.blit(level_text, level_rect)
        
        # 显示难度
        difficulty_text = score_font.render(f"Difficulty Level: {self.player.level}", True, PURPLE)
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
        screen.blit(difficulty_text, difficulty_rect)
        
        tip_font = pygame.font.Font(None, 36)
        tip_text = tip_font.render("Press ESC to return to main menu", True, LIGHT_BLUE)
        tip_rect = tip_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 180))
        screen.blit(tip_text, tip_rect)
    
    def draw_victory_screen(self):
      
       
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
       
        font = pygame.font.Font(None, 72)
        text = font.render("VICTORY!", True, GREEN)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(text, text_rect)
     
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Final Score: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(score_text, score_rect)
        
        level_text = score_font.render(f"Level: {self.player.level}", True, LIGHT_BLUE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(level_text, level_rect)
        
      
        boss_text = score_font.render("You have defeated the Boss!", True, (255, 100, 100))
        boss_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
        screen.blit(boss_text, boss_rect)
        

        # 绘制按钮
        self.victory_btn.draw(screen)
       
        tip_font = pygame.font.Font(None, 36)
        tip_text = tip_font.render("Press ESC or click button to return to menu", True, LIGHT_BLUE)
        tip_rect = tip_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 180))
        screen.blit(tip_text, tip_rect)

if __name__ == "__main__":
    game = Game()
    game.run()