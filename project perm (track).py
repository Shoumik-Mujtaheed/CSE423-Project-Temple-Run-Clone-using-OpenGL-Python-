from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random



# =========================
# NEW: Track Segment Class
# =========================
class TrackSegment:
    def __init__(self, start_pos, direction, length=200):
        self.start = start_pos
        self.direction = direction # A vector like (0, 0, 1) for forward
        self.length = length
        # The "right" vector is always perpendicular to the direction
        self.right_vec = (direction[2], direction[1], -direction[0])
        self.end = (
            start_pos[0] + direction[0] * length,
            start_pos[1],
            start_pos[2] + direction[2] * length
        )





# =========================
# Game State Control
# =========================
GAME_STATE_MAIN_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_PAUSED = 2
current_game_state = GAME_STATE_MAIN_MENU


# =========================
# Main Menu Button Definitions
# =========================
start_button_rect = {'x': 250, 'y': 350, 'w': 200, 'h': 60}
close_button_rect = {'x': 550, 'y': 350, 'w': 200, 'h': 60}

# --- NEW: Pause Menu Buttons ---
# The button to activate the pause menu (visible during gameplay)
pause_button_rect = {'x': 870, 'y': 730, 'w': 120, 'h': 50} # Top-right corner

# The buttons inside the pause menu overlay
resume_button_rect = {'x': 150, 'y': 350, 'w': 200, 'h': 60}
restart_button_rect = {'x': 400, 'y': 350, 'w': 200, 'h': 60}
exit_pause_button_rect = {'x': 650, 'y': 350, 'w': 200, 'h': 60}


# --- NEW: Pause timing variables ---
pause_start_time = 0
total_paused_duration = 0





# =========================
# Original game state (from your file)
# =========================
player_lane = 0  # -1 = left, 0 = center, 1 = right
player_z = 0     # Player's forward position
player_speed = 5  # Base running speed
speed_increase_factor = 0.001  # Speed increases over time
lane_width = 100  # Distance between lanes
lane_positions = [lane_width, 0, -lane_width]  # Left, center, right lane X positions

# Player state variables
player_y = 0  # Player's height (for jumping)
is_jumping = False
is_sliding = False
jump_start_time = 0
slide_start_time = 0
jump_duration = 0.5
slide_duration = 0.3
jump_height = 60  # Maximum jump height

# Animation variables
animation_time = 0
running_animation_speed = 8.0  # Controls arm/leg swing speed

# Camera variables
camera_distance = 200  # Distance behind player
camera_height = 150  # Height above player
fovY = 90

# Track variables
track_segment_length = 100
track_segments = []  # List to store track segments
max_track_segments = 20

# =========================
# Obstacles (from your file)
# Rule 2: reduce intensity minimally by increasing spacing only.
# =========================
obstacles = []  # List of obstacles: (type, lane, z_position)
OBSTACLE_GROUND = 0  # Jump over these
OBSTACLE_AIR = 1     # Slide under these
obstacle_spawn_distance = 280  # Distance between obstacles (was 200)

# =========================
# From groupmate file: Environment, Coins, Power-ups, Score, Day/Night
# =========================
# Environment
environment_elements = []
last_env_generate_z = 0
ENV_X_MIN, ENV_X_MAX = 150, 400  # X-range for spawning elements (outside track)

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
DAY_NIGHT_DURATION = 10.0  # Seconds for one phase (day or night)
cycle_start_time = time.time()
DAY_COLOR = [0.53, 0.81, 0.98]
NIGHT_COLOR = [0.05, 0.05, 0.15]



def draw_button(rect, button_text, bg_color):
    """A helper function to draw a button with centered text."""
    # Draw button background
    glColor3f(bg_color[0], bg_color[1], bg_color[2])
    glBegin(GL_QUADS)
    glVertex2f(rect['x'], rect['y'])
    glVertex2f(rect['x'] + rect['w'], rect['y'])
    glVertex2f(rect['x'] + rect['w'], rect['y'] + rect['h'])
    glVertex2f(rect['x'], rect['y'] + rect['h'])
    glEnd()
    
    # Set text color to white
    glColor3f(1.0, 1.0, 1.0)
    
    # Calculate centered position for the text
    text_width = len(button_text) * 9 # Approx. width in pixels
    text_x = rect['x'] + (rect['w'] - text_width) / 2
    text_y = rect['y'] + (rect['h'] / 2) - 6
    
    glRasterPos2f(text_x, text_y)
    for char in button_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))



def draw_pause_menu():
    """Draws the semi-transparent overlay and the pause menu buttons."""
    # --- THIS IS THE KEY: We need to disable the depth test for the 2D overlay ---
    glDisable(GL_DEPTH_TEST)

    # Set up 2D orthographic view
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # --- Draw the semi-transparent background overlay ---
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.7) # Black with 70% opacity
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    glDisable(GL_BLEND)

    # Draw the menu buttons on top of the overlay
    draw_button(resume_button_rect, "Resume", (0.2, 0.6, 0.2)) # Green
    draw_button(restart_button_rect, "Restart", (0.2, 0.2, 0.8)) # Blue
    draw_button(exit_pause_button_rect, "Exit", (0.8, 0.2, 0.2)) # Red

    # Restore the previous matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # --- Re-enable the depth test for the next 3D frame ---
    glEnable(GL_DEPTH_TEST)


        
def draw_main_menu():
    """Draws the main menu screen, correctly handling the depth test."""
    # --- THIS IS THE FIX: Disable depth test for 2D UI drawing ---
    glDisable(GL_DEPTH_TEST)

    # Set up 2D orthographic view
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw the title
    glColor3f(1.0, 1.0, 1.0)
    title_text = "Main Menu"
    title_width = len(title_text) * 9
    title_x = (1000 - title_width) / 2
    glRasterPos2f(title_x, 600)
    for char in title_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Draw the buttons using the new helper function
    draw_button(start_button_rect, "Start", (0.2, 0.6, 0.2))
    draw_button(close_button_rect, "Exit", (0.8, 0.2, 0.2))

    # Restore the previous matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # --- Re-enable the depth test for 3D game rendering ---
    glEnable(GL_DEPTH_TEST)





def start_game():
    """Resets all game variables and switches the state to playing."""
    # Declare all globals being modified
    global current_game_state, player_z, player_y, player_lane, player_speed, score, lives
    global is_jumping, is_sliding, obstacles, coins, power_ups, reserved_slots, cycle_start_time
    global pause_start_time, total_paused_duration

    # Switch state
    current_game_state = GAME_STATE_PLAYING
    
    # Reset all relevant variables
    player_lane = 0
    player_z = 0
    player_y = 0
    player_speed = 5.0
    score = 0
    lives = 1
    is_jumping = False
    is_sliding = False
    
    obstacles.clear()
    coins.clear()
    power_ups.clear()
    reserved_slots.clear()
    
    init_track()
    cycle_start_time = time.time()
    
    # --- FIX: Reset pause timers for the new game session ---
    pause_start_time = 0
    total_paused_duration = 0








# =========================
# Rule 1: Shared spawn-slot deconfliction (minimal additions)
# =========================
BIN_Z = 40  # coarse Z bin size to avoid exact overlaps
reserved_slots = set()  # (lane, z_bin)

def _slot_key(lane, z):
    return (lane, int(z // BIN_Z))

def _slot_free(lane, z):
    return _slot_key(lane, z) not in reserved_slots

def _reserve(lane, z):
    reserved_slots.add(_slot_key(lane, z))

def _cleanup_reservations():
    # Free slots far behind player
    back_bin = int((player_z - 200) // BIN_Z)
    stale = [k for k in reserved_slots if k[1] < back_bin]
    for k in stale:
        reserved_slots.discard(k)

# =========================
# Original init and track from your file
# =========================
track_segments = []
MIN_TRACK_AHEAD = 1200 # Always try to have this much track generated ahead

def init_track():
    """Initializes the track with a few straight segments."""
    global track_segments
    track_segments.clear()
    
    # Start with a few straight segments
    start_pos = (0, 0, -200) # Start slightly behind the origin
    direction = (0, 0, 1)
    for _ in range(10):
        segment = TrackSegment(start_pos, direction)
        track_segments.append(segment)
        start_pos = segment.end


def manage_track():
    """Manages adding and removing track segments, including turns."""
    global track_segments
    
    # Remove segments that are far behind the player
    track_segments = [seg for seg in track_segments if seg.end[2] > player_z - 500]

    # Add new segments if we don't have enough track ahead
    last_segment = track_segments[-1]
    while last_segment.end[2] < player_z + MIN_TRACK_AHEAD:
        new_direction = last_segment.direction
        turn_chance = random.random()
        
        # 30% chance to generate a turn segment
        if turn_chance < 0.15: # Turn left
            # New direction is the old "right" vector, but negated
            new_direction = (-last_segment.right_vec[0], 0, -last_segment.right_vec[2])
        elif turn_chance < 0.30: # Turn right
            new_direction = last_segment.right_vec
        
        new_segment = TrackSegment(last_segment.end, new_direction)
        track_segments.append(new_segment)
        last_segment = new_segment

# =========================
# Your obstacle spawner (unchanged logic, with only deconfliction + spacing variable)
# =========================
def spawn_obstacles():
    """Spawn obstacles randomly on the track (kept from your file, with slot check)."""
    global obstacles
    # Remove obstacles that are too far behind
    obstacles = [obs for obs in obstacles if obs[2] > player_z - 200]

    # Add new obstacles if needed (original condition kept)
    if not obstacles or max(obs[2] for obs in obstacles) < player_z + 800:
        obstacle_lane = random.randint(-1, 1)  # Random lane
        obstacle_type = random.choice([OBSTACLE_GROUND, OBSTACLE_AIR])
        obstacle_z = (max(obs[2] for obs in obstacles) + obstacle_spawn_distance) if obstacles else player_z + 300

        # Rule 1: do not overlap with coins/power-ups/other obstacles
        if _slot_free(obstacle_lane, obstacle_z):
            obstacles.append((obstacle_type, obstacle_lane, obstacle_z))
            _reserve(obstacle_lane, obstacle_z)

def draw_obstacles():
    """Draw all obstacles (unmodified)."""
    for obstacle_type, lane, z_pos in obstacles:
        if abs(z_pos - player_z) < 500:  # Only draw nearby obstacles
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
# Your player state (jump/slide)
# =========================
def update_player_state():
    global player_y, is_jumping, is_sliding

    current_time = time.time()

    # Handle jumping (unchanged)
    if is_jumping:
        elapsed = current_time - jump_start_time
        if elapsed < jump_duration:
            progress = elapsed / jump_duration
            player_y = jump_height * (1 - (2 * progress - 1) ** 2)
        else:
            is_jumping = False
            player_y = 0

    # Handle sliding (unchanged)
    if is_sliding:
        elapsed = current_time - slide_start_time
        if elapsed >= slide_duration:
            is_sliding = False

def check_collisions():
    """Your obstacle collision (unchanged)."""
    player_lane_x = lane_positions[player_lane + 1]
    for obstacle_type, lane, z_pos in obstacles:
        lane_x = lane_positions[lane + 1]
        if (abs(player_lane_x - lane_x) < 30 and abs(player_z - z_pos) < 40):
            if obstacle_type == OBSTACLE_GROUND and not is_jumping:
                return True
            elif obstacle_type == OBSTACLE_AIR and not is_sliding:
                return True
    return False

# =========================
# Your character and track render (unchanged)
# =========================
def draw_character():
    """Draws the character at their dynamic world position and rotation."""
    world_pos, direction = get_player_position_and_direction()
    
    glPushMatrix()
    glTranslatef(world_pos[0], world_pos[1], world_pos[2])
    
    # Rotate the character to face the direction of the track
    angle = math.atan2(direction[0], direction[2]) * (180 / math.pi)
    glRotatef(-angle, 0, 1, 0)

    if is_sliding:
        glRotatef(90, 1, 0, 0)  # slide visual

    arm_swing = math.sin(animation_time * running_animation_speed) * 30
    leg_swing = math.sin(animation_time * running_animation_speed) * 20

    glPushMatrix()
    glTranslatef(0, 50, 0)
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
    """Draws the new, dynamic track with turns."""
    box_size = 20
    for segment in track_segments:
        # Only draw nearby segments
        if abs(segment.start[2] - player_z) < MIN_TRACK_AHEAD:
            num_boxes = int(segment.length / box_size)
            for i in range(num_boxes):
                for lane_idx in [-1, 0, 1]: # Left, center, right lanes
                    # Calculate position along the segment's direction
                    pos_along_segment = i * box_size
                    center_x = segment.start[0] + segment.direction[0] * pos_along_segment
                    center_z = segment.start[2] + segment.direction[2] * pos_along_segment
                    
                    # Offset by the lane using the segment's "right" vector
                    box_x = center_x + segment.right_vec[0] * lane_width * lane_idx
                    box_z = center_z + segment.right_vec[2] * lane_width * lane_idx

                    # Alternate colors for checkerboard pattern
                    if (i + abs(lane_idx)) % 2 == 0:
                        glColor3f(0.7, 0.7, 0.7)
                    else:
                        glColor3f(0.3, 0.3, 0.3)
                        
                    # We can use a simple cube since the world rotation is handled by the vectors
                    glPushMatrix()
                    glTranslatef(box_x, -40, box_z)
                    glScalef(3.0, 0.2, 1.0) # A flat box
                    # We need to rotate the cube to align with the track segment
                    angle = math.atan2(segment.direction[0], segment.direction[2]) * (180/math.pi)
                    glRotatef(-angle, 0, 1, 0)
                    glutSolidCube(box_size)
                    glPopMatrix()

# =========================
# Camera (unchanged)
# =========================
def setup_camera():
    """The camera now follows the dynamic player position."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    world_pos, direction = get_player_position_and_direction()
    
    # Position the camera behind the player, relative to the track direction
    cam_x = world_pos[0] - direction[0] * camera_distance
    cam_y = world_pos[1] + camera_height
    cam_z = world_pos[2] - direction[2] * camera_distance
    
    # The camera should look at a point slightly in front of the player
    look_at_x = world_pos[0]
    look_at_y = world_pos[1] + 50 # Look slightly above the player's feet
    look_at_z = world_pos[2]
    
    gluLookAt(cam_x, cam_y, cam_z, look_at_x, look_at_y, look_at_z, 0, 1, 0)

# =========================
# Groupmate: Environment drawing (unchanged)
# =========================
def draw_tree(position):
    """Draws a larger low-poly tree at a given position with leaves pointing upward."""
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])

    # Tree Trunk - This part is correct and remains unchanged.
    glColor3f(0.5, 0.35, 0.05) # Brown color for trunk
    glPushMatrix()
    glTranslatef(0, 25, 0)
    glScalef(0.5, 5.0, 0.5)
    glutSolidCube(10)
    glPopMatrix()

    # Tree Foliage - Now rotated to point up
    glColor3f(0.0, 0.5, 0.0) # Dark green for leaves
    glPushMatrix() # Use a new matrix stack for the foliage
    glTranslatef(0, 60, 0) # Move the foliage to the top of the trunk
    
    # --- THIS IS THE FIX ---
    # Rotate the cone by -90 degrees around the X-axis.
    # This pivots the Z-axis (forward) to become the Y-axis (up).
    glRotatef(-90, 1, 0, 0) 
    
    # Now, draw the cone. It will be drawn in the rotated orientation.
    glutSolidCone(30, 60, 10, 5) # base, height, slices, stacks
    
    glPopMatrix() # End of foliage matrix
    glPopMatrix() # End of tree matrix


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
    environment_elements = [elem for elem in environment_elements if elem['pos'][2] > player_z - camera_distance]

def draw_environment():
    for element in environment_elements:
        if element['type'] == 'tree':
            draw_tree(element['pos'])
        elif element['type'] == 'statue':
            draw_broken_statue(element['pos'])
        elif element['type'] == 'rock':
            draw_rock_formation(element['pos'])

# =========================
# Groupmate: Coins and power-ups (with minimal slot checks and coin height tweak)
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
    last_segment_z = max(track_segments, key=lambda seg: seg.end[2]).end[2] if track_segments else 0
    spawn_z = last_segment_z + 100
    spawn_chances = {'yellow': 0.005, 'green': 0.002, 'purple': 0.0005}
    for coin_type, chance in spawn_chances.items():
        if random.random() < chance:
            # Rule 3: two heights; aerial depends on jump height so jumping is required
            pos_y = (40 + jump_height) if random.random() < 0.3 else 10  # minimal change
            lane = random.choice([-1, 0, 1])
            lane_x = lane_positions[lane + 1]
            # Rule 1: avoid overlap by slot check
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
        spawn_z = (max(track_segments, key=lambda seg: seg.end[2]).end[2] if track_segments else 0) + 100
        # Rule 1: avoid overlap
        if _slot_free(lane, spawn_z):
            power_ups.append({'type': power_up_type, 'pos': [lane_x, 10, spawn_z]})
            _reserve(lane, spawn_z)
            last_power_up_spawn_time = current_time

def manage_collisions_and_effects():
    """
    Handles all player collision checks and activates/deactivates power-up effects,
    correctly using true gameplay time and player jump height.
    """
    # Declare all necessary global variables at the top
    global coins, power_ups, score, lives
    global player_speed, is_speed_boost_active, speed_boost_end_time
    global is_shield_active, shield_end_time, is_magnet_active, magnet_end_time

    # --- FIX: Use a single, pause-adjusted time for all calculations in this frame ---
    current_time = time.time() - total_paused_duration
    
    player_x = lane_positions[player_lane + 1]

    # --- Power-up Collection ---
    for p_up in power_ups[:]:
        # Simple collision check for power-ups (which are always at ground level)
        if abs(player_x - p_up['pos'][0]) < 20 and abs(player_z - p_up['pos'][2]) < 20:
            p_type = p_up['type']
            if p_type == 'speed_boost':
                if not is_speed_boost_active: # Prevent speed from multiplying on rapid collection
                    player_speed *= 1.5
                is_speed_boost_active = True
                # Set end time based on the adjusted current_time
                speed_boost_end_time = current_time + POWER_UP_DURATION
            elif p_type == 'extra_life':
                lives += 1
            elif p_type == 'shield':
                is_shield_active = True
                shield_end_time = current_time + POWER_UP_DURATION
            elif p_type == 'magnet':
                is_magnet_active = True
                magnet_end_time = current_time + POWER_UP_DURATION
            power_ups.remove(p_up)

    # --- Magnet Effect ---
    if is_magnet_active:
        for coin in coins:
            # Pull coins within a certain forward distance of the player
            if abs(player_z - coin['pos'][2]) < 150:
                # Animate coin moving towards player's current position
                coin['pos'][0] += (player_x - coin['pos'][0]) * 0.1
                # Use player's current y-position for the animation target
                coin['pos'][1] += ((40 + player_y) - coin['pos'][1]) * 0.1

    # --- Coin Collection ---
    for coin in coins[:]:
        # --- FIX: Collision check now includes player's jump height (player_y) ---
        if (abs(player_x - coin['pos'][0]) < 20 and
            abs(player_z - coin['pos'][2]) < 20 and
            abs((40 + player_y) - coin['pos'][1]) < 50): # Player's body center is at 40 + y_offset
            score += coin['value']
            coins.remove(coin)

    # --- Power-up Deactivation ---
    # This logic now works correctly because current_time is pause-adjusted.
    if is_speed_boost_active and current_time > speed_boost_end_time:
        is_speed_boost_active = False
        player_speed /= 1.5
    if is_shield_active and current_time > shield_end_time:
        is_shield_active = False
    if is_magnet_active and current_time > magnet_end_time:
        is_magnet_active = False

    # --- Cleanup collectibles far behind player ---
    # This logic remains correct and is good for performance.
    coins[:] = [c for c in coins if c['pos'][2] > player_z - 50]
    power_ups[:] = [p for p in power_ups if p['pos'][2] > player_z - 50]


# =========================
# Groupmate: Day/Night color (unchanged)
# =========================
def update_and_apply_sky_color():
    """
    Calculates and applies a smooth day/night sky color transition,
    correctly freezing the cycle when the game is paused.
    """
    
    # This variable will hold the "true" gameplay time.
    effective_elapsed_time = 0
    
    # --- THIS IS THE FIX ---
    if current_game_state == GAME_STATE_PAUSED:
        # If the game is paused, "freeze" the elapsed time.
        # We calculate what the elapsed time was at the moment pause was hit.
        effective_elapsed_time = (pause_start_time - cycle_start_time) - total_paused_duration
    else:
        # If the game is running (or in the main menu), calculate time normally.
        # This correctly accounts for all previous, completed pauses.
        effective_elapsed_time = (time.time() - cycle_start_time) - total_paused_duration

    # The rest of the function remains the same, but now uses the correct "effective_elapsed_time".
    total_cycle_time = DAY_NIGHT_DURATION * 2
    cycle_progress = (effective_elapsed_time % total_cycle_time) / total_cycle_time
    
    # Use a cosine wave for a smooth interpolation factor 't'
    t = (math.cos(cycle_progress * 2 * math.pi) + 1) / 2.0
    
    # Linearly interpolate between the day and night colors
    current_color = [
        DAY_COLOR[i] * t + NIGHT_COLOR[i] * (1 - t)
        for i in range(3)
    ]
    
    # Apply this calculated color to OpenGL's background
    glClearColor(current_color[0], current_color[1], current_color[2], 1.0)


# =========================
# Main update (merged: your logic + calls to groupmate managers)
# =========================
def get_player_position_and_direction():
    """Finds the player's current segment and calculates their world position and direction."""
    for segment in track_segments:
        # A simple way to find the current segment is by checking the z-position
        # (This can be optimized later if needed)
        if segment.start[2] <= player_z < segment.end[2] or segment.start[0] <= player_z < segment.end[0]:
            # Calculate how far along the segment the player is
            if segment.direction[2] != 0: # Moving along Z
                progress = (player_z - segment.start[2]) / segment.length
            else: # Moving along X
                progress = (player_z - segment.start[0]) / segment.length
            
            progress = max(0, min(1, progress)) # Clamp progress between 0 and 1

            # Get the center point on the track
            center_x = segment.start[0] + segment.direction[0] * segment.length * progress
            center_z = segment.start[2] + segment.direction[2] * segment.length * progress

            # Add the lane offset using the segment's "right" vector
            final_x = center_x + segment.right_vec[0] * lane_width * player_lane
            final_z = center_z + segment.right_vec[2] * lane_width * player_lane

            return (final_x, player_y, final_z), segment.direction
            
    # Fallback if no segment is found (shouldn't happen with proper track management)
    return (lane_positions[player_lane + 1], player_y, player_z), (0, 0, 1)


def update_game():
    """Update game state - now with turning track logic."""
    global player_z, player_speed, animation_time
    animation_time = time.time()
    update_player_state()
    
    player_z += player_speed
    player_speed += speed_increase_factor
    
    # Call the new track manager
    manage_track()
    
    # Manage all other game entities
    spawn_obstacles()
    manage_environment_elements()
    manage_coins()
    manage_power_ups()
    manage_collisions_and_effects()
    
    if check_collisions():
        print("Collision detected!")
        # For now, we'll just pause, later this will be game over
        global current_game_state
        current_game_state = GAME_STATE_PAUSED

    _cleanup_reservations()


# =========================
# Input (unchanged)
# =========================
def keyboardListener(key, x, y):
    """Handles lane switching and jump/slide."""
    global player_lane, is_jumping, is_sliding, jump_start_time, slide_start_time
    
    # --- THIS LOGIC IS NOW MOVED TO specialKeyListener ---
    # if key == b'a' or key == b'A': ...
    # if key == b'd' or key == b'D': ...
    
    if key == b'w' or key == b'W':
        if not is_jumping and not is_sliding:
            is_jumping = True
            jump_start_time = time.time()
    elif key == b's' or key == b'S':
        if not is_sliding and not is_jumping:
            is_sliding = True
            slide_start_time = time.time()

def specialKeyListener(key, x, y):
    """Handles lane switching AND the new turning logic."""
    global player_lane, current_game_state
    
    current_pos, current_dir = get_player_position_and_direction()
    
    # Find the next segment to check for turns
    current_segment_index = -1
    for i, segment in enumerate(track_segments):
        if segment.start[2] <= player_z < segment.end[2] or segment.start[0] <= player_z < segment.end[0]:
            current_segment_index = i
            break
            
    if current_segment_index != -1 and current_segment_index + 1 < len(track_segments):
        next_segment = track_segments[current_segment_index + 1]
        
        # Check if we are near a turn
        is_near_turn = (player_z > next_segment.start[2] - 50) or (player_z > next_segment.start[0] - 50)
        
        if is_near_turn and next_segment.direction != current_dir:
            # A turn is available
            if key == GLUT_KEY_LEFT and next_segment.direction == (-current_dir[2], 0, current_dir[0]):
                # Successful left turn
                player_z += 100 # Move player onto the new segment
                return
            elif key == GLUT_KEY_RIGHT and next_segment.direction == (current_dir[2], 0, -current_dir[0]):
                # Successful right turn
                player_z += 100
                return
            else:
                # Missed the turn
                current_game_state = GAME_STATE_PAUSED
                return

    # If not near a turn, handle regular lane switching
    if key == GLUT_KEY_LEFT:
        if player_lane > -1:
            player_lane -= 1
    elif key == GLUT_KEY_RIGHT:
        if player_lane < 1:
            player_lane += 1





def mouseListener(button, state, x, y):
    """Handles mouse inputs, now correctly managing global pause timing variables."""
    # --- FIX: Declare variables as global to avoid UnboundLocalError ---
    global current_game_state, pause_start_time, total_paused_duration
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        mouse_y = 800 - y

        # --- State 1: Main Menu ---
        if current_game_state == GAME_STATE_MAIN_MENU:
            if (start_button_rect['x'] <= x <= start_button_rect['x'] + start_button_rect['w'] and
                start_button_rect['y'] <= mouse_y <= start_button_rect['y'] + start_button_rect['h']):
                start_game()
            elif (close_button_rect['x'] <= x <= close_button_rect['x'] + close_button_rect['w'] and
                  close_button_rect['y'] <= mouse_y <= close_button_rect['y'] + close_button_rect['h']):
                glutLeaveMainLoop()
        
        # --- State 2: Playing (check for pause button click) ---
        elif current_game_state == GAME_STATE_PLAYING:
            if (pause_button_rect['x'] <= x <= pause_button_rect['x'] + pause_button_rect['w'] and
                pause_button_rect['y'] <= mouse_y <= pause_button_rect['y'] + pause_button_rect['h']):
                pause_start_time = time.time()
                current_game_state = GAME_STATE_PAUSED
                
        # --- State 3: Paused (check for menu button clicks) ---
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
                start_game() # This now correctly resets everything
            # Exit Button
            elif (exit_pause_button_rect['x'] <= x <= exit_pause_button_rect['x'] + exit_pause_button_rect['w'] and
                  exit_pause_button_rect['y'] <= mouse_y <= exit_pause_button_rect['y'] + exit_pause_button_rect['h']):
                glutLeaveMainLoop()





def idle():
    """Idle function - only updates the game if it's in the playing state."""
    # The game logic will only run when the state is PLAYING.
    # It will be frozen during MAIN_MENU and PAUSED states.
    if current_game_state == GAME_STATE_PLAYING:
        update_game()
    
    glutPostRedisplay() # Always redisplay to keep the window responsive



# =========================
# Rendering (merged HUD from both)
# =========================
def showScreen():
    """Main display function that now directs to menu, game, or paused rendering."""
    # Clear the screen. Black is the default for the main menu.
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if current_game_state == GAME_STATE_MAIN_MENU:
        draw_main_menu()
    
    elif current_game_state == GAME_STATE_PLAYING or current_game_state == GAME_STATE_PAUSED:
        # --- Render the game scene for BOTH playing and paused states ---
        update_and_apply_sky_color()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, 1000, 800)
        setup_camera()
        
        draw_track()
        draw_environment()
        # This is the old draw_collectibles function
        for coin in coins: draw_coin(coin)
        for p_up in power_ups: draw_power_up_icon(p_up)
        draw_obstacles()
        draw_character()
        draw_active_power_up_effects()
        
        # --- Draw the UI (HUD + Pause Button) ---
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Draw the HUD text
        glColor3f(1, 1, 1)
        glRasterPos2f(10, 770)
        info_text = f"Score: {score} | Lives: {lives} | Speed: {player_speed:.1f}"
        for ch in info_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        # Draw the Pause button (purple)
        draw_button(pause_button_rect, "Pause", (0.5, 0.2, 0.8))
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        
        # --- If the game is paused, draw the menu on top of everything ---
        if current_game_state == GAME_STATE_PAUSED:
            draw_pause_menu()

    glutSwapBuffers()



def main():
    init_track()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Temple Run - Merged (Obstacles + Environment + Coins/PowerUps)")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
