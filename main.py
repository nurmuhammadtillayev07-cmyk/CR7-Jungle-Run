"""
CR7 Jungle Run - Full Edition (Rotatsiya qo'llab-quvvatlanadi)
Pygame o'yin - Pydroid 3 / Android uchun moslashtirilgan
"""

import pygame
import random
import sys
import math
import json
import os

try:
    import numpy as np
    NUMPY_OK = True
except Exception:
    NUMPY_OK = False

pygame.init()

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    MIXER_OK = True
except Exception:
    MIXER_OK = False

# ----------------- ASOSIY SOZLAMALAR -----------------
VIRTUAL_WIDTH = 960
VIRTUAL_HEIGHT = 480
FPS = 90
GROUND_Y = 370

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
GOLD = (255, 195, 0)
SKY_TOP_DAY = (135, 206, 235)
SKY_BOTTOM_DAY = (240, 255, 240)
SKY_TOP_NIGHT = (10, 12, 45)
SKY_BOTTOM_NIGHT = (45, 45, 75)
JUNGLE_FAR = (40, 80, 40)
JUNGLE_MID = (30, 65, 30)
GROUND_COLOR = (101, 67, 33)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
BLUE = (70, 130, 220)
PINK = (255, 105, 180)
ORANGE = (255, 140, 0)

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cr7_save.json")

QUALITY_SETTINGS = {
    "high": {"trees_skip": 1, "rain_count": 40, "particle_mult": 1.0, "dust": True, "stars": 40},
    "low": {"trees_skip": 2, "rain_count": 16, "particle_mult": 0.5, "dust": False, "stars": 15},
}

# ----------------- SAQLASH TIZIMI -----------------

def load_save():
    default = {
        "high_score": 0,
        "total_coins": 0,
        "sound_on": True,
        "music_on": True,
        "graphics": "high",
    }
    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
            default.update(data)
    except Exception:
        pass
    return default


def write_save(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


# ----------------- OVOZ TIZIMI -----------------

def make_tone(freq=440.0, duration=0.15, volume=0.4, wave="sine"):
    if not (NUMPY_OK and MIXER_OK):
        return None
    try:
        sample_rate = 22050
        n = max(1, int(sample_rate * duration))
        t = np.linspace(0, duration, n, False)
        if wave == "sine":
            data = np.sin(freq * t * 2 * np.pi)
        elif wave == "square":
            data = np.sign(np.sin(freq * t * 2 * np.pi))
        elif wave == "noise":
            data = np.random.uniform(-1, 1, n)
        else:
            data = np.sin(freq * t * 2 * np.pi)
        envelope = np.linspace(1, 0, n)
        data = data * envelope
        audio = (data * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(audio)
    except Exception:
        return None


def make_chirp(f0=300.0, f1=700.0, duration=0.2, volume=0.4):
    if not (NUMPY_OK and MIXER_OK):
        return None
    try:
        sample_rate = 22050
        n = max(1, int(sample_rate * duration))
        t = np.linspace(0, duration, n, False)
        freq_t = np.linspace(f0, f1, n)
        phase = 2 * np.pi * np.cumsum(freq_t) / sample_rate
        data = np.sin(phase)
        envelope = np.linspace(1, 0, n)
        data = data * envelope
        audio = (data * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(audio)
    except Exception:
        return None


def make_music_loop():
    if not (NUMPY_OK and MIXER_OK):
        return None
    try:
        sample_rate = 22050
        duration = 4.0
        n = int(sample_rate * duration)
        t = np.linspace(0, duration, n, False)
        freqs = [130.81, 164.81, 196.00]
        data = np.zeros(n)
        for f in freqs:
            data += np.sin(2 * np.pi * f * t)
        data /= len(freqs)
        tremolo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * t)
        data *= tremolo
        audio = (data * 0.18 * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(audio)
    except Exception:
        return None


class SoundManager:
    def __init__(self, save_data):
        self.enabled = NUMPY_OK and MIXER_OK
        self.sound_on = save_data.get("sound_on", True)
        self.music_on = save_data.get("music_on", True)
        self.sounds = {}
        self.music = None
        if self.enabled:
            try:
                self.sounds["jump"] = make_chirp(350, 750, 0.16, 0.35)
                self.sounds["coin"] = make_tone(1300, 0.12, 0.35, "sine")
                self.sounds["hit"] = make_tone(130, 0.18, 0.5, "noise")
                self.sounds["button"] = make_tone(700, 0.05, 0.25, "square")
                self.sounds["powerup"] = make_chirp(400, 1000, 0.25, 0.35)
                self.sounds["levelup"] = make_chirp(500, 1100, 0.35, 0.4)
                self.sounds["ball"] = make_tone(900, 0.1, 0.3, "sine")
                self.music = make_music_loop()
            except Exception:
                self.enabled = False

    def play(self, name):
        if self.enabled and self.sound_on:
            snd = self.sounds.get(name)
            if snd:
                try:
                    snd.play()
                except Exception:
                    pass

    def play_music(self):
        if self.enabled and self.music_on and self.music:
            try:
                self.music.play(loops=-1)
            except Exception:
                pass

    def stop_music(self):
        if self.enabled and self.music:
            try:
                self.music.stop()
            except Exception:
                pass

    def toggle_sound(self):
        self.sound_on = not self.sound_on

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            self.play_music()
        else:
            self.stop_music()


# --- ROTATSIYA VA EKRAN SOZLAMALARI ---
# Boshlanishida ekranning joriy o'lchamlarini aniqlaymiz
display_info = pygame.display.Info()
REAL_WIDTH = display_info.current_w
REAL_HEIGHT = display_info.current_h

# Agar telefon xato qiymat qaytarsa, standart o'lcham beramiz
if REAL_WIDTH <= 0 or REAL_HEIGHT <= 0:
    REAL_WIDTH, REAL_HEIGHT = VIRTUAL_WIDTH, VIRTUAL_HEIGHT

# pygame.RESIZABLE bayrog'i telefon aylanayotganda ekranni moslashtirish imkonini beradi
screen = pygame.display.set_mode((REAL_WIDTH, REAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("CR7 Jungle Run")

virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
clock = pygame.time.Clock()

try:
    font_small = pygame.font.Font(None, 24)
    font_medium = pygame.font.Font(None, 32)
    font_large = pygame.font.Font(None, 64)
except Exception:
    class DummyFont:
        def render(self, text, antialias, color, background=None):
            return pygame.Surface((10, 10))
        def get_width(self):
            return 10
        def get_height(self):
            return 10
    font_small = DummyFont()
    font_medium = DummyFont()
    font_large = DummyFont()


# ----------------- SPRITE YUKLASH TIZIMI -----------------

SPRITE_SRC_W = 70
SPRITE_SRC_H = 110
SPRITE_COLS = 8
SPRITE_DRAW_W = 62
SPRITE_DRAW_H = 96
SPRITE_FOOT_MARGIN = int(6 * SPRITE_DRAW_H / SPRITE_SRC_H)


def load_player_sprites():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "player_sprites.png")
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except Exception:
        return None
    try:
        rows = ["run", "jump", "duck"]
        frames = {"run": [], "jump": [], "duck": []}
        for r, key in enumerate(rows):
            for c in range(SPRITE_COLS):
                rect = pygame.Rect(c * SPRITE_SRC_W, r * SPRITE_SRC_H, SPRITE_SRC_W, SPRITE_SRC_H)
                sub = sheet.subsurface(rect).copy()
                scaled = pygame.transform.smoothscale(sub, (SPRITE_DRAW_W, SPRITE_DRAW_H))
                frames[key].append(scaled)
        return frames
    except Exception:
        return None


# ----------------- O'YIN ELEMENTLARI -----------------

class Player:
    def __init__(self, sprites=None):
        self.x = 200
        self.ground_y = GROUND_Y
        self.width = 44
        self.height = 80
        self.base_height = 80
        self.y = self.ground_y - self.height

        self.vel_y = 0
        self.gravity = 0.95
        self.jump_strength = -16.5

        self.is_jumping = False
        self.is_ducking = False

        self.frame_timer = 0
        self.run_frame = 0
        self.squash = 1.0

        self.sprites = sprites
        self.has_sprites = sprites is not None
        self.run_timer = 0
        self.run_index = 0
        self.duck_timer = 0
        self.duck_index = 0

    def jump(self, sound=None):
        if not self.is_jumping and not self.is_ducking:
            self.is_jumping = True
            self.vel_y = self.jump_strength
            self.squash = 1.15
            if sound:
                sound.play("jump")

    def duck(self, state):
        self.is_ducking = state
        if state and not self.is_jumping:
            self.height = 45
            self.y = self.ground_y - self.height
        elif not state and not self.is_jumping:
            self.height = self.base_height
            self.y = self.ground_y - self.height

    def update(self):
        landed = False
        if self.is_jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y
            if self.y >= self.ground_y - self.height:
                self.y = self.ground_y - self.height
                self.is_jumping = False
                self.vel_y = 0
                self.squash = 0.8
                landed = True

        if self.squash < 1.0:
            self.squash = min(1.0, self.squash + 0.025)
        elif self.squash > 1.0:
            self.squash = max(1.0, self.squash - 0.025)

        self.frame_timer += 1
        if self.frame_timer % 5 == 0:
            self.run_frame = (self.run_frame + 1) % 4

        if not self.is_jumping:
            if self.is_ducking:
                self.duck_timer += 1
                if self.duck_timer % 4 == 0:
                    self.duck_index = (self.duck_index + 1) % SPRITE_COLS
            else:
                self.run_timer += 1
                if self.run_timer % 4 == 0:
                    self.run_index = (self.run_index + 1) % SPRITE_COLS

        return landed

    def draw(self, surface, invuln=False, frame_count=0):
        if invuln and (frame_count // 4) % 2 == 0:
            return

        if self.has_sprites:
            self._draw_sprite(surface)
        else:
            self._draw_fallback(surface)

    def _draw_sprite(self, surface):
        if self.is_jumping:
            jmin, jmax = self.jump_strength, 14.0
            t = (self.vel_y - jmin) / (jmax - jmin)
            t = max(0.0, min(1.0, t))
            idx = int(t * (SPRITE_COLS - 1))
            frame = self.sprites["jump"][idx]
        elif self.is_ducking:
            frame = self.sprites["duck"][self.duck_index]
        else:
            frame = self.sprites["run"][self.run_index]

        feet_y = self.y + self.height
        draw_x = self.x + self.width // 2 - SPRITE_DRAW_W // 2
        draw_y = feet_y - SPRITE_DRAW_H + SPRITE_FOOT_MARGIN
        surface.blit(frame, (draw_x, draw_y))

    def _draw_fallback(self, surface):
        cx = self.x + self.width // 2
        bob = 0
        if not self.is_jumping and not self.is_ducking:
            bob = -abs(math.sin(self.run_frame * math.pi / 2)) * 3
        cy = self.y + bob

        leg_offset = 6 if self.run_frame % 2 == 0 else -6
        arm_offset = -leg_offset
        if self.is_jumping:
            leg_offset = 4
            arm_offset = -8

        if self.is_ducking and not self.is_jumping:
            pygame.draw.circle(surface, (244, 194, 194), (cx + 12, int(cy) + 12), 10)
            pygame.draw.circle(surface, BLACK, (cx + 14, int(cy) + 8), 8)
            pygame.draw.rect(surface, RED, (cx - 20, cy + 16, 32, 18))
            pygame.draw.rect(surface, GREEN, (cx - 20, cy + 34, 32, 10))
            pygame.draw.rect(surface, WHITE, (cx - 15, cy + 44, 12, 6))
            pygame.draw.rect(surface, WHITE, (cx + 2, cy + 44, 12, 6))
            num_lbl = font_small.render("7", True, YELLOW)
            surface.blit(num_lbl, (cx - 8, cy + 16))
        else:
            pygame.draw.line(surface, (244, 194, 194), (cx - 18, cy + 28), (cx - 18 + arm_offset, cy + 45), 5)
            pygame.draw.line(surface, (244, 194, 194), (cx + 18, cy + 28), (cx + 18 - arm_offset, cy + 45), 5)
            pygame.draw.circle(surface, (244, 194, 194), (cx, int(cy) + 12), 11)
            pygame.draw.circle(surface, BLACK, (cx, int(cy) + 6), 9)
            pygame.draw.rect(surface, RED, (cx - 18, cy + 23, 36, 30))
            pygame.draw.rect(surface, GREEN, (cx - 18, cy + 53, 36, 18))
            pygame.draw.rect(surface, WHITE, (cx - 16, cy + 71 + leg_offset, 12, 9))
            pygame.draw.rect(surface, WHITE, (cx + 4, cy + 71 - leg_offset, 12, 9))
            num_lbl = font_medium.render("7", True, YELLOW)
            surface.blit(num_lbl, (cx - 5, int(cy) + 28))

    @property
    def rect(self):
        return pygame.Rect(self.x + 4, self.y, self.width - 8, self.height)


class Obstacle:
    def __init__(self, speed):
        self.width = 44
        self.type = random.choice(["low", "mid", "high"])

        if self.type == "low":
            self.height = 45
            self.y = GROUND_Y - self.height
        elif self.type == "mid":
            self.height = 68
            self.y = GROUND_Y - self.height
        else:
            self.height = 50
            self.y = 270

        self.x = VIRTUAL_WIDTH + random.randint(10, 80)
        self.speed = speed
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, (139, 69, 19), (self.x, self.y, self.width, self.height))
        brick_h = 8
        for i in range(int(self.height / brick_h) + 1):
            cy = self.y + i * brick_h
            if cy < self.y + self.height:
                pygame.draw.line(surface, LIGHT_GRAY, (self.x, cy), (self.x + self.width, cy), 1)
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Coin:
    def __init__(self, speed):
        self.x = VIRTUAL_WIDTH + random.randint(100, 400)
        self.y = random.randint(170, 280)
        self.base_radius = 16
        self.radius = self.base_radius
        self.speed = speed
        self.collected = False
        self.timer = random.randint(0, 100)

    def update(self):
        self.x -= self.speed
        self.timer += 1
        self.radius = self.base_radius + math.sin(self.timer * 0.2) * 3

    def draw(self, surface):
        r = max(4, int(self.radius))
        pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), r, 2)
        pygame.draw.circle(surface, YELLOW, (int(self.x) - 4, int(self.y) - 4), max(2, r // 3))

    @property
    def rect(self):
        return pygame.Rect(self.x - self.base_radius, self.y - self.base_radius,
                            self.base_radius * 2, self.base_radius * 2)


class FootBall:
    def __init__(self, speed):
        self.x = VIRTUAL_WIDTH + random.randint(150, 500)
        self.y = random.choice([200, 250, 300])
        self.radius = 14
        self.speed = speed
        self.collected = False
        self.rotation = 0

    def update(self):
        self.x -= self.speed
        self.rotation = (self.rotation + 6) % 360

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        rad = math.radians(self.rotation)
        for i in range(5):
            a = rad + i * (2 * math.pi / 5)
            x2 = self.x + math.cos(a) * self.radius * 0.6
            y2 = self.y + math.sin(a) * self.radius * 0.6
            pygame.draw.line(surface, BLACK, (self.x, self.y), (x2, y2), 1)

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


class PowerUp:
    def __init__(self, speed, kind):
        self.kind = kind
        self.x = VIRTUAL_WIDTH + random.randint(200, 600)
        self.y = random.choice([190, 230, 270])
        self.radius = 16
        self.speed = speed
        self.collected = False
        self.timer = 0

    def update(self):
        self.x -= self.speed
        self.timer += 1

    def draw(self, surface):
        pulse = 2 * math.sin(self.timer * 0.15)
        r = max(4, int(self.radius + pulse))
        color = BLUE if self.kind == "shield" else PINK
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), r, 2)
        label = "S" if self.kind == "shield" else ">>"
        lbl = font_small.render(label, True, WHITE)
        surface.blit(lbl, (self.x - lbl.get_width() // 2, self.y - lbl.get_height() // 2))

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=3, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        ratio = max(0.0, self.life / self.max_life)
        alpha = max(0, min(255, int(255 * ratio)))
        s = max(1, int(self.size * ratio) + 1)
        temp = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, (self.color[0], self.color[1], self.color[2], alpha), (s, s), s)
        surface.blit(temp, (self.x - s, self.y - s))

    @property
    def alive(self):
        return self.life > 0


class RainDrop:
    def __init__(self):
        self.x = random.randint(0, VIRTUAL_WIDTH)
        self.y = random.randint(-VIRTUAL_HEIGHT, 0)
        self.speed = random.uniform(9, 14)
        self.length = random.randint(10, 18)

    def update(self):
        self.y += self.speed
        self.x -= self.speed * 0.3
        if self.y > VIRTUAL_HEIGHT:
            self.y = random.randint(-50, 0)
            self.x = random.randint(0, VIRTUAL_WIDTH)

    def draw(self, surface):
        pygame.draw.line(surface, (180, 200, 255), (self.x, self.y), (self.x - 4, self.y + self.length), 2)


class ParallaxTree:
    def __init__(self, x, layer):
        self.x = x
        self.layer = layer
        self.speed_factor = 0.4 if layer == 1 else 1.2
        self.color = JUNGLE_FAR if layer == 1 else JUNGLE_MID
        self.height = random.randint(140, 210) if layer == 1 else random.randint(100, 150)
        self.y = GROUND_Y - self.height

    def update(self, base_speed):
        self.x -= base_speed * 0.25 * self.speed_factor
        if self.x < -80:
            self.x = VIRTUAL_WIDTH + random.randint(10, 150)
            self.height = random.randint(140, 210) if self.layer == 1 else random.randint(100, 150)
            self.y = GROUND_Y - self.height

    def draw(self, surface):
        pygame.draw.rect(surface, (70, 40, 20), (self.x + 18, self.y + self.height - 40, 8, 40))
        pygame.draw.polygon(surface, self.color, [(self.x - 10, self.y + self.height - 30),
                                                    (self.x + 22, self.y),
                                                    (self.x + 54, self.y + self.height - 30)])


# ----------------- YORDAMCHI FUNKSIYALAR -----------------

def build_gradient_sky(top, bottom, height=370):
    surface = pygame.Surface((VIRTUAL_WIDTH, height))
    for y in range(height):
        t = y / float(height)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (VIRTUAL_WIDTH, y))
    return surface


def draw_ground(surface, offset):
    pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y, VIRTUAL_WIDTH, VIRTUAL_HEIGHT - GROUND_Y))
    pygame.draw.rect(surface, GREEN, (0, GROUND_Y, VIRTUAL_WIDTH, 10))
    step = 20
    shift = int(offset % step)
    for x in range(-step, VIRTUAL_WIDTH + step, step):
        px = x - shift
        pygame.draw.polygon(surface, (20, 100, 20), [(px, GROUND_Y), (px + 4, GROUND_Y - 8), (px + 8, GROUND_Y)])


def draw_heart(surface, x, y, size, filled):
    color = RED if filled else DARK_GRAY
    r = size // 2
    pygame.draw.circle(surface, color, (x - r // 2, y), r // 2 + 1)
    pygame.draw.circle(surface, color, (x + r // 2, y), r // 2 + 1)
    pygame.draw.polygon(surface, color, [(x - size // 2 - 1, y + 1), (x + size // 2 + 1, y + 1),
                                         (x, y + size // 2 + 2)])


def scale_touch_event(real_pos, real_w, real_h):
    scale_x = VIRTUAL_WIDTH / real_w
    scale_y = VIRTUAL_HEIGHT / real_h
    return int(real_pos[0] * scale_x), int(real_pos[1] * scale_y)


def spawn_burst(particles, x, y, color, count, mult=1.0):
    n = max(1, int(count * mult))
    for _ in range(n):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(1.5, 4.5)
        vx = math.cos(ang) * spd
        vy = math.sin(ang) * spd
        particles.append(Particle(x, y, vx, vy, color, random.randint(18, 32), size=4, gravity=0.15))


def spawn_dust(particles, x, y, mult=1.0):
    if random.random() > 0.6 * mult:
        return
    vx = random.uniform(-0.5, 0.2)
    vy = random.uniform(-0.6, -0.1)
    particles.append(Particle(x, y, vx, vy, (150, 120, 90), random.randint(14, 22), size=3, gravity=0.02))


def draw_text_center(surface, text, font, color, cx, cy):
    lbl = font.render(text, True, color)
    surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


def draw_button(surface, rect, text, font, bg_color, text_color):
    pygame.draw.rect(surface, bg_color, rect, border_radius=12)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=12)
    draw_text_center(surface, text, font, text_color, rect.centerx, rect.centery)


# ----------------- MAIN LOOP -----------------

def main():
    global REAL_WIDTH, REAL_HEIGHT, screen
    
    save_data = load_save()
    sound_mgr = SoundManager(save_data)
    sound_mgr.play_music()

    player_sprites = load_player_sprites()

    high_score = save_data.get("high_score", 0)
    total_coins = save_data.get("total_coins", 0)
    graphics_quality = save_data.get("graphics", "high")

    sky_day_surface = build_gradient_sky(SKY_TOP_DAY, SKY_BOTTOM_DAY)
    sky_night_surface = build_gradient_sky(SKY_TOP_NIGHT, SKY_BOTTOM_NIGHT)
    sky_night_surface.set_alpha(0)

    star_positions = [(random.randint(0, VIRTUAL_WIDTH), random.randint(10, 340)) for _ in range(40)]
    rain_drops = [RainDrop() for _ in range(40)]

    # Sensor tugmalari
    jump_btn_rect = pygame.Rect(40, 320, 140, 120)
    duck_btn_rect = pygame.Rect(VIRTUAL_WIDTH - 180, 320, 140, 120)
    pause_btn_rect = pygame.Rect(15, 15, 45, 45)

    # Menyu tugmalari
    start_btn_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 260, 220, 55)
    menu_settings_btn_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 330, 220, 55)

    resume_btn_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 170, 220, 50)
    restart_btn_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 235, 220, 50)
    pause_settings_btn_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 300, 220, 50)
    pause_menu_btn_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 365, 220, 50)

    sound_toggle_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 140, 220, 50)
    music_toggle_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 205, 220, 50)
    graphics_toggle_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 270, 220, 50)
    back_btn_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 350, 220, 50)

    gameover_restart_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, VIRTUAL_HEIGHT // 2 + 55, 220, 50)

    def reset_state():
        return {
            "player": Player(player_sprites),
            "obstacles": [],
            "coins": [],
            "balls": [],
            "powerups": [],
            "particles": [],
            "coin_count": 0,
            "lives": 3,
            "invuln_timer": 0,
            "shield_active": False,
            "shield_timer": 0,
            "speed_active": False,
            "speed_timer": 0,
            "base_speed": 8.6,
            "speed": 8.6,
            "score": 0,
            "level": 1,
            "spawn_timer": 0,
            "next_spawn": random.randint(70, 110),
            "coin_spawn_timer": 0,
            "ball_spawn_timer": 0,
            "powerup_spawn_timer": 0,
            "shake_timer": 0,
            "shake_mag": 0,
            "day_timer": random.randint(0, 900),
            "raining": False,
            "rain_toggle_timer": random.randint(400, 900),
            "level_msg_timer": 0,
        }

    game = reset_state()
    trees = [ParallaxTree(x, layer) for layer in (1, 0) for x in range(50, VIRTUAL_WIDTH + 100, 250)]

    state = "menu"
    prev_state = "menu"
    frame_count = 0

    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1
        quality = QUALITY_SETTINGS[graphics_quality]

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # --- EKRA ROTATSIYA (BURILISH) HODISASI ---
            elif event.type == pygame.VIDEORESIZE:
                new_w, new_h = event.size
                if new_w > 0 and new_h > 0:
                    REAL_WIDTH, REAL_HEIGHT = new_w, new_h
                    # Ekranni yangi o'lchamlarga muvofiq qayta ochamiz
                    screen = pygame.display.set_mode((REAL_WIDTH, REAL_HEIGHT), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "playing":
                        state = "paused"
                    elif state == "paused":
                        state = "playing"
                    else:
                        running = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if state == "playing":
                        game["player"].jump(sound_mgr)
                    elif state == "menu":
                        state = "playing"
                        game = reset_state()
                    elif state == "gameover":
                        state = "playing"
                        game = reset_state()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if state == "playing":
                        game["player"].duck(True)
                elif event.key == pygame.K_p:
                    if state == "playing":
                        state = "paused"
                    elif state == "paused":
                        state = "playing"

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    if state == "playing":
                        game["player"].duck(False)

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    raw_pos = event.pos
                else:
                    raw_pos = (event.x * REAL_WIDTH, event.y * REAL_HEIGHT)
                pos = scale_touch_event(raw_pos, REAL_WIDTH, REAL_HEIGHT)

                if state == "menu":
                    if start_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        state = "playing"
                        game = reset_state()
                    elif menu_settings_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        prev_state = "menu"
                        state = "settings"

                elif state == "playing":
                    if pause_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        state = "paused"
                    elif jump_btn_rect.collidepoint(pos):
                        game["player"].jump(sound_mgr)
                    elif duck_btn_rect.collidepoint(pos):
                        game["player"].duck(True)

                elif state == "paused":
                    if resume_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        state = "playing"
                    elif restart_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        game = reset_state()
                        state = "playing"
                    elif pause_settings_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        prev_state = "paused"
                        state = "settings"
                    elif pause_menu_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        state = "menu"

                elif state == "settings":
                    if sound_toggle_rect.collidepoint(pos):
                        sound_mgr.toggle_sound()
                        save_data["sound_on"] = sound_mgr.sound_on
                        write_save(save_data)
                        sound_mgr.play("button")
                    elif music_toggle_rect.collidepoint(pos):
                        sound_mgr.toggle_music()
                        save_data["music_on"] = sound_mgr.music_on
                        write_save(save_data)
                        sound_mgr.play("button")
                    elif graphics_toggle_rect.collidepoint(pos):
                        graphics_quality = "low" if graphics_quality == "high" else "high"
                        save_data["graphics"] = graphics_quality
                        write_save(save_data)
                        sound_mgr.play("button")
                    elif back_btn_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        state = prev_state

                elif state == "gameover":
                    if gameover_restart_rect.collidepoint(pos):
                        sound_mgr.play("button")
                        game = reset_state()
                        state = "playing"

            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                if event.type == pygame.MOUSEBUTTONUP:
                    raw_pos = event.pos
                else:
                    raw_pos = (event.x * REAL_WIDTH, event.y * REAL_HEIGHT)
                pos = scale_touch_event(raw_pos, REAL_WIDTH, REAL_HEIGHT)

                if state == "playing":
                    if duck_btn_rect.collidepoint(pos) or not pygame.mouse.get_pressed()[0]:
                        game["player"].duck(False)

        # ----------------- YANGILANISH TIZIMI -----------------
        if state == "playing":
            landed = game["player"].update()
            if landed:
                game["shake_timer"] = 6
                game["shake_mag"] = 4
            for tree in trees:
                tree.update(game["speed"])
            game["ground_offset"] = game.get("ground_offset", 0.0) + game["speed"]
            game["day_timer"] += 1

            game["rain_toggle_timer"] -= 1
            if game["rain_toggle_timer"] <= 0:
                if game["level"] >= 2:
                    game["raining"] = not game["raining"]
                else:
                    game["raining"] = False
                game["rain_toggle_timer"] = random.randint(500, 1000)

            game["spawn_timer"] += 1
            if game["spawn_timer"] >= game["next_spawn"]:
                game["obstacles"].append(Obstacle(game["speed"]))
                game["spawn_timer"] = 0
                game["next_spawn"] = random.randint(60, 100)

            for obs in game["obstacles"]:
                obs.update()
                if not obs.passed and obs.x + obs.width < game["player"].x:
                    obs.passed = True
                    game["score"] += 1
                    if game["score"] > high_score:
                        high_score = game["score"]
                    new_level = 1 + game["score"] // 10
                    if new_level > game["level"]:
                        game["level"] = new_level
                        game["base_speed"] += 1.1
                        game["level_msg_timer"] = 90
                        sound_mgr.play("levelup")

            if game["invuln_timer"] <= 0:
                for obs in game["obstacles"]:
                    if game["player"].rect.colliderect(obs.rect):
                        cx, cy = game["player"].x + game["player"].width // 2, game["player"].y + game["player"].height // 2
                        if game["shield_active"]:
                            game["shield_active"] = False
                            game["shield_timer"] = 0
                            spawn_burst(game["particles"], cx, cy, BLUE, 14, quality["particle_mult"])
                            sound_mgr.play("hit")
                            game["invuln_timer"] = 40
                            game["shake_timer"] = 8
                            game["shake_mag"] = 6
                        else:
                            game["lives"] -= 1
                            spawn_burst(game["particles"], cx, cy, RED, 16, quality["particle_mult"])
                            sound_mgr.play("hit")
                            game["invuln_timer"] = 90
                            game["shake_timer"] = 18
                            game["shake_mag"] = 10
                            if game["lives"] <= 0:
                                total_coins += game["coin_count"]
                                save_data["total_coins"] = total_coins
                                if game["score"] > save_data.get("high_score", 0):
                                    save_data["high_score"] = game["score"]
                                write_save(save_data)
                                state = "gameover"
                                break

            game["obstacles"] = [o for o in game["obstacles"] if o.x + o.width > 0]

            if game["invuln_timer"] > 0:
                game["invuln_timer"] -= 1

            # Tangalar
            game["coin_spawn_timer"] += 1
            if game["coin_spawn_timer"] > 55 and random.randint(1, 100) <= 3:
                game["coins"].append(Coin(game["speed"]))
                game["coin_spawn_timer"] = 0

            for coin in game["coins"]:
                coin.update()
                if game["player"].rect.colliderect(coin.rect):
                    game["coin_count"] += 1
                    coin.collected = True
                    spawn_burst(game["particles"], coin.x, coin.y, GOLD, 10, quality["particle_mult"])
                    sound_mgr.play("coin")

            game["coins"] = [c for c in game["coins"] if c.x > -50 and not c.collected]

            # Futbol to'plari
            game["ball_spawn_timer"] += 1
            if game["ball_spawn_timer"] > 300 and random.randint(1, 400) == 1:
                game["balls"].append(FootBall(game["speed"]))
                game["ball_spawn_timer"] = 0

            for ball in game["balls"]:
                ball.update()
                if game["player"].rect.colliderect(ball.rect):
                    ball.collected = True
                    game["score"] += 5
                    spawn_burst(game["particles"], ball.x, ball.y, WHITE, 10, quality["particle_mult"])
                    sound_mgr.play("ball")

            game["balls"] = [b for b in game["balls"] if b.x > -50 and not b.collected]

            # Bonuslar (PowerUps)
            game["powerup_spawn_timer"] += 1
            if game["powerup_spawn_timer"] > 500 and random.randint(1, 600) == 1:
                kind = random.choice(["shield", "speed"])
                game["powerups"].append(PowerUp(game["speed"], kind))
                game["powerup_spawn_timer"] = 0

            for p in game["powerups"]:
                p.update()
                if game["player"].rect.colliderect(p.rect):
                    p.collected = True
                    sound_mgr.play("powerup")
                    if p.kind == "shield":
                        game["shield_active"] = True
                        game["shield_timer"] = 350
                    elif p.kind == "speed":
                        game["speed_active"] = True
                        game["speed_timer"] = 300

            game["powerups"] = [p for p in game["powerups"] if p.x > -50 and not p.collected]

            if game["shield_active"]:
                game["shield_timer"] -= 1
                if game["shield_timer"] <= 0:
                    game["shield_active"] = False

            if game["speed_active"]:
                game["speed_timer"] -= 1
                game["speed"] = game["base_speed"] * 1.45
                if game["speed_timer"] <= 0:
                    game["speed_active"] = False
            else:
                game["speed"] = game["base_speed"]

            for pt in game["particles"]:
                pt.update()
            game["particles"] = [pt for pt in game["particles"] if pt.alive]

            if quality["dust"] and not game["player"].is_jumping and not game["player"].is_ducking:
                spawn_dust(game["particles"], game["player"].x + 8, GROUND_Y - 4, quality["particle_mult"])

        if game["raining"]:
            for r in rain_drops[:quality["rain_count"]]:
                r.update()

        # ----------------- CHIZISH TIZIMI -----------------
        day_t = (math.sin(game["day_timer"] * 0.001) + 1) * 0.5
        virtual_screen.blit(sky_day_surface, (0, 0))
        sky_night_surface.set_alpha(int((1 - day_t) * 255))
        virtual_screen.blit(sky_night_surface, (0, 0))

        if day_t < 0.5:
            star_alpha = int((1 - (day_t * 2)) * 255)
            star_alpha = max(0, min(255, star_alpha))
            for i, pos in enumerate(star_positions[:quality["stars"]]):
                if i % 3 == 0:
                    s_size = 3
                else:
                    s_size = 2
                temp = pygame.Surface((s_size * 2, s_size * 2), pygame.SRCALPHA)
                pulse = 150 + int(105 * math.sin((frame_count + i * 15) * 0.08))
                pygame.draw.circle(temp, (255, 255, 255, int(star_alpha * (pulse / 255))), (s_size, s_size), s_size)
                virtual_screen.blit(temp, (pos[0], pos[1]))

        if game["raining"]:
            for r in rain_drops[:quality["rain_count"] // 2]:
                r.draw(virtual_screen)

        for i, tree in enumerate(trees):
            if i % 2 == 0 and quality["trees_skip"] == 2:
                continue
            tree.draw(virtual_screen)

        draw_ground(virtual_screen, game.get("ground_offset", 0.0))

        if game["raining"]:
            for r in rain_drops[quality["rain_count"] // 2:quality["rain_count"]]:
                r.draw(virtual_screen)

        for obs in game["obstacles"]:
            obs.draw(virtual_screen)
        for coin in game["coins"]:
            coin.draw(virtual_screen)
        for ball in game["balls"]:
            ball.draw(virtual_screen)
        for p in game["powerups"]:
            p.draw(virtual_screen)
        for pt in game["particles"]:
            pt.draw(virtual_screen)

        game["player"].draw(virtual_screen, game["invuln_timer"] > 0, frame_count)

        if game["shield_active"]:
            px, py = game["player"].x + game["player"].width // 2, game["player"].y + game["player"].height // 2
            sh_r = max(game["player"].width, game["player"].height) // 2 + 10
            sh_surf = pygame.Surface((sh_r * 2, sh_r * 2), pygame.SRCALPHA)
            alpha_val = 90 + int(30 * math.sin(frame_count * 0.15))
            pygame.draw.circle(sh_surf, (70, 130, 220, alpha_val), (sh_r, sh_r), sh_r, 3)
            virtual_screen.blit(sh_surf, (px - sh_r, py - sh_r))

        if game["speed_active"]:
            for i in range(1, 4):
                sh_surf = pygame.Surface((game["player"].width, game["player"].height), pygame.SRCALPHA)
                alpha_val = max(0, 80 - i * 20)
                sh_surf.fill((255, 105, 180, alpha_val))
                virtual_screen.blit(sh_surf, (game["player"].x - i * 14, game["player"].y))

        # --- UI (Foydalanuvchi interfeysi) ---
        if state == "playing":
            score_lbl = font_medium.render(f"Ball: {game['score']}", True, WHITE)
            coin_lbl = font_medium.render(f"Tanga: {game['coin_count']}", True, GOLD)
            virtual_screen.blit(score_lbl, (15, 70))
            virtual_screen.blit(coin_lbl, (15, 105))

            for i in range(3):
                draw_heart(virtual_screen, 180 + i * 35, 83, 26, i < game["lives"])

            pygame.draw.rect(virtual_screen, (255, 255, 255, 30), jump_btn_rect, border_radius=12)
            pygame.draw.rect(virtual_screen, (255, 255, 255, 80), jump_btn_rect, 2, border_radius=12)
            draw_text_center(virtual_screen, "SAKRACH", font_medium, WHITE, jump_btn_rect.centerx, jump_btn_rect.centery)

            pygame.draw.rect(virtual_screen, (255, 255, 255, 30), duck_btn_rect, border_radius=12)
            pygame.draw.rect(virtual_screen, (255, 255, 255, 80), duck_btn_rect, 2, border_radius=12)
            draw_text_center(virtual_screen, "EGILISH", font_medium, WHITE, duck_btn_rect.centerx, duck_btn_rect.centery)

            pygame.draw.rect(virtual_screen, (60, 60, 60, 180), pause_btn_rect, border_radius=8)
            pygame.draw.rect(virtual_screen, WHITE, pause_btn_rect, 2, border_radius=8)
            draw_text_center(virtual_screen, "||", font_small, WHITE, pause_btn_rect.centerx, pause_btn_rect.centery)

            if game["level_msg_timer"] > 0:
                game["level_msg_timer"] -= 1
                level_lbl = font_large.render(f"LEVEL {game['level']}", True, YELLOW)
                virtual_screen.blit(level_lbl, (VIRTUAL_WIDTH // 2 - level_lbl.get_width() // 2, 110))

        elif state == "menu":
            virtual_screen.blit(sky_day_surface, (0, 0))
            draw_text_center(virtual_screen, "CR7 JUNGLE RUN", font_large, YELLOW, VIRTUAL_WIDTH // 2, 90)
            draw_text_center(virtual_screen, f"Rekord: {high_score}   Jami tanga: {total_coins}", font_medium, WHITE, VIRTUAL_WIDTH // 2, 160)

            draw_button(virtual_screen, start_btn_rect, "BOSHLASH", font_medium, GREEN, WHITE)
            draw_button(virtual_screen, menu_settings_btn_rect, "SOZLAMALAR", font_medium, BLUE, WHITE)

        elif state == "paused":
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            virtual_screen.blit(overlay, (0, 0))

            draw_text_center(virtual_screen, "O'YIN TO'XTATILDI", font_large, WHITE, VIRTUAL_WIDTH // 2, 100)

            draw_button(virtual_screen, resume_btn_rect, "DAVOM ETISH", font_medium, GREEN, WHITE)
            draw_button(virtual_screen, restart_btn_rect, "QAYTA BOSHLASH", font_medium, ORANGE, WHITE)
            draw_button(virtual_screen, pause_settings_btn_rect, "SOZLAMALAR", font_medium, BLUE, WHITE)
            draw_button(virtual_screen, pause_menu_btn_rect, "CHIQISH (MENU)", font_medium, RED, WHITE)

        elif state == "settings":
            virtual_screen.fill(DARK_GRAY)
            draw_text_center(virtual_screen, "SOZLAMALAR", font_large, WHITE, VIRTUAL_WIDTH // 2, 60)

            s_status = "YONIQ" if sound_mgr.sound_on else "O'CHIQ"
            m_status = "YONIQ" if sound_mgr.music_on else "O'CHIQ"
            g_status = "YUQORI" if graphics_quality == "high" else "PAST"

            draw_button(virtual_screen, sound_toggle_rect, f"OVOZ: {s_status}", font_medium, BLUE, WHITE)
            draw_button(virtual_screen, music_toggle_rect, f"MUSIQA: {m_status}", font_medium, BLUE, WHITE)
            draw_button(virtual_screen, graphics_toggle_rect, f"GRAFIKA: {g_status}", font_medium, BLUE, WHITE)
            draw_button(virtual_screen, back_btn_rect, "ORQAGA", font_medium, RED, WHITE)

        elif state == "gameover":
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            virtual_screen.blit(overlay, (0, 0))
            draw_text_center(virtual_screen, "O'YIN TUGADI", font_large, RED,
                              VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 70)
            draw_text_center(virtual_screen,
                              f"Ball: {game['score']}   Tanga: {game['coin_count']}   Rekord: {high_score}",
                              font_medium, WHITE, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 20)
            draw_button(virtual_screen, gameover_restart_rect, "QAYTA O'YNASH", font_medium, GREEN, WHITE)

        # ----------------- RE-SCALE VA SILKINISH EFFECTI -----------------
        scaled_surface = pygame.transform.smoothscale(virtual_screen, (REAL_WIDTH, REAL_HEIGHT))
        offset_x, offset_y = 0, 0
        if game["shake_mag"] > 0:
            offset_x = random.randint(-game["shake_mag"], game["shake_mag"])
            offset_y = random.randint(-game["shake_mag"], game["shake_mag"])
            game["shake_mag"] = max(0, game["shake_mag"] - 1)
        screen.fill(BLACK)
        screen.blit(scaled_surface, (offset_x, offset_y))

        pygame.display.flip()

    save_data["high_score"] = max(save_data.get("high_score", 0), high_score)
    save_data["total_coins"] = total_coins
    write_save(save_data)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
