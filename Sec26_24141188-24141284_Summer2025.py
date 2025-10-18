# SECTION - 26 | GROUP - 12

# FAHIM SHAHRIAR RAFI - 24141188
# KHANDAKER SHOUMIK MUJTAHEED - 24141284

#=================================================================
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

# =========================
# Game State Control
# =========================
GAME_STATE_MAIN_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_PAUSED = 3  
current_game_state = GAME_STATE_MAIN_MENU

# =========================
# Framerate Control
# =========================
FPS = 60
FRAME_DURATION_MS = int(1000 / FPS)

# =========================
# Main Menu Button Definitions
# =========================
start_button_rect = {'x': 250, 'y': 350, 'w': 200, 'h': 60}
close_button_rect = {'x': 550, 'y': 350, 'w': 200, 'h': 60}

# Pause Menu Buttons
pause_button_rect = {'x': 870, 'y': 720, 'w': 120, 'h': 50}  # Top-right corner during gameplay
resume_button_rect = {'x': 150, 'y': 350, 'w': 200, 'h': 60}
restart_button_rect = {'x': 400, 'y': 350, 'w': 200, 'h': 60}
exit_pause_button_rect = {'x': 650, 'y': 350, 'w': 200, 'h': 60}

# Pause timing variables
pause_start_time = 0
total_paused_duration = 0

# =========================
# Original game state
# =========================
player_lane = 0
player_z = 0
player_speed = 0.5
speed_increase_factor = 0.00001
lane_width = 100
lane_positions = [lane_width, 0, -lane_width]

# =========================
# Health System
# =========================
player_health = 10
max_health = 10

# Player state variables
player_y = 0
is_jumping = False
is_sliding = False
jump_start_time = 0
slide_start_time = 0
jump_duration = 0.5
slide_duration = 0.5
jump_height = 60


# Player head flash 
green_flash_end_time = 0
red_flash_end_time = 0
FLASH_DURATION = 0.3  # Flash duration in seconds

# Animation variables
animation_time = 0
running_animation_speed = 8.0

# Camera variables
camera_distance = 200
camera_height = 150
fovY = 90

# Track variables
track_segment_length = 100
track_segments = []
max_track_segments = 20

# =========================
# Obstacles + spawn delay + damage tracking 
# =========================
obstacles = []
OBSTACLE_GROUND = 0
OBSTACLE_AIR = 1
obstacle_spawn_distance = 280

# Track which obstacles have already damaged the player
damaged_obstacles = set()  # Stores (obstacle_type, lane, z_pos) tuples

# Obstacle spawn delay
OBSTACLE_SPAWN_DELAY = 5.0
game_start_time = time.time()

# =========================
# Environment, Coins, Power-ups, Score, Day/Night
# =========================
# Environment
environment_elements = []
last_env_generate_z = 0
ENV_X_MIN, ENV_X_MAX = 150, 400

# Power-ups
power_ups = []
last_power_up_spawn_time = 0
POWER_UP_SPAWN_INTERVAL = 10.0
POWER_UP_SPAWN_CHANCE = 0.1
POWER_UP_DURATION = 5.0
is_speed_boost_active = False
speed_boost_end_time = 0
is_shield_active = False
shield_end_time = 0
is_magnet_active = False
magnet_end_time = 0
lives = 1

# Score and coins
score = 0
coins = []
coin_animation_start = time.time()

# Day/Night
DAY_NIGHT_DURATION = 10.0
cycle_start_time = time.time()
DAY_COLOR = [0.53, 0.81, 0.98]
NIGHT_COLOR = [0.05, 0.05, 0.15]

def draw_button(rect, button_text, bg_color):
    """A helper function to draw a button with centered text."""
    glColor3f(bg_color[0], bg_color[1], bg_color[2])
    glBegin(GL_QUADS)
    glVertex2f(rect['x'], rect['y'])
    glVertex2f(rect['x'] + rect['w'], rect['y'])
    glVertex2f(rect['x'] + rect['w'], rect['y'] + rect['h'])
    glVertex2f(rect['x'], rect['y'] + rect['h'])
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    text_width = len(button_text) * 9
    text_x = rect['x'] + (rect['w'] - text_width) / 2
    text_y = rect['y'] + (rect['h'] / 2) - 6
    glRasterPos2f(text_x, text_y)
    for char in button_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_main_menu():
    """Draws the main menu screen, correctly handling the depth test."""
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1.0, 1.0, 1.0)
    title_text = "Main Menu"
    title_width = len(title_text) * 9
    title_x = (1000 - title_width) / 2
    glRasterPos2f(title_x, 600)
    for char in title_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    draw_button(start_button_rect, "Start", (0.2, 0.6, 0.2))
    draw_button(close_button_rect, "Exit", (0.8, 0.2, 0.2))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_game_over():
    """Draws the game over screen with red text on black background."""
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1.0, 0.0, 0.0)
    game_over_text = "GAME OVER"
    text_width = len(game_over_text) * 18
    text_x = (1000 - text_width) / 2
    glRasterPos2f(text_x, 450)
    for char in game_over_text:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    
    glColor3f(1.0, 0.0, 0.0)
    score_text = f"Final Score: {score}"
    score_width = len(score_text) * 9
    score_x = (1000 - score_width) / 2
    glRasterPos2f(score_x, 350)
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glColor3f(0.8, 0.8, 0.8)
    restart_text = "Press R to restart or ESC button to exit"
    restart_width = len(restart_text) * 9
    restart_x = (1000 - restart_width) / 2
    glRasterPos2f(restart_x, 250)
    for char in restart_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

# Pause menu function
def draw_pause_menu():
    """Draws the semi-transparent overlay and the pause menu buttons."""
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw the semi-transparent background overlay
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.7)  # Black with 70% opacity
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    glDisable(GL_BLEND)
    
    # Draw "PAUSED" title
    glColor3f(1.0, 1.0, 1.0)
    paused_text = "PAUSED"
    paused_width = len(paused_text) * 18
    paused_x = (1000 - paused_width) / 2
    glRasterPos2f(paused_x, 500)
    for char in paused_text:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    
    # Draw the menu buttons on top of the overlay
    draw_button(resume_button_rect, "Resume", (0.2, 0.6, 0.2))    # Green
    draw_button(restart_button_rect, "Restart", (0.2, 0.2, 0.8))  # Blue
    draw_button(exit_pause_button_rect, "Exit", (0.8, 0.2, 0.2))  # Red
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def start_game():
    """Resets all game variables and switches the state to playing."""
    # Declare all globals being modified
    global current_game_state, player_z, player_y, player_lane, player_speed, score, lives
    global is_jumping, is_sliding, obstacles, coins, power_ups, reserved_slots, cycle_start_time
    global player_health, game_start_time, damaged_obstacles, pause_start_time, total_paused_duration
    global green_flash_end_time, red_flash_end_time

    # Switch state
    current_game_state = GAME_STATE_PLAYING
    
    # --- THIS IS THE FIX ---
    player_lane = 0 # Always start in the center lane
    
    # Reset all other relevant variables
    player_z = 0
    player_y = 0
    player_speed = 5.0
    score = 0
    lives = 1
    player_health = max_health
    is_jumping = False
    is_sliding = False
    
    obstacles.clear()
    coins.clear()
    power_ups.clear()
    reserved_slots.clear()
    damaged_obstacles.clear()
    
    init_track()
    
    # Reset all timers
    current_time = time.time()
    cycle_start_time = current_time
    game_start_time = current_time
    pause_start_time = 0
    total_paused_duration = 0
    green_flash_end_time = 0
    red_flash_end_time = 0



# =========================
# Rule 1: Shared spawn-slot deconfliction
# =========================
BIN_Z = 40
reserved_slots = set()

def _slot_key(lane, z):
    return (lane, int(z // BIN_Z))

def _slot_free(lane, z):
    return _slot_key(lane, z) not in reserved_slots

def _reserve(lane, z):
    reserved_slots.add(_slot_key(lane, z))

def _cleanup_reservations():
    back_bin = int((player_z - 200) // BIN_Z)
    stale = [k for k in reserved_slots if k[1] < back_bin]
    for k in stale:
        reserved_slots.discard(k)

# =========================
# Original init and track
# =========================
def init_track():
    global track_segments
    track_segments = []
    for i in range(max_track_segments):
        track_segments.append(i * track_segment_length)

# =========================
# Obstacle spawner (with spawn delay)
# =========================
def spawn_obstacles():
    """Spawn obstacles randomly on the track (with 5 second delay)."""
    global obstacles
    
    if time.time() - game_start_time < OBSTACLE_SPAWN_DELAY:
        return
    
    obstacles = [obs for obs in obstacles if obs[2] > player_z - 200]
    if not obstacles or max(obs[2] for obs in obstacles) < player_z + 800:
        obstacle_lane = random.randint(-1, 1)
        obstacle_type = random.choice([OBSTACLE_GROUND, OBSTACLE_AIR])
        obstacle_z = (max(obs[2] for obs in obstacles) + obstacle_spawn_distance) if obstacles else player_z + 300
        if _slot_free(obstacle_lane, obstacle_z):
            obstacles.append((obstacle_type, obstacle_lane, obstacle_z))
            _reserve(obstacle_lane, obstacle_z)

def draw_obstacles():
    """Draw all obstacles (unmodified)."""
    for obstacle_type, lane, z_pos in obstacles:
        if abs(z_pos - player_z) < 500:
            lane_x = lane_positions[lane + 1]
            if obstacle_type == OBSTACLE_GROUND:
                glPushMatrix()
                glTranslatef(lane_x, -20, z_pos)
                glColor3f(1.0, 0.2, 0.2)
                glutSolidCube(40)
                glPopMatrix()
            elif obstacle_type == OBSTACLE_AIR:
                glPushMatrix()
                glTranslatef(lane_x, 40, z_pos)
                glColor3f(0.2, 0.2, 1.0)
                glScalef(2.0, 0.5, 1.0)
                glutSolidCube(40)
                glPopMatrix()

# =========================
# Player state (jump/slide)
# =========================
def update_player_state():
    global player_y, is_jumping, is_sliding
    current_time = time.time()
    if is_jumping:
        elapsed = current_time - jump_start_time
        if elapsed < jump_duration:
            progress = elapsed / jump_duration
            player_y = jump_height * (1 - (2 * progress - 1) ** 2)
        else:
            is_jumping = False
            player_y = 0
    if is_sliding:
        elapsed = current_time - slide_start_time
        if elapsed >= slide_duration:
            is_sliding = False

# =========================
# FIXED: Collision detection with proper damage tracking and shield protection
# =========================
def check_collisions():
    """FIXED: Collision detection that only damages once per obstacle and respects shield AND speed boost."""
    global player_health, current_game_state, damaged_obstacles, red_flash_end_time
    
    player_lane_x = lane_positions[player_lane + 1]
    collision_occurred = False
    
    for obstacle_type, lane, z_pos in obstacles:
        lane_x = lane_positions[lane + 1]
        obstacle_key = (obstacle_type, lane, z_pos)  # Unique identifier for this obstacle
        
        # Check if player is colliding with this obstacle
        if (abs(player_lane_x - lane_x) < 30 and abs(player_z - z_pos) < 40):
            # Check if this obstacle should cause damage
            should_damage = False
            
            if obstacle_type == OBSTACLE_GROUND and not is_jumping:
                should_damage = True
            elif obstacle_type == OBSTACLE_AIR and not is_sliding:
                should_damage = True
            
            if should_damage:
                collision_occurred = True
                
                # FIXED: Only damage if this obstacle hasn't damaged before
                if obstacle_key not in damaged_obstacles:
                    # FIXED: Both shield AND speed boost prevent damage
                    if not is_shield_active and not is_speed_boost_active:
                        player_health -= 1
                        red_flash_end_time = time.time() + FLASH_DURATION
                        if player_health <= 0:
                            current_game_state = GAME_STATE_GAME_OVER
                    
                    # Mark this obstacle as having caused damage
                    damaged_obstacles.add(obstacle_key)
    
    return collision_occurred


def cleanup_damaged_obstacles():
    """FIXED: Clean up damage tracking for obstacles that are no longer relevant."""
    global damaged_obstacles
    
    # Remove damage records for obstacles that are far behind the player
    obstacles_to_remove = set()
    for obstacle_key in damaged_obstacles:
        obstacle_type, lane, z_pos = obstacle_key
        if z_pos < player_z - 100:  # Remove if obstacle is far behind
            obstacles_to_remove.add(obstacle_key)
    
    for obstacle_key in obstacles_to_remove:
        damaged_obstacles.discard(obstacle_key)

# =========================
# Character and track render (unchanged)
# =========================
def draw_character():
    glPushMatrix()
    current_x = lane_positions[player_lane + 1]
    glTranslatef(current_x, player_y, player_z)
    if is_sliding:
        glRotatef(90, 1, 0, 0)
    arm_swing = math.sin(animation_time * running_animation_speed) * 30
    leg_swing = math.sin(animation_time * running_animation_speed) * 20
    
    # Head (sphere above torso) - NOW WITH FLASHING
    glPushMatrix()
    glTranslatef(0, 35, 0)
    
    # Check for active flash effects
    current_time = time.time()
    if current_time < green_flash_end_time:
        # Green flash for coin collection
        glColor3f(0.2, 1.0, 0.2)  
    elif current_time < red_flash_end_time:
        # Red flash for damage
        glColor3f(1.0, 0.2, 0.2)  
    else:
        # Normal head color
        glColor3f(0.8, 0.6, 0.4)  
    
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.2, 0.4, 0.8)
    glutSolidCube(30)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-25, 10, 0)
    glRotatef(arm_swing, 1, 0, 0)
    glTranslatef(0, -15, 0)
    glColor3f(0.8, 0.6, 0.4)
    glScalef(0.3, 1.0, 0.3)
    glutSolidCube(30)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(25, 10, 0)
    glRotatef(-arm_swing, 1, 0, 0)
    glTranslatef(0, -15, 0)
    glColor3f(0.8, 0.6, 0.4)
    glScalef(0.3, 1.0, 0.3)
    glutSolidCube(30)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-10, -15, 0)
    glRotatef(leg_swing, 1, 0, 0)
    glTranslatef(0, -20, 0)
    glColor3f(0.1, 0.1, 0.6)
    glScalef(0.4, 1.5, 0.4)
    glutSolidCube(30)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(10, -15, 0)
    glRotatef(-leg_swing, 1, 0, 0)
    glTranslatef(0, -20, 0)
    glColor3f(0.1, 0.1, 0.6)
    glScalef(0.4, 1.5, 0.4)
    glutSolidCube(30)
    glPopMatrix()
    glPopMatrix()


def draw_track():
    box_size = 20
    for segment_z in track_segments:
        if abs(segment_z - player_z) < 500:
            for lane in range(3):
                lane_x = lane_positions[lane]
                boxes_per_segment = int(track_segment_length / box_size)
                for box_i in range(boxes_per_segment):
                    box_z = segment_z + (box_i * box_size)
                    if (lane + box_i) % 2 == 0:
                        glColor3f(0.7, 0.7, 0.7)
                    else:
                        glColor3f(0.3, 0.3, 0.3)
                    glPushMatrix()
                    glTranslatef(lane_x, -40, box_z)
                    glScalef(3.0, 0.2, 1.0)
                    glutSolidCube(box_size)
                    glPopMatrix()
    glColor3f(1.0, 0.0, 0.0)
    for segment_z in track_segments:
        if abs(segment_z - player_z) < 500:
            glPushMatrix()
            glTranslatef(50, -35, segment_z)
            glScalef(0.1, 0.1, 5.0)
            glutSolidCube(20)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(-50, -35, segment_z)
            glScalef(0.1, 0.1, 5.0)
            glutSolidCube(20)
            glPopMatrix()

def draw_ground():
    """Draw dark brown ground on both sides of the track."""
    ground_y = -45
    ground_color = (0.3, 0.2, 0.1)  
    
    # Ground extends based on visible track segments
    for segment_z in track_segments:
        if abs(segment_z - player_z) < 500:  
            
            # Left side ground 
            glColor3f(ground_color[0], ground_color[1], ground_color[2])
            glPushMatrix()
            
            glTranslatef(-250, ground_y, segment_z)
            glScalef(15.0, 0.1, 5.0)  # Wide (300 units)
            glutSolidCube(20)
            glPopMatrix()
            
            # Right side ground 
            glColor3f(ground_color[0], ground_color[1], ground_color[2])
            glPushMatrix()
            
            glTranslatef(250, ground_y, segment_z)
            glScalef(15.0, 0.1, 5.0)  # Wide (300 units)
            glutSolidCube(20)
            glPopMatrix()


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    current_x = lane_positions[player_lane + 1]
    camera_x = current_x
    camera_y = camera_height
    camera_z = player_z - camera_distance
    target_x = current_x
    target_y = player_y
    target_z = player_z
    gluLookAt(camera_x, camera_y, camera_z, target_x, target_y, target_z, 0, 1, 0)

# =========================
# Environment drawing 
# =========================
def draw_tree(position):
    """Draws a larger low-poly tree at a given position with leaves pointing upward."""
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glColor3f(0.5, 0.35, 0.05)  
    glPushMatrix()
    glTranslatef(0, 25, 0)
    glScalef(0.5, 5.0, 0.5)
    glutSolidCube(10)
    glPopMatrix()
    glColor3f(0.0, 0.5, 0.0) 
    glPushMatrix()
    glTranslatef(0, 60, 0)  
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(30, 60, 10, 5)
    glPopMatrix()
    glPopMatrix()

def draw_broken_statue(position):
    glPushMatrix()
    glTranslatef(position[0], position[1] - 10, position[2])
    glRotatef(random.uniform(-15, 15), 0, 1, 0)
    glColor3f(0.4, 0.5, 0.4)
    glPushMatrix()
    glScalef(1.5, 2.5, 1.0)
    glutSolidCube(20)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(10, -10, 5)
    glRotatef(25, 1, 0, 0)
    glScalef(1.0, 1.5, 0.8)
    glutSolidCube(15)
    glPopMatrix()
    glPopMatrix()

def draw_rock_formation(position):
    glPushMatrix()
    glTranslatef(position[0], position[1] - 5, position[2])
    glRotatef(random.uniform(-25, 25), 0, 1, 0)
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glScalef(2.0, 3.0, 1.5)
    glutSolidCube(20)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(15, -10, 8)
    glRotatef(30, 1, 0, 0)
    glScalef(1.0, 1.8, 1.2)
    glutSolidCube(15)
    glPopMatrix()
    glPopMatrix()

def manage_environment_elements():
    global environment_elements, last_env_generate_z
    if player_z > last_env_generate_z:
        last_env_generate_z += 50
        element_type = None
        if 0 <= score < 200:
            element_type = 'tree'
        elif 200 <= score < 500:
            element_type = 'statue'
        elif score >= 500:
            element_type = 'rock'
        if element_type and random.random() < 0.5:
            side = random.choice([-1, 1])
            pos_x = side * random.uniform(ENV_X_MIN, ENV_X_MAX)
            pos_z = player_z + 1200 + random.uniform(0, 200)
            environment_elements.append({'type': element_type, 'pos': [pos_x, 0, pos_z]})
    environment_elements[:] = [elem for elem in environment_elements if elem['pos'][2] > player_z - camera_distance]

def draw_environment():
    for element in environment_elements:
        if element['type'] == 'tree':
            draw_tree(element['pos'])
        elif element['type'] == 'statue':
            draw_broken_statue(element['pos'])
        elif element['type'] == 'rock':
            draw_rock_formation(element['pos'])

# =========================
# Coins and power-ups 
# =========================
def draw_coin(coin_data):
    glPushMatrix()
    x, y, z = coin_data['pos']
    glTranslatef(x, y, z)
    current_time = time.time()
    elapsed = (current_time - coin_animation_start) * 2.0
    scale = 1.3 + 0.2 * math.sin(2 * math.pi * elapsed)
    glScalef(scale, scale, scale)
    coin_type = coin_data['type']
    if coin_type == 'yellow':
        glColor3f(1.0, 1.0, 0.0)
    elif coin_type == 'green':
        glColor3f(0.1, 1.0, 0.1)
    elif coin_type == 'purple':
        glColor3f(0.8, 0.4, 1.0)
    glutSolidTorus(5, 12, 10, 20)
    glPopMatrix()

def draw_power_up_icon(power_up_data):
    glPushMatrix()
    x, y, z = power_up_data['pos']
    glTranslatef(x, y + 20, z)
    current_time = time.time()
    scale = 1.0 + 0.2 * math.sin(current_time * 5)
    glScalef(scale, scale, scale)
    power_up_type = power_up_data['type']
    icon_text = ''
    if power_up_type == 'speed_boost':
        glColor3f(1.0, 0.5, 0.0)
        icon_text = '>>'
    elif power_up_type == 'extra_life':
        glColor3f(0.0, 1.0, 0.0)
        icon_text = '+'
    elif power_up_type == 'shield':
        glColor3f(0.2, 0.8, 1.0)
        icon_text = '{ }'
    elif power_up_type == 'magnet':
        glColor3f(1.0, 0.0, 1.0)
        icon_text = 'U'
    glRasterPos2f(-10, 0)
    for char in icon_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glPopMatrix()

def draw_active_power_up_effects():
    player_x = lane_positions[player_lane + 1]
    if is_shield_active:
        glPushMatrix()
        glTranslatef(player_x, 40, player_z)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.2, 0.8, 1.0, 0.3)
        glutSolidSphere(60, 20, 20)
        glDisable(GL_BLEND)
        glPopMatrix()
    if is_magnet_active:
        glPushMatrix()
        glTranslatef(player_x, 40, player_z)
        glColor3f(1.0, 0.0, 1.0)
        glRasterPos2f(-50, 0)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('['))
        glRasterPos2f(40, 0)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(']'))
        glPopMatrix()

def manage_coins():
    """Unchanged logic except: aerial coin height uses jump height; and slot reservation."""
    global coins, score
    last_segment_z = max(track_segments) if track_segments else 0
    spawn_z = last_segment_z + 100
    spawn_chances = {'yellow': 0.005, 'green': 0.002, 'purple': 0.0005}
    for coin_type, chance in spawn_chances.items():
        if random.random() < chance:
            pos_y = (40 + jump_height) if random.random() < 0.3 else 10
            lane = random.choice([-1, 0, 1])
            lane_x = lane_positions[lane + 1]
            if _slot_free(lane, spawn_z):
                coins.append({
                    'pos': [lane_x, pos_y, spawn_z],
                    'type': coin_type,
                    'value': {'yellow': 1, 'green': 2, 'purple': 3}[coin_type]
                })
                _reserve(lane, spawn_z)

def manage_power_ups():
    """Unchanged logic except: slot reservation to avoid overlaps."""
    global power_ups, last_power_up_spawn_time
    current_time = time.time()
    time_since_last_spawn = current_time - last_power_up_spawn_time
    if time_since_last_spawn > POWER_UP_SPAWN_INTERVAL and random.random() < POWER_UP_SPAWN_CHANCE:
        power_up_type = random.choice(['speed_boost', 'extra_life', 'shield', 'magnet'])
        lane = random.choice([-1, 0, 1])
        lane_x = lane_positions[lane + 1]
        spawn_z = (max(track_segments) if track_segments else 0) + 100
        if _slot_free(lane, spawn_z):
            power_ups.append({'type': power_up_type, 'pos': [lane_x, 10, spawn_z]})
            _reserve(lane, spawn_z)
            last_power_up_spawn_time = current_time

def manage_collisions_and_effects():
    """Original logic, with health gain from extra_life power-ups and pause-aware timing."""
    global coins, power_ups, score, lives, player_health
    global player_speed, is_speed_boost_active, speed_boost_end_time
    global is_shield_active, shield_end_time, is_magnet_active, magnet_end_time
    
    # Pause-adjusted time for all calculations
    current_time = time.time() - total_paused_duration
    player_x = lane_positions[player_lane + 1]

    # Power-up collection
    for p_up in power_ups[:]:
        if abs(player_x - p_up['pos'][0]) < 20 and abs(player_z - p_up['pos'][2]) < 20:
            p_type = p_up['type']
            if p_type == 'speed_boost':
                if not is_speed_boost_active:
                    player_speed *= 1.5
                is_speed_boost_active = True
                speed_boost_end_time = current_time + POWER_UP_DURATION
            elif p_type == 'extra_life':
                lives += 1
                player_health = min(max_health, player_health + 1)
            elif p_type == 'shield':
                is_shield_active = True
                shield_end_time = current_time + POWER_UP_DURATION
            elif p_type == 'magnet':
                is_magnet_active = True
                magnet_end_time = current_time + POWER_UP_DURATION
            power_ups.remove(p_up)

    # Magnet effect
    if is_magnet_active:
        for coin in coins:
            if abs(player_z - coin['pos'][2]) < 150:
                coin['pos'][0] += (player_x - coin['pos'][0]) * 0.1
                coin['pos'][1] += (40 - coin['pos'][1]) * 0.1

    # Coin collection
    for coin in coins[:]:
        if (abs(player_x - coin['pos'][0]) < 20 and
            abs(player_z - coin['pos'][2]) < 20 and
            abs((40 + player_y) - coin['pos'][1]) < 50):
            score += coin['value']
            global green_flash_end_time
            green_flash_end_time = current_time + FLASH_DURATION
            coins.remove(coin)


    # Power-up deactivation
    if is_speed_boost_active and current_time > speed_boost_end_time:
        is_speed_boost_active = False
        player_speed /= 1.5
    if is_shield_active and current_time > shield_end_time:
        is_shield_active = False
    if is_magnet_active and current_time > magnet_end_time:
        is_magnet_active = False

    # Cleanup
    coins[:] = [c for c in coins if c['pos'][2] > player_z - 50]
    power_ups[:] = [p for p in power_ups if p['pos'][2] > player_z - 50]

# Day/night system with pause awareness
def update_and_apply_sky_color():
    """Calculates and applies day/night sky color transition, correctly handling pauses."""
    effective_elapsed_time = 0
    
    if current_game_state == GAME_STATE_PAUSED:
        effective_elapsed_time = (pause_start_time - cycle_start_time) - total_paused_duration
    else:
        effective_elapsed_time = (time.time() - cycle_start_time) - total_paused_duration
    
    total_cycle_time = DAY_NIGHT_DURATION * 2
    cycle_progress = (effective_elapsed_time % total_cycle_time) / total_cycle_time
    t = (math.cos(cycle_progress * 2 * math.pi) + 1) / 2.0
    current_color = [DAY_COLOR[i] * t + NIGHT_COLOR[i] * (1 - t) for i in range(3)]
    glClearColor(current_color[0], current_color[1], current_color[2], 1.0)


# =========================
def update_game():
    global player_z, player_speed, animation_time, track_segments
    animation_time = time.time()
    update_player_state()
    player_z += player_speed
    player_speed += speed_increase_factor
    while len(track_segments) < max_track_segments:
        last_segment = max(track_segments) if track_segments else 0
        track_segments.append(last_segment + track_segment_length)
    track_segments[:] = [seg for seg in track_segments if seg > player_z - 300]
    while max(track_segments) < player_z + 1000:
        track_segments.append(max(track_segments) + track_segment_length)
    spawn_obstacles()
    manage_environment_elements()
    manage_coins()
    manage_power_ups()
    manage_collisions_and_effects()
    check_collisions()  
    cleanup_damaged_obstacles()  
    _cleanup_reservations()

def timer_func(value):
    """Fixed 60 FPS timer callback"""
    if current_game_state == GAME_STATE_PLAYING:
        update_game()
    glutPostRedisplay()
    glutTimerFunc(FRAME_DURATION_MS, timer_func, 0)

def keyboardListener(key, x, y):
    """Handles all keyboard inputs."""
    global player_lane, is_jumping, is_sliding, jump_start_time, slide_start_time, current_game_state
    if key == 27 or key == b'\x1b':
        glutLeaveMainLoop()
        return 

   # Active game controls
    if current_game_state == GAME_STATE_PLAYING:
        if key == b'a' or key == b'A':
            if player_lane > -1:
                player_lane -= 1
        elif key == b'd' or key == b'D':
            if player_lane < 1:
                player_lane += 1
        elif key == b'w' or key == b'W':
            if not is_jumping and not is_sliding:
                is_jumping = True
                jump_start_time = time.time()
        elif key == b's' or key == b'S':
            if not is_sliding and not is_jumping:
                is_sliding = True
                slide_start_time = time.time()

    # Game over control
    elif current_game_state == GAME_STATE_GAME_OVER:
        if key == b'r' or key == b'R':
            start_game()


def specialKeyListener(key, x, y): pass


def mouseListener(button, state, x, y):
    """Handles mouse inputs, including pause menu interactions."""
    global current_game_state, pause_start_time, total_paused_duration
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        mouse_y = 800 - y
        
        # Main Menu
        if current_game_state == GAME_STATE_MAIN_MENU:
            if (start_button_rect['x'] <= x <= start_button_rect['x'] + start_button_rect['w'] and
                start_button_rect['y'] <= mouse_y <= start_button_rect['y'] + start_button_rect['h']):
                start_game()
            elif (close_button_rect['x'] <= x <= close_button_rect['x'] + close_button_rect['w'] and
                  close_button_rect['y'] <= mouse_y <= close_button_rect['y'] + close_button_rect['h']):
                glutLeaveMainLoop()
        
        # Playing 
        elif current_game_state == GAME_STATE_PLAYING:
            if (pause_button_rect['x'] <= x <= pause_button_rect['x'] + pause_button_rect['w'] and
                pause_button_rect['y'] <= mouse_y <= pause_button_rect['y'] + pause_button_rect['h']):
                pause_start_time = time.time()
                current_game_state = GAME_STATE_PAUSED
        
        # Paused 
        elif current_game_state == GAME_STATE_PAUSED:
            # Resume Button
            if (resume_button_rect['x'] <= x <= resume_button_rect['x'] + resume_button_rect['w'] and
                resume_button_rect['y'] <= mouse_y <= resume_button_rect['y'] + resume_button_rect['h']):
                if pause_start_time > 0:
                    total_paused_duration += time.time() - pause_start_time
                current_game_state = GAME_STATE_PLAYING
            # Restart Button
            elif (restart_button_rect['x'] <= x <= restart_button_rect['x'] + restart_button_rect['w'] and
                  restart_button_rect['y'] <= mouse_y <= restart_button_rect['y'] + restart_button_rect['h']):
                start_game()
            # Exit Button
            elif (exit_pause_button_rect['x'] <= x <= exit_pause_button_rect['x'] + exit_pause_button_rect['w'] and
                  exit_pause_button_rect['y'] <= mouse_y <= exit_pause_button_rect['y'] + exit_pause_button_rect['h']):
                glutLeaveMainLoop()

def showScreen():
    """Main display function that directs to menu, game, paused, or game over rendering."""
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if current_game_state == GAME_STATE_MAIN_MENU:
        draw_main_menu()
    
    elif current_game_state == GAME_STATE_GAME_OVER:
        draw_game_over()

    elif current_game_state == GAME_STATE_PLAYING or current_game_state == GAME_STATE_PAUSED:
        update_and_apply_sky_color()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, 1000, 800)
        setup_camera()
        draw_track()
        draw_ground()  
        draw_environment()
        for coin in coins: draw_coin(coin)
        for p_up in power_ups: draw_power_up_icon(p_up)
        draw_obstacles()
        draw_character()
        draw_active_power_up_effects()
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1, 1, 1)
        glRasterPos2f(10, 770)
        info_text = f"Score: {score} | Health: {player_health}/{max_health} | Speed: {player_speed:.1f}"
        for ch in info_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        time_elapsed = (time.time() - game_start_time) - total_paused_duration
        if time_elapsed < OBSTACLE_SPAWN_DELAY:
            remaining = OBSTACLE_SPAWN_DELAY - time_elapsed
            glRasterPos2f(10, 740)
            countdown_text = f"Obstacles start in: {remaining:.1f}s"
            for ch in countdown_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        draw_button(pause_button_rect, "Pause", (0.5, 0.2, 0.8))

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        if current_game_state == GAME_STATE_PAUSED:
            draw_pause_menu()

    glutSwapBuffers()


def main():
    init_track()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Temple Run - Health System + Pause Menu")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutTimerFunc(FRAME_DURATION_MS, timer_func, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
