import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random 
import time 

# Window and coordinate system 
W, H = 540, 960   # width x height  (vertical)

# Input state 
_keys = set()  

#Game state 
game_running = True           
game_playing = True           
game_over = False             
score = 0

# Timing (delta time) 
last_time = None              
max_frame_dt = 0.033          # 30 fps

# ---------------- Hitbox platform----------------
hitbox_platform_x = W // 2            
hitbox_platform_y = 60                
hitbox_platform_half_w = 70          
hitbox_platform_h = 28               
hitbox_platform_speed = 360.0        
hitbox_platform_color = (1.0, 1.0, 1.0)  

# Diamond parameters  
diamond_active = False
diamond_x = W // 2
diamond_y = H - 140
diamond_size = 22                 
diamond_color = (0.9, 0.9, 0.2)   
diamond_vy = -140.0               
diamond_accel = -12.0            
diamond_spawn_margin = 40        

# Difficulty ramp 
diamond_base_speed = 140.0        
diamond_speed_per_score = 10.0    

# UI buttons (hitbox regions) 
btn_restart_x0 = 20
btn_restart_x1 = 120
btn_row_y0 = H - 100
btn_row_y1 = H - 20

btn_play_x0 = W // 2 - 50
btn_play_x1 = W // 2 + 50

btn_quit_x0 = W - 120
btn_quit_x1 = W - 20

# Button icon toggle 
show_pause_icon = True  


# ---------------- Midpoint Line Algorithm ----------------
def put_pixel(x, y):
    glVertex2i(int(x), int(y))  

def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    adx = abs(dx)
    ady = abs(dy)
    if dx >= 0 and dy >= 0:
        return 0 if adx >= ady else 1
    if dx < 0 and dy >= 0:
        return 2 if adx >= ady else 3
    if dx < 0 and dy < 0:
        return 4 if adx >= ady else 5
    return 6 if adx >= ady else 7  # dx >= 0, dy < 0

def to_zone0(x, y, z):
    if z == 0: return x, y
    if z == 1: return y, x
    if z == 2: return y, -x
    if z == 3: return -x, y
    if z == 4: return -x, -y
    if z == 5: return -y, -x
    if z == 6: return -y, x
    if z == 7: return x, -y

def from_zone0(x, y, z):
    if z == 0: return x, y
    if z == 1: return y, x
    if z == 2: return -y, x
    if z == 3: return -x, y
    if z == 4: return -x, -y
    if z == 5: return -y, -x
    if z == 6: return y, -x
    if z == 7: return x, -y

def draw_line(x1, y1, x2, y2, color=(1, 1, 1)):
    z = find_zone(x1, y1, x2, y2)

    # Transform both points to zone 0
    ax1, ay1 = to_zone0(x1, y1, z)
    ax2, ay2 = to_zone0(x2, y2, z)

    # Ensure x increases
    if ax2 < ax1:
        ax1, ax2 = ax2, ax1
        ay1, ay2 = ay2, ay1

    dx = ax2 - ax1
    dy = ay2 - ay1

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    x, y = ax1, ay1
    r, g, b = color

    glBegin(GL_POINTS)
    glColor3f(r, g, b)

    while x <= ax2:
        ox, oy = from_zone0(x, y, z)
        put_pixel(ox, oy)
        if d > 0:
            y += 1
            d += incNE
        else:
            d += incE
        x += 1

    glEnd()


def draw_hitbox_platform():
    cx = hitbox_platform_x
    cy = hitbox_platform_y
    half_w = hitbox_platform_half_w
    h = hitbox_platform_h
    color = hitbox_platform_color
    
    bottom_inset_ratio = 0.65  
    bottom_half_width = int(half_w * bottom_inset_ratio)
    

    bottom_left_x = cx - bottom_half_width
    bottom_right_x = cx + bottom_half_width
    bottom_y = cy
    
 
    top_left_x = cx - half_w
    top_right_x = cx + half_w
    top_y = cy + h
    
    draw_line(bottom_left_x, bottom_y, bottom_right_x, bottom_y, color)
    draw_line(bottom_left_x, bottom_y, top_left_x, top_y, color)
    draw_line(bottom_right_x, bottom_y, top_right_x, top_y, color)
    draw_line(top_left_x, top_y, top_right_x, top_y, color)

# Button Drawing Functions 
def draw_restart_button():
    color = (0.0, 0.85, 0.8) #Teal 
    cx, cy = 70, H - 60  
    half = 20
    
    draw_line(cx - half//2, cy, cx, cy + half//2, color)
    draw_line(cx - half//2, cy, cx, cy - half//2, color)

def draw_play_pause_button():
    color = (1.0, 0.75, 0.2)
    cx, cy = W // 2, H - 60
    button_size = 30  
    half = button_size//2  
    
    if game_playing:
        bar_w = max(3, button_size//8)  
        bar_h = button_size*2//3        
        gap = bar_w + 2                 
        
        bx1 = cx - gap - bar_w
        by1 = cy - bar_h//2
        draw_line(bx1 + bar_w, by1, bx1 + bar_w, by1 + bar_h, color)
        draw_line(bx1 + bar_w, by1 + bar_h, bx1, by1 + bar_h, color)
       
        bx2 = cx + gap
        by2 = cy - bar_h//2
        draw_line(bx2 + bar_w, by2, bx2 + bar_w, by2 + bar_h, color)
        draw_line(bx2 + bar_w, by2 + bar_h, bx2, by2 + bar_h, color)
       
    else:
        p1_x, p1_y = cx - half//2, cy - half  
        p2_x, p2_y = cx - half//2, cy + half  
        p3_x, p3_y = cx + half, cy            
        
        draw_line(p1_x, p1_y, p2_x, p2_y, color)
        draw_line(p2_x, p2_y, p3_x, p3_y, color)
        draw_line(p3_x, p3_y, p1_x, p1_y, color)

def draw_quit_button():
    color =  (1.0, 0.2, 0.2)
    cx, cy = W - 70, H - 60
    size = 30  
    pad = size//6  

    draw_line(cx - size//2 + pad, cy - size//2 + pad, 
              cx + size//2 - pad, cy + size//2 - pad, color)
    draw_line(cx - size//2 + pad, cy + size//2 - pad, 
              cx + size//2 - pad, cy - size//2 + pad, color)

def draw_quit_button():
    color = (1.0, 0.2, 0.2)
    cx, cy = W - 70, H - 60
    pad = 20//5  
    size = 30
    
    draw_line(cx - size//2 + pad, cy - size//2 + pad, 
              cx + size//2 - pad, cy + size//2 - pad, color)
    
    draw_line(cx - size//2 + pad, cy + size//2 - pad, 
              cx + size//2 - pad, cy - size//2 + pad, color)

def draw_top_buttons():
    draw_restart_button()
    draw_play_pause_button() 
    draw_quit_button()


# AABB and Collision Detection 
class AABB:
    def __init__(self, x, y, w, h):
        self.x = x      
        self.y = y      
        self.w = w      
        self.h = h      

def aabb_intersect(box1, box2):
    return (box1.x < box2.x + box2.w and
            box1.x + box1.w > box2.x and
            box1.y < box2.y + box2.h and
            box1.y + box1.h > box2.y)

def hitbox_platform_aabb():
    top_width = 2 * hitbox_platform_half_w
    
    return AABB(
        hitbox_platform_x - hitbox_platform_half_w,  
        hitbox_platform_y,                          
        top_width,                                  
        hitbox_platform_h                          
    )

# Diamond Functions 
def spawn_diamond():
 
    global diamond_active, diamond_x, diamond_y, diamond_size, diamond_color, diamond_vy
    
    diamond_active = True
    
    #Random X position for diamond spawn
    diamond_x = random.randint(diamond_spawn_margin, W - diamond_spawn_margin)
    
    # Start from top of screen
    diamond_y = H - 140
    diamond_size = random.randint(18, 22)
    
    #Random colors for each diamond
    r = random.uniform(0.5, 1.0)
    g = random.uniform(0.5, 1.0)
    b = random.uniform(0.5, 1.0)
    diamond_color = (r, g, b)
    
    # Initlal velocity 
    diamond_vy = -(diamond_base_speed + score * diamond_speed_per_score)


def draw_diamond():
    if not diamond_active:
        return
    

    cx = diamond_x
    cy = diamond_y
    size = diamond_size
    color = diamond_color
    
    top    = (cx, cy + size)
    right  = (cx + size, cy)
    bottom = (cx, cy - size)
    left   = (cx - size, cy)
    
    # Draw the 4 diamond edges using midpoint lines
    draw_line(top[0], top[1], right[0], right[1], color)      
    draw_line(right[0], right[1], bottom[0], bottom[1], color) 
    draw_line(bottom[0], bottom[1], left[0], left[1], color)   
    draw_line(left[0], left[1], top[0], top[1], color)        

def diamond_aabb():
    if not diamond_active:
        return AABB(0, 0, 0, 0)  
    
    # Diamond's bounding box (square)
    size = diamond_size
    return AABB(
        diamond_x - size,    
        diamond_y - size,      
        2 * size,           
        2 * size           
    )

# Game Control Functions 
def restart_game():
    global game_playing, game_over, score, hitbox_platform_x, hitbox_platform_color, last_time
    
    # Reset game state
    game_playing = True
    game_over = False
    score = 0
    
    # Reset platform position and color
    hitbox_platform_x = W // 2
    hitbox_platform_color =  (1.0, 1.0, 1.0) #White reset
    
    # Reset timing
    last_time = None
    
    # Spawn first diamond
    spawn_diamond()
    
    print("Starting Over")

def toggle_play_pause():
    global game_playing, show_pause_icon

    if game_over:
        return
    
    # Toggle the playing state
    game_playing = not game_playing
    
    # Update icon state for button display
    show_pause_icon = game_playing
    
    if game_playing:
        print("Game Resumed")
    else:
        print("Game Paused")

def trigger_game_over():
    global game_over, game_playing, diamond_active, hitbox_platform_color
    
    game_over = True
    game_playing = False
    diamond_active = False  # Remove current diamond
    hitbox_platform_color = (1.0, 0.0, 0.0) # Turn platform red
    
    print(f"Game Over (final score={score})")

def quit_game():
    print(f"Goodbye (score={score})")
    glutLeaveMainLoop()

# ---------------- Input Handling ----------------
def special_key_down(key, x, y):
    _keys.add(key)

def special_key_up(key, x, y):
    if key in _keys:
        _keys.remove(key)

def mouse_click(button, state, x, y):
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    
    # Convert to bottom-left origin coordinates
    mx, my = x, H - y
    
    # Check restart button (left arrow)
    if btn_restart_x0 <= mx <= btn_restart_x1 and btn_row_y0 <= my <= btn_row_y1:
        restart_game()
        return
    
    # Check play/pause button (center)
    if btn_play_x0 <= mx <= btn_play_x1 and btn_row_y0 <= my <= btn_row_y1:
        toggle_play_pause()
        return
    
    # Check quit button (right)
    if btn_quit_x0 <= mx <= btn_quit_x1 and btn_row_y0 <= my <= btn_row_y1:
        quit_game()
        return

def keyboard_input(key, x, y):
    if key == b'\x1b':  # ESC key
        quit_game()

# ---------------- Game Update ----------------
def update(dt):
    # Skip updates if paused or game over
    if not game_playing or game_over:
        return
    
    # Platform movement (left/right with clamping)
    vx = 0.0
    if GLUT_KEY_LEFT in _keys:
        vx -= hitbox_platform_speed
    if GLUT_KEY_RIGHT in _keys:
        vx += hitbox_platform_speed
    
    # Apply platform movement
    global hitbox_platform_x
    hitbox_platform_x += vx * dt
    
    # Clamp platform to screen bounds
    min_x = hitbox_platform_half_w + 4
    max_x = W - (hitbox_platform_half_w + 4)
    hitbox_platform_x = max(min_x, min(max_x, hitbox_platform_x))
    
    # Diamond physics (falling with acceleration)
    if not diamond_active:
        spawn_diamond()
    else:
        global diamond_vy, diamond_y
        # Apply acceleration (speed increases over time)
        diamond_vy += diamond_accel * dt
        # Apply velocity
        diamond_y += diamond_vy * dt
        
        # Check collision with platform
        if aabb_intersect(diamond_aabb(), hitbox_platform_aabb()):
            global score
            score += 1
            print(f"Score: {score}")
            spawn_diamond()  # Spawn new diamond
        
        # Check if diamond missed (hit bottom)
        elif diamond_y - diamond_size <= 0:
            trigger_game_over()



# ---------------- OpenGL Setup and Main Loop ----------------
def init_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    # All game elements
    draw_top_buttons()
    draw_hitbox_platform()
    draw_diamond()
    
    glutSwapBuffers()

def idle():
    """Frame limiting and delta time calculation"""
    global last_time
    
    current_time = time.time()
    if last_time is None:
        last_time = current_time
        return
    
    dt = current_time - last_time

    if dt > max_frame_dt:
        dt = max_frame_dt
    
    update(dt)
    last_time = current_time
    glutPostRedisplay()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds!")
    
    init_opengl()
    restart_game()  
    
    # Register callbacks
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutReshapeFunc(reshape)
    glutSpecialFunc(special_key_down)
    glutSpecialUpFunc(special_key_up)
    glutMouseFunc(mouse_click)
    glutKeyboardFunc(keyboard_input)
    
    glutMainLoop()

if __name__ == "__main__":
    main()