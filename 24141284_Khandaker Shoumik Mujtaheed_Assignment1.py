
#Khandaker Shoumik Mujtaheed 
#ID - 24141284
#Section - 26
#_______________________________________________________________________________________________________

import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Global variables for window dimensions (16:9 ratio)
W_Width = 960
W_Height = 540

# Day/Night cycle variables
sky_color_steps = [
    (0.529, 0.808, 0.922),  # Step 0: Light blue (day)
    (0.0, 0.7, 1.0),        # Step 1: Blue (day)
    (0.75, 0.75, 0.75),     # Step 2: Light grey (day)
    (0.5, 0.5, 0.5),        # Step 3: Darker grey (night)
    (0.3, 0.3, 0.3),        # Step 4: Darker grey (night)
    (0.1, 0.1, 0.1)         # Step 5: Darkest grey (night)
]

current_color_step = 0
sky_color = sky_color_steps[current_color_step]
ground_color = (0.545, 0.271, 0.075)   # Brown (stays constant)

# Global raindrop variables
raindrops = []
rain_direction = 0.0
raindrop_color = (0.0, 0.0, 0.5)  # Dark blue for day

def get_rain_color(step):
    if step < 3:  # Day (first 3 steps)
        return (0.0, 0.0, 0.5)  # Dark blue
    else:  # Night (last 3 steps)
        return (1.0, 1.0, 1.0)  # White

def update_day_night_colors():
    global sky_color, raindrop_color, current_color_step
    sky_color = sky_color_steps[current_color_step]
    raindrop_color = get_rain_color(current_color_step)

def init_raindrops():
    global raindrops
    raindrops = []
    num_raindrops = 100
    
    for _ in range(num_raindrops):
        x = random.uniform(-W_Width/2, W_Width/2)
        y = random.uniform(W_Height/2, W_Height)
        raindrops.append([x, y])

def convert_coordinate(x, y):
    global W_Width, W_Height
    a = x - (W_Width/2)
    b = (W_Height/2) - y 
    return a, b

def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, W_Width/W_Height, 1, 500.0)
    init_raindrops()
    update_day_night_colors()

def draw_background():
    # Sky (top half) using GL_QUADS
    glColor3f(*sky_color)
    glBegin(GL_QUADS)
    glVertex2f(-W_Width/2, 0)
    glVertex2f(W_Width/2, 0)
    glVertex2f(W_Width/2, W_Height/2)
    glVertex2f(-W_Width/2, W_Height/2)
    glEnd()
    
    # Ground (bottom half) using GL_QUADS
    glColor3f(*ground_color)
    glBegin(GL_QUADS)
    glVertex2f(-W_Width/2, -W_Height/2)
    glVertex2f(W_Width/2, -W_Height/2)
    glVertex2f(W_Width/2, 0)
    glVertex2f(-W_Width/2, 0)
    glEnd()

def draw_raindrops():
    global raindrops, rain_direction, raindrop_color
    
    glColor3f(*raindrop_color)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    
    for raindrop in raindrops:
        x, y = raindrop
        
        # Calculate angle offset for the raindrop line itself
        angle_offset = rain_direction * 3
        
        # Draw angled line (raindrop)
        glVertex2f(x, y)
        glVertex2f(x + angle_offset, y - 10)
    
    glEnd()
    glLineWidth(1.0)

def update_raindrops():
    global raindrops, rain_direction
    
    for i, raindrop in enumerate(raindrops):
        x, y = raindrop
        
        # Move raindrop down (vertical component)
        y -= 1.5
        
        # Move raindrop horizontally based on rain direction (diagonal component)
        x += rain_direction 
        
        # Reset raindrop if it goes below screen or too far horizontally
        if y < -W_Height/2 or x < -W_Width/2 - 100 or x > W_Width/2 + 100:
            x = random.uniform(-W_Width/2, W_Width/2)
            y = random.uniform(W_Height/2, W_Height + 100)
        
        raindrops[i] = [x, y]

def draw_house_base(x_center, ground_y, house_size):
    house_width = house_size * 1.5
    house_height = house_size
    half_width = house_width / 2
    
    glColor3f(0.8, 0.7, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(x_center - half_width, ground_y)
    glVertex2f(x_center + half_width, ground_y)
    glVertex2f(x_center + half_width, ground_y + house_height)
    glVertex2f(x_center - half_width, ground_y + house_height)
    glEnd()

def draw_house_roof(x_center, ground_y, house_size):
    house_width = house_size * 1.5
    half_width = house_width / 2
    roof_height = house_size * 0.6
    
    glColor3f(0.7, 0.2, 0.2)
    glBegin(GL_TRIANGLES)
    glVertex2f(x_center - half_width - 10, ground_y + house_size)
    glVertex2f(x_center + half_width + 10, ground_y + house_size)
    glVertex2f(x_center, ground_y + house_size + roof_height)
    glEnd()

def draw_house_door(x_center, ground_y, house_size):
    door_width = house_size * 0.45
    door_height = house_size * 0.75
    door_half_width = door_width / 2
    
    glColor3f(0.4, 0.2, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(x_center - door_half_width, ground_y)
    glVertex2f(x_center + door_half_width, ground_y)
    glVertex2f(x_center + door_half_width, ground_y + door_height)
    glVertex2f(x_center - door_half_width, ground_y + door_height)
    glEnd()

def draw_house_windows(x_center, ground_y, house_size):
    window_size = house_size * 0.25
    window_y = ground_y + house_size * 0.6
    window_offset = house_size * 0.45
    
    glColor3f(1.0, 1.0, 1.0)
    
    # Left window
    glBegin(GL_QUADS)
    glVertex2f(x_center - window_offset - window_size/2, window_y - window_size/2)
    glVertex2f(x_center - window_offset + window_size/2, window_y - window_size/2)
    glVertex2f(x_center - window_offset + window_size/2, window_y + window_size/2)
    glVertex2f(x_center - window_offset - window_size/2, window_y + window_size/2)
    glEnd()
    
    # Right window
    glBegin(GL_QUADS)
    glVertex2f(x_center + window_offset - window_size/2, window_y - window_size/2)
    glVertex2f(x_center + window_offset + window_size/2, window_y - window_size/2)
    glVertex2f(x_center + window_offset + window_size/2, window_y + window_size/2)
    glVertex2f(x_center + window_offset - window_size/2, window_y + window_size/2)
    glEnd()

def draw_house(x_center, ground_y, house_size):
    draw_house_base(x_center, ground_y, house_size)
    draw_house_roof(x_center, ground_y, house_size)
    draw_house_door(x_center, ground_y, house_size)
    draw_house_windows(x_center, ground_y, house_size)

def draw_tree_trunk(x_center, ground_y):
    glColor3f(0.4, 0.2, 0.0)
    glBegin(GL_LINES)
    glVertex2f(x_center, ground_y)
    glVertex2f(x_center, ground_y + 50)
    glEnd()

def draw_tree_foliage(x_center, ground_y):
    glColor3f(0.0, 0.6, 0.0)
    
    triangle_y_positions = [
        ground_y + 25,
        ground_y + 25 + 21,
        ground_y + 25 + 42
    ]
    
    for base_y in triangle_y_positions:
        glBegin(GL_TRIANGLES)
        glVertex2f(x_center - 20, base_y)
        glVertex2f(x_center + 20, base_y)
        glVertex2f(x_center, base_y + 60)
        glEnd()

def draw_trees():
    num_trees = 13
    spacing = W_Width / (num_trees + 1)
    ground_y = 0
    
    for i in range(1, num_trees + 1):
        x_center = spacing * i - W_Width/2
        draw_tree_trunk(x_center, ground_y)
        draw_tree_foliage(x_center, ground_y)

def keyboardListener(key, x, y):
    global rain_direction, current_color_step
    if key == b'r' or key == b'R':
        rain_direction = 0.0
        print("Rain direction reset to straight down")
    
    # Day/Night cycle controls
    elif key == b'd' or key == b'D':
        if current_color_step > 0:
            current_color_step -= 1
            update_day_night_colors()
            phase = "day" if current_color_step < 3 else "night"
            print(f"Day cycle: Step {current_color_step} ({phase})")

    elif key == b'n' or key == b'N':
        if current_color_step < 5:
            current_color_step += 1
            update_day_night_colors()
            phase = "day" if current_color_step < 3 else "night"
            print(f"Night cycle: Step {current_color_step} ({phase})")
    
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global rain_direction
    if key == GLUT_KEY_LEFT and rain_direction>=-1.0:
        rain_direction -= 0.1
        print(f"Rain direction: {rain_direction:.1f} (left)")
    elif key == GLUT_KEY_RIGHT and rain_direction<=1.0:
        rain_direction += 0.1
        print(f"Rain direction: {rain_direction:.1f} (right)")
    
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)

    draw_background()
    draw_trees()
    draw_house(0, 0, 120)
    draw_raindrops()
    
    glutSwapBuffers()

def animate():
    """Animation callback for raindrop movement"""
    update_raindrops()
    glutPostRedisplay()

def reshape(width, height):
    global W_Width, W_Height
    W_Width = width
    W_Height = height
    glViewport(0, 0, width, height)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, width/height, 1, 500.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(0, 0)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
    
    glutCreateWindow(b"House Scene with Day/Night Cycle")
    init()
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMainLoop()

if __name__ == "__main__":
    main()

#   ========= TASK ONE ENDS ==========
#======================================================================================

# ========== TASK TWO =============

import sys
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Global window dimensions
W_Width = 800
W_Height = 600

# Global variables for points
points = []
point_size = 5.0           
velocity_magnitude = 0.5   
velocity_multiplier = 1   

# Blinking system 
is_blinking = False        
blink_frame_counter = 0    
blink_interval = 30        
blink_state = True        

# Freeze system 
is_frozen = False          

# Frame rate limiting variables
target_fps = 180
frame_duration = 1.0 / target_fps  
last_frame_time = time.time()

# Point class to represent each moving point
class Point:
    def __init__(self, x, y, dx, dy, color):
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.dx = dx            # Velocity in x direction
        self.dy = dy            # Velocity in y direction
        self.color = color      # RGB color tuple
        self.original_color = color  # Store original color for blinking

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-W_Width/2, W_Width/2, -W_Height/2, W_Height/2)
    glMatrixMode(GL_MODELVIEW)

def add_point(x_win, y_win):
    global points, point_size, velocity_magnitude, velocity_multiplier
    
    # Don't add points when frozen
    if is_frozen:
        print("System is frozen - cannot add new points")
        return
    
    x = x_win - W_Width/2
    y = W_Height/2 - y_win
    
    base_dx = velocity_magnitude if random.choice([True, False]) else -velocity_magnitude
    base_dy = velocity_magnitude if random.choice([True, False]) else -velocity_magnitude
    
    dx = base_dx * velocity_multiplier
    dy = base_dy * velocity_multiplier
    
    # Generate random RGB color
    color = (random.random(), random.random(), random.random())
    
    # Create and add new point
    new_point = Point(x, y, dx, dy, color)
    points.append(new_point)
    print(f"Point added at ({x:.1f}, {y:.1f}) with velocity ({dx:.3f}, {dy:.3f})")

def toggle_freeze():
    global is_frozen
    
    is_frozen = not is_frozen
    
    if is_frozen:
        print("SYSTEM FROZEN - All functionality disabled")
        print("Press SPACEBAR again to unfreeze")
    else:
        print("SYSTEM UNFROZEN - All functionality restored")

def toggle_blinking():
    global is_blinking, blink_frame_counter, blink_state, blink_interval
    
    # Don't allow blinking changes when frozen
    if is_frozen:
        print("System is frozen - cannot toggle blinking")
        return
    
    is_blinking = not is_blinking
    blink_frame_counter = 0
    blink_state = True  
    
    if is_blinking:
        print(f"Blinking started - points will blink every {blink_interval} frames")
    else:
        print("Blinking stopped - points returned to original colors")
        # Ensure all points return to their original colors
        for point in points:
            point.color = point.original_color

def update_blinking():
    global blink_frame_counter, blink_state, blink_interval
    
    # Don't update blinking when frozen
    if is_frozen:
        return
    
    if is_blinking:
        blink_frame_counter += 1
        
        if blink_frame_counter >= blink_interval:
            blink_frame_counter = 0
            blink_state = not blink_state
            
            for point in points:
                if blink_state:
                    point.color = point.original_color
                else:
                    point.color = (0.0, 0.0, 0.0)

def change_velocity(multiplier):
    global points, velocity_multiplier
    
    # Don't allow velocity changes when frozen
    if is_frozen:
        print("System is frozen - cannot change velocity")
        return
    
    velocity_multiplier *= multiplier
    
    for point in points:
        point.dx *= multiplier
        point.dy *= multiplier
    
    print(f"Velocity changed by {multiplier}x. Total multiplier: {velocity_multiplier:.2f}")

def update_points():
    global points
    
    if is_frozen:
        return
    
    for point in points:
        point.x += point.dx
        point.y += point.dy
        
        if point.x <= -W_Width/2 or point.x >= W_Width/2:
            point.dx = -point.dx  
        
        if point.y <= -W_Height/2 or point.y >= W_Height/2:
            point.dy = -point.dy  

def draw_points():
    global points, point_size
    
    glPointSize(point_size)
    glBegin(GL_POINTS)
    
    for point in points:
        glColor3f(*point.color) 
        glVertex2f(point.x, point.y)  
    
    glEnd()

def draw_boundary():
    glColor3f(1.0, 1.0, 1.0)  # White color for boundary
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(-W_Width/2, -W_Height/2)  # Bottom left
    glVertex2f(W_Width/2, -W_Height/2)   # Bottom right
    glVertex2f(W_Width/2, W_Height/2)    # Top right
    glVertex2f(-W_Width/2, W_Height/2)   # Top left
    glEnd()

# def draw_freeze_indicator():
#     """Draw a visual indicator when system is frozen"""
#     if is_frozen:
#         # Draw "FROZEN" text indicator (simplified as a red border)
#         glColor3f(1.0, 0.0, 0.0)  # Red color for freeze indicator
#         glLineWidth(4.0)
#         glBegin(GL_LINE_LOOP)
#         glVertex2f(-W_Width/2 + 10, -W_Height/2 + 10)
#         glVertex2f(W_Width/2 - 10, -W_Height/2 + 10)
#         glVertex2f(W_Width/2 - 10, W_Height/2 - 10)
#         glVertex2f(-W_Width/2 + 10, W_Height/2 - 10)
#         glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    draw_boundary()
    draw_points()
    #draw_freeze_indicator()  # Show freeze state visually
    
    glutSwapBuffers()

def mouse_callback(button, state, x, y):
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        add_point(x, y)
        glutPostRedisplay()
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        toggle_blinking()
        glutPostRedisplay()

def keyboard_callback(key, x, y):
    if key == b' ':  # Spacebar pressed
        toggle_freeze()
        glutPostRedisplay()

def special_key_callback(key, x, y):
    if key == GLUT_KEY_UP:
        change_velocity(2)  # Increase velocity by 1.5x
        glutPostRedisplay()
    elif key == GLUT_KEY_DOWN:
        change_velocity(0.5)  # Decrease velocity by 1.5x
        glutPostRedisplay()

def animate():
    global last_frame_time, frame_duration
    
    current_time = time.time()
    elapsed = current_time - last_frame_time
    
    if elapsed >= frame_duration:
        update_points()      
        update_blinking()    
        glutPostRedisplay()
        last_frame_time = current_time

def reshape(width, height):
    global W_Width, W_Height
    W_Width = width
    W_Height = height
    glViewport(0, 0, width, height)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-width/2, width/2, -height/2, height/2)
    glMatrixMode(GL_MODELVIEW)

def main():
    global last_frame_time
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Amazing Box")
    
    init()
    
    # Initialize frame timing
    last_frame_time = time.time()
    
    # Register callback functions
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse_callback)
    glutKeyboardFunc(keyboard_callback)  # Handle spacebar
    glutSpecialFunc(special_key_callback)
    glutIdleFunc(animate)
    
    print("===AMAZING BOX===")
    print("Right-click: Generate moving points")
    print("Left-click: Toggle blinking mode")
    print("UP arrow: Increase velocity by 2x")
    print("DOWN arrow: Decrease velocity by 2x")
    print("SPACEBAR: Freeze/Unfreeze all functionality")
    print(f"Frame rate limited to {target_fps} FPS")
    print("=" * 45)
    glutMainLoop()

if __name__ == "__main__":
    main()