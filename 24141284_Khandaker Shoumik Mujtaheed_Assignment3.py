import math
import time
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Camera-related variables
camera_angle = 0.0
camera_radius = 200.0
camera_height = 500.0
fovY = 120
is_first_person = False 

# Player variables
player_pos = (0, 0, 0)
player_angle = 270.0

# Enemy variables
enemies = []
enemy_animation_start = time.time()
enemy_speed = 0.05

# Bullet variables
bullets = []
bullet_speed = 20.0  

# Game state variables
player_health = 5
max_health = 5
score = 0
bullets_missed = 0
max_missed_bullets = 10
game_over = False
game_over_message = ""

# Cheat mode variables
is_cheating = False
cheat_vision = False
cheat_rotation_speed = 25.0  
current_target_index = 0  
target_locked = False  

def calculate_3rd_person_camera():
    angle_rad = math.radians(camera_angle)
    x = camera_radius * math.cos(angle_rad)
    y = camera_radius * math.sin(angle_rad)
    z = camera_height
    return (x, y, z)

def calculate_1st_person_camera():

    px, py, pz = player_pos
    camera_offset_distance = 40 
    camera_height_offset = 35 
    
    # Calculate position behind player based on player angle
    angle_rad = math.radians(player_angle - 90) 
    camera_x = px - camera_offset_distance * math.cos(angle_rad) 
    camera_y = py - camera_offset_distance * math.sin(angle_rad) 
    camera_z = pz + camera_height_offset 
    
    return (camera_x, camera_y, camera_z)

def calculate_angle_to_target(target_pos):
   
    px, py, pz = player_pos
    tx, ty, tz = target_pos
    
    # Angle from player to target
    dx = tx - px
    dy = ty - py
    
    # Convert to angle 
    target_angle = math.degrees(math.atan2(dy, dx)) + 90
    
    if target_angle < 0:
        target_angle += 360
    elif target_angle >= 360:
        target_angle -= 360
        
    return target_angle

def get_closest_enemy():
    
    if not enemies:
        return None
        
    px, py, pz = player_pos
    closest_enemy = None
    closest_distance = float('inf')
    
    for enemy in enemies:
        ex, ey, ez = enemy['pos']
        distance = math.sqrt((px - ex)**2 + (py - ey)**2)
        
        if distance < closest_distance:
            closest_distance = distance
            closest_enemy = enemy
            
    return closest_enemy

def angle_difference(angle1, angle2):
    
    diff = angle2 - angle1
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    return diff

def spawn_targeted_bullet(target_pos):
    
    global bullets
    
    if game_over:
        return
        
    # Gun tip position
    px, py, pz = player_pos
    gun_offset_distance = 30
    
    # Direction to target
    tx, ty, tz = target_pos
    dx = tx - px
    dy = ty - py
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance > 0:
        # Normalize direction
        dx /= distance
        dy /= distance
        
        gun_tip_x = px + gun_offset_distance * dx
        gun_tip_y = py + gun_offset_distance * dy
        gun_tip_z = pz + 35
        
        bullets.append({
            'pos': [gun_tip_x, gun_tip_y, gun_tip_z],
            'dir': [dx, dy, 0]
        })

def update_cheat_mode():
   
    global player_angle, target_locked
    
    if not is_cheating:
        return
    
    # Continuous rotation of player in cheat mode 
    player_angle += cheat_rotation_speed
    if player_angle >= 360:
        player_angle -= 360
    elif player_angle < 0:
        player_angle += 360
    
    # Reset target if no enemies remaining 
    if not enemies:
        target_locked = False
        return
    
    target_enemy = get_closest_enemy()
    
    if target_enemy is None:
        target_locked = False
        return
    
    target_pos = target_enemy['pos']
    required_angle = calculate_angle_to_target(target_pos)
    
    # Calculate how much we need to rotate
    angle_diff = angle_difference(player_angle, required_angle)
    
    # If we're close enough to the target angle, shoot immediately
    if abs(angle_diff) < 8:  
        if not target_locked:
            spawn_targeted_bullet(target_pos)
            target_locked = True
    else:
        target_locked = False


def draw_player():
   
    global player_health, game_over, game_over_message
    
    if game_over:
        # Player lies down when game over
        glPushMatrix()
        x, y, z = player_pos
        glTranslatef(x, y, z + 10)
        glRotatef(player_angle, 0, 0, 1)
        glRotatef(90, 1, 0, 0) 
        
        # Torso
        glPushMatrix()
        glTranslatef(0, 0, 5)
        glColor3f(0.0, 0.0, 1.0)
        glScalef(0.8, 0.5, 0.8)
        glutSolidCube(25)
        glPopMatrix()
        glPopMatrix()
        return
    
    glPushMatrix()
    x, y, z = player_pos
    glTranslatef(x, y, z + 25)
    glRotatef(player_angle, 0, 0, 1)
    
    # Torso 
    glPushMatrix()
    glTranslatef(0, 0, 5)
    glColor3f(0.0, 0.0, 1.0)
    glScalef(0.8, 0.5, 0.8)
    glutSolidCube(25)
    glPopMatrix()
    
    # Head 
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glColor3f(1.0, 1.0, 1.0)
    gluSphere(gluNewQuadric(), 8, 10, 10)
    glPopMatrix()
    
    # Left arm 
    glPushMatrix()
    glTranslatef(-15, -6, 12)
    glRotatef(90, 1, 0, 0)
    glColor3f(1.0, 1.0, 1.0)
    gluCylinder(gluNewQuadric(), 4, 4, 20, 8, 8)
    glPopMatrix()
    
    # Right arm 
    glPushMatrix()
    glTranslatef(15, -6, 12)
    glRotatef(90, 1, 0, 0)
    glColor3f(1.0, 1.0, 1.0)
    gluCylinder(gluNewQuadric(), 4, 4, 20, 8, 8)
    glPopMatrix()
    
    # Gun 
    glPushMatrix()
    glTranslatef(0, -12, 12)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.3, 0.3, 0.3)
    gluCylinder(gluNewQuadric(), 5, 5, 30, 10, 10)
    glPopMatrix()
    
    # Left leg 
    glPushMatrix()
    glTranslatef(-8, 0, -20)
    glColor3f(0, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 18, 8, 8)
    glPopMatrix()
    
    # Right leg 
    glPushMatrix()
    glTranslatef(8, 0, -20)
    glColor3f(0, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 18, 8, 8)
    glPopMatrix()
    
    glPopMatrix()

def initialize_enemies():
    global enemies
    enemies = []
    for i in range(5):
        x = random.uniform(-200, 200)
        y = random.uniform(-200, 200)
        while -50 < x < 50 and -50 < y < 50:
            x = random.uniform(-200, 200)
            y = random.uniform(-200, 200)
        enemies.append({
            'pos': [x, y, 0],
            'animation_offset': i * 0.2
        })

def move_enemies():
   
    global player_health, game_over, game_over_message
    
    if game_over:
        return
        
    px, py, pz = player_pos
    
    for enemy in enemies:
        ex, ey, ez = enemy['pos']
        
        # Calculate direction toward player
        dx = px - ex
        dy = py - ey
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize direction and apply speed
            dx = (dx / distance) * enemy_speed
            dy = (dy / distance) * enemy_speed
            
            # Update enemy position
            enemy['pos'][0] += dx
            enemy['pos'][1] += dy
        
        # Check collision with player
        player_distance = math.sqrt((px - enemy['pos'][0])**2 + (py - enemy['pos'][1])**2)
        if player_distance < 30: # Collision radius
            player_health -= 1
            
            # Move enemy away after hit to prevent multiple hits
            enemy['pos'][0] = random.uniform(-200, 200)
            enemy['pos'][1] = random.uniform(-200, 200)
            while -50 < enemy['pos'][0] < 50 and -50 < enemy['pos'][1] < 50:
                enemy['pos'][0] = random.uniform(-200, 200)
                enemy['pos'][1] = random.uniform(-200, 200)
            
            if player_health <= 0:
                game_over = True
                game_over_message = "GAME OVER - No Health Remaining!"
                break

def draw_enemy(enemy_data):
    
    glPushMatrix()
    x, y, z = enemy_data['pos']
    glTranslatef(x, y, z + 25)
    
    # Get current scale for pulsating animation
    current_time = time.time()
    elapsed = (current_time - enemy_animation_start + enemy_data['animation_offset']) * 2.0
    scale = 0.85 + 0.15 * math.sin(2 * math.pi * elapsed)
    glScalef(scale, scale, scale)
    
    # Enemy body
    glPushMatrix()
    glTranslatef(0, 0, 0)
    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 20, 10, 10)
    glPopMatrix()
    
    # Enemy head
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()
    
    glPopMatrix()

def draw_enemies():
    for enemy in enemies:
        draw_enemy(enemy)

def spawn_bullet():

    global bullets
    
    if game_over:
        return
        
    # Gun tip position
    px, py, pz = player_pos
    gun_offset_distance = 30
    
    angle_rad = math.radians(player_angle - 90)
    gun_tip_x = px + gun_offset_distance * math.cos(angle_rad)
    gun_tip_y = py + gun_offset_distance * math.sin(angle_rad)
    gun_tip_z = pz + 35
    
    # Direction vector
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    
    bullets.append({
        'pos': [gun_tip_x, gun_tip_y, gun_tip_z],
        'dir': [dx, dy, 0]
    })

def spawn_new_enemy():

    global enemies, target_locked
    
    x = random.uniform(-200, 200)
    y = random.uniform(-200, 200)
    
    while -50 < x < 50 and -50 < y < 50:
        x = random.uniform(-200, 200)
        y = random.uniform(-200, 200)
    
    enemies.append({
        'pos': [x, y, 0],
        'animation_offset': random.random() * 2.0
    })
    
    # Reset target lock when new enemy spawns to enable immediate targeting
    target_locked = False


def update_bullets():
   
    global bullets, enemies, score, bullets_missed, game_over, game_over_message, target_locked
    
    if game_over:
        return
    
    bullets_to_keep = []
    
    for bullet in bullets:

        bullet['pos'][0] += bullet['dir'][0] * bullet_speed
        bullet['pos'][1] += bullet['dir'][1] * bullet_speed
        
        # Check if bullet is out of bounds
        if (abs(bullet['pos'][0]) > 320 or abs(bullet['pos'][1]) > 320):
            bullets_missed += 1
            
            # Game over condition for missed bullets
            if bullets_missed >= max_missed_bullets:
                game_over = True
                game_over_message = "GAME OVER - Too Many Missed Bullets!"
            continue
        
        # Check collision with enemies
        bullet_hit = False
        for enemy in enemies[:]:
            ex, ey, ez = enemy['pos']
            bx, by, bz = bullet['pos']
            
            distance = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - (ez + 25))**2)
            
            if distance < 25:
                enemies.remove(enemy)
                spawn_new_enemy()
                score += 1 
                bullet_hit = True
                target_locked = False  
                break
        
        if not bullet_hit:
            bullets_to_keep.append(bullet)
    
    bullets = bullets_to_keep


def draw_bullets():
  
    glColor3f(1.0, 0.0, 0.0)
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        glutSolidCube(6)
        glPopMatrix()

def reset_game():
    
    global player_pos, player_angle, player_health, score, bullets_missed, game_over, game_over_message, bullets
    global is_cheating, cheat_vision, current_target_index, target_locked
    player_pos = (0, 0, 0)
    player_angle = 270.0
    player_health = max_health
    score = 0
    bullets_missed = 0
    game_over = False
    game_over_message = ""
    bullets = []
    is_cheating = False
    cheat_vision = False
    current_target_index = 0
    target_locked = False
    initialize_enemies()

def draw_tile(color):
   
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_QUADS)
    glVertex3f(-30, -30, 0)
    glVertex3f(30, -30, 0)
    glVertex3f(30, 30, 0)
    glVertex3f(-30, 30, 0)
    glEnd()

def draw_border_wall(color, wall_type):
   
    glColor3f(color[0], color[1], color[2])
    
    if wall_type == 'horizontal':
        glBegin(GL_QUADS)
        glVertex3f(-300, -2, 0)
        glVertex3f(300, -2, 0)
        glVertex3f(300, -2, 50)
        glVertex3f(-300, -2, 50)
        
        glVertex3f(-300, 2, 0)
        glVertex3f(300, 2, 0)
        glVertex3f(300, 2, 50)
        glVertex3f(-300, 2, 50)
        
        glVertex3f(-300, -2, 0)
        glVertex3f(-300, 2, 0)
        glVertex3f(-300, 2, 50)
        glVertex3f(-300, -2, 50)
        
        glVertex3f(300, -2, 0)
        glVertex3f(300, 2, 0)
        glVertex3f(300, 2, 50)
        glVertex3f(300, -2, 50)
        
        glVertex3f(-300, -2, 50)
        glVertex3f(300, -2, 50)
        glVertex3f(300, 2, 50)
        glVertex3f(-300, 2, 50)
        glEnd()
        
    elif wall_type == 'vertical':
        glBegin(GL_QUADS)
        glVertex3f(-2, -300, 0)
        glVertex3f(2, -300, 0)
        glVertex3f(2, -300, 50)
        glVertex3f(-2, -300, 50)
        
        glVertex3f(-2, 300, 0)
        glVertex3f(2, 300, 0)
        glVertex3f(2, 300, 50)
        glVertex3f(-2, 300, 50)
        
        glVertex3f(-2, -300, 0)
        glVertex3f(-2, 300, 0)
        glVertex3f(-2, 300, 50)
        glVertex3f(-2, -300, 50)
        
        glVertex3f(2, -300, 0)
        glVertex3f(2, 300, 0)
        glVertex3f(2, 300, 50)
        glVertex3f(2, -300, 50)
        
        glVertex3f(-2, -300, 50)
        glVertex3f(2, -300, 50)
        glVertex3f(2, 300, 50)
        glVertex3f(-2, 300, 50)
        glEnd()

def draw_grid_floor():
   
    white_color = (1.0, 1.0, 1.0)
    pink_color = (1.0, 0.75, 0.8)
    wall_colors = [
        (1.0, 0.0, 0.0), # Red wall (North)
        (0.0, 1.0, 0.0), # Green wall (East)
        (0.0, 0.0, 1.0), # Blue wall (South)
        (1.0, 1.0, 0.0) # Yellow wall (West)
    ]
    
    # 10x10 grid 
    for row in range(10):
        for col in range(10):
            glPushMatrix()
            x = (col - 4.5) * 60
            y = (row - 4.5) * 60
            glTranslatef(x, y, 0)
            
            if (row + col) % 2 == 0:
                draw_tile(white_color)
            else:
                draw_tile(pink_color)
            glPopMatrix()
    
    # Border walls
    wall_data = [
        (0, 302, 0, 'horizontal', 0),
        (302, 0, 0, 'vertical', 1),
        (0, -302, 0, 'horizontal', 2),
        (-302, 0, 0, 'vertical', 3)
    ]
    
    for x, y, z, wall_type, color_idx in wall_data:
        glPushMatrix()
        glTranslatef(x, y, z)
        draw_border_wall(wall_colors[color_idx], wall_type)
        glPopMatrix()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
   
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def setupCamera():
   
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if is_first_person or cheat_vision:
        camera_pos = calculate_1st_person_camera()
        x, y, z = camera_pos
        
        px, py, pz = player_pos
        angle_rad = math.radians(player_angle - 90)
        target_x = px + 100 * math.cos(angle_rad) 
        target_y = py + 100 * math.sin(angle_rad)
        target_z = pz + 25 
        
        gluLookAt(x, y, z, # Camera position (behind player)
                  target_x, target_y, target_z, # Look-at target (ahead of player)
                  0, 0, 1) # Up vector (z-axis)
    else:
        camera_pos = calculate_3rd_person_camera()
        x, y, z = camera_pos
        gluLookAt(x, y, z, # Camera position
                  0, 0, 0, # Look-at target (center of grid)
                  0, 0, 1) # Up vector (z-axis)

def keyboardListener(key, x, y):
    
    global player_pos, player_angle, is_cheating, cheat_vision
    
    if game_over and key != b'r':
        return # Only allow reset when game over
    
    if key == b'w':
        angle_rad = math.radians(player_angle - 90)
        move_x = 20 * math.cos(angle_rad)
        move_y = 20 * math.sin(angle_rad)
        new_x = player_pos[0] + move_x
        new_y = player_pos[1] + move_y
        if -285 <= new_x <= 285 and -285 <= new_y <= 285:
            player_pos = (new_x, new_y, player_pos[2])
            
    elif key == b's':
        angle_rad = math.radians(player_angle - 90)
        move_x = -20 * math.cos(angle_rad)
        move_y = -20 * math.sin(angle_rad)
        new_x = player_pos[0] + move_x
        new_y = player_pos[1] + move_y
        if -285 <= new_x <= 285 and -285 <= new_y <= 285:
            player_pos = (new_x, new_y, player_pos[2])
            
    elif key == b'a' and not is_cheating: # Only allow manual rotation when not cheating
        player_angle += 15.0
        if player_angle >= 360.0:
            player_angle -= 360.0
            
    elif key == b'd' and not is_cheating: # Only allow manual rotation when not cheating
        player_angle -= 15.0
        if player_angle < 0.0:
            player_angle += 360.0
    
    elif key == b'c': # Toggle cheat mode
        is_cheating = not is_cheating
        print(f"Cheat mode: {'ON' if is_cheating else 'OFF'}")
        
    elif key == b'v': # Toggle cheat vision 
        if is_cheating:
            cheat_vision = not cheat_vision
            print(f"Cheat vision: {'ON' if cheat_vision else 'OFF'}")
        else:
            print("Cheat vision only available in cheat mode!")
            
    elif key == b'r':
        reset_game()

def specialKeyListener(key, x, y):
   
    global camera_angle, camera_height
    
    # Arrow keys only work in third person mode and not in cheat vision
    if not is_first_person and not cheat_vision:
        if key == GLUT_KEY_UP:
            camera_height += 50
        elif key == GLUT_KEY_DOWN:
            camera_height -= 50
        elif key == GLUT_KEY_LEFT:
            camera_angle += 5.0
            if camera_angle >= 360.0:
                camera_angle -= 360.0
        elif key == GLUT_KEY_RIGHT:
            camera_angle -= 5.0
            if camera_angle < 0.0:
                camera_angle += 360.0

def mouseListener(button, state, x, y):
   
    global is_first_person
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not is_cheating: # Manual firing when not cheating
            spawn_bullet()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not cheat_vision: 
            is_first_person = not is_first_person
            print(f"Camera mode: {'First Person' if is_first_person else 'Third Person'}")

def idle():
   
    if not game_over:
        update_cheat_mode() 
        move_enemies()
        update_bullets()
    glutPostRedisplay()

def showScreen():
   
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    draw_grid_floor()
    
    # Only draw player in third person mode (don't draw in first person or cheat vision)
    if not is_first_person and not cheat_vision:
        draw_player()
    
    draw_enemies()
    draw_bullets()
    
    # Display game information
    cheat_status = "ON" if is_cheating else "OFF"
    
    draw_text(10, 770, "Bullet Frenzy")
    draw_text(10, 740, f"Health: {player_health}/{max_health} | Score: {score}")
    draw_text(10, 710, f"Bullets Missed: {bullets_missed}/{max_missed_bullets} | Cheat: {cheat_status}")
    
    if game_over:
        draw_text(300, 400, game_over_message, GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(10, 650, f"Final Score: {score}", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(10, 600, "Press 'R' to Restart", GLUT_BITMAP_TIMES_ROMAN_24)

    glutSwapBuffers()

def main():
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy - 3D Game")
    initialize_enemies()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
