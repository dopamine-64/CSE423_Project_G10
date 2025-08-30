from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ------------------ Camera / Grid ------------------
camera_pos = (0, 500, 500)
fovY = 120
tile_size = 100
offset = (11.7 * tile_size)  # half span used by your grid

GRID_LENGTH = 600  # Length of grid lines
rand_var = 423

# ------------------ Player / Arrows ------------------
player_angle = 0    # yaw around Z (A/D rotate this)
arrows = []         # (x, y, z, angle_deg, vz)

# Player base transform (where the keep-top player is placed)
player_base = (-55.0, -650.0, 350.0)
player_tilt = -28.0       # forward tilt (around +X)
player_scale = 1.2
player_angle = 0     # yaw around Z
player_pitch = 0     # new: up/down tilt
# Bow/hands local spot in the player model (between the two arms)
# Arms are around (±20, 15, 100); this is the center between them, a tad forward.
bow = (0.0, 22.0, 105.0)  # (x, y, z) in player's local space before tilt/rotation

# ------------------ UI ------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(0, 0, 0)
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

# ------------------------ CASTLE HELPERS ------------------------
def draw_gatehouse(center_x=0, front_y=250, wall_thickness=30, height=140):
    glPushMatrix()
    glTranslatef(center_x, front_y - wall_thickness / 2 - 1, 120)
    glColor3f(0.6, 0.5, 0.45)
    glScalef(160, 10, 20)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(center_x, front_y - wall_thickness / 2 - 1, 50)
    glColor3f(0.45, 0.35, 0.28)
    glScalef(50, 4, 100)
    glutSolidCube(1)
    glPopMatrix()

    draw_tower(center_x - 80, front_y, base_r=25, height=150)
    draw_tower(center_x + 80, front_y, base_r=25, height=150)

def draw_merlon(w=20, d=30, h=40, color=(0.6, 0.45, 0.35)):
    glPushMatrix()
    glColor3f(*color)
    glScalef(w, d, h)
    glutSolidCube(1)
    glPopMatrix()

def draw_tower(x, y, base_r=45, height=160):
    glPushMatrix()
    glTranslatef(x, y, 0)

    glColor3f(0.7, 0.6, 0.55)
    gluCylinder(gluNewQuadric(), base_r, base_r, height, 18, 4)

    glPushMatrix()
    glTranslatef(0, 0, height)
    glColor3f(0.6, 0.5, 0.45)
    glScalef(base_r * 2.2, base_r * 2.2, 8)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, height + 10)
    segments = 7
    ring_r = base_r * 1.4
    for i in range(segments):
        ang = (2 * math.pi / segments) * i
        px = ring_r * math.cos(ang)
        py = ring_r * math.sin(ang)
        glPushMatrix()
        glTranslatef(px, py, 0)
        draw_merlon(w=10, d=16, h=15, color=(0.55, 0.42, 0.32))
        glPopMatrix()
    glPopMatrix()

    glPopMatrix()

def draw_wall_front(x1, x2, y, thickness=30, height=120):
    length = abs(x2 - x1)
    cx = (x1 + x2) / 2.0
    glPushMatrix()
    glTranslatef(cx, y, height / 2)
    glColor3f(0.854, 0.706, 0.549)
    glScalef(length, thickness, height)
    glutSolidCube(1)
    glPopMatrix()

    step = 60
    count = max(1, int(length / step))
    for i in range(count + 1):
        t = i / count
        x = x1 + t * (x2 - x1)
        glPushMatrix()
        glTranslatef(x, y, height + 10)
        draw_merlon(w=18, d=thickness * 0.8, h=17)
        glPopMatrix()

def draw_wall_back(x1, x2, y, thickness=30, height=120):
    length = abs(x2 - x1)
    cx = (x1 + x2) / 2.0
    glPushMatrix()
    glTranslatef(cx, y, height / 2)
    glColor3f(0.9, 0.8, 0.7)
    glScalef(length, thickness, height)
    glutSolidCube(1)
    glPopMatrix()

    step = 60
    count = max(1, int(length / step))
    for i in range(count + 1):
        t = i / count
        x = x1 + t * (x2 - x1)
        glPushMatrix()
        glTranslatef(x, y, height + 10)
        draw_merlon(w=18, d=thickness * 0.8, h=17)
        glPopMatrix()

def draw_wall_sides(y1, y2, x, thickness=30, height=120):
    length = abs(y2 - y1)
    cy = (y1 + y2) / 2.0
    glPushMatrix()
    glTranslatef(x, cy, height / 2)
    glColor3f(0.9, 0.8, 0.7)
    glScalef(thickness, length, height)
    glutSolidCube(1)
    glPopMatrix()

    step = 60
    count = max(1, int(length / step))
    for i in range(count + 1):
        t = i / count
        y = y1 + t * (y2 - y1)
        glPushMatrix()
        glTranslatef(x, y, height + 10)
        draw_merlon(w=18, d=thickness * 0.8, h=17)
        glPopMatrix()

def draw_keep(x=0, y=0, w=140, d=140, h=180):
    glPushMatrix()
    glTranslatef(x, y, h / 2)
    glColor3f(0.68, 0.62, 0.56)
    glScalef(w, d, h)
    glutSolidCube(1)
    glPopMatrix()

    for sx in (-1, 1):
        for sy in (-1, 1):
            glPushMatrix()
            glTranslatef(x + sx * (w / 2 - 15), y + sy * (d / 2 - 15), h + 15)
            draw_merlon(w=26, d=26, h=32, color=(0.55, 0.44, 0.34))
            glPopMatrix()

def draw_castle():
    half = 250
    t = 30
    h = 120

    glPushMatrix()
    glTranslatef(0, -20, 40)
    glColor3f(0.82, 0.50, 0.40)
    glScalef(2 * half + 60, 2 * half + 60, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    draw_wall_back(-half, half, -half, thickness=t, height=h)
    draw_tower(-half, -half, base_r=45, height=200)
    draw_tower(half, -half, base_r=45, height=200)
    draw_keep(-5, 0, w=140, d=140, h=180)
    draw_wall_sides(-half, half, half, thickness=t, height=h)
    draw_wall_sides(-half, half, -half, thickness=t, height=h)
    draw_wall_front(-half, half, half, thickness=t, height=h)
    draw_gatehouse(center_x=0, front_y=half + 40, wall_thickness=t, height=h + 20)
    draw_tower(-half, half+15, base_r=45, height=190)
    draw_tower(half, half+15, base_r=45, height=190)

# ------------------ Clouds ------------------
cloud_positions = []

def init_clouds(num_clouds):
    global cloud_positions
    cloud_positions = []
    for _ in range(num_clouds):
        x = random.randint(-740, 740)
        y = random.randint(-1500, -100)
        z = random.randint(520, 680)
        cloud_positions.append((x, y, z))

def draw_cloud(x, y, z):
    glColor3f(1, 1, 1)
    for dx, dy, dz in [(0,0,0), (20,0,0), (-20,0,0), (10,10,0), (-10,10,0), (0,5,10)]:
        glPushMatrix()
        glTranslatef(x+dx, y+dy, z+dz)
        glScalef(20, 20, 20)
        glutSolidCube(1)
        glPopMatrix()

def draw_clouds():
    for (x, y, z) in cloud_positions:
        draw_cloud(x, y, z)

# ------------------ Grid ------------------
def draw_grid_and_walls():
    for i in range(23):
        for j in range(23):
            if (i + j) % 2 == 0:
                glColor3f(0.3, 0.6, 0.0)
            else:
                glColor3f(0.13, 0.5, 0.13)
            x = j * tile_size - offset
            y = i * tile_size - offset
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0.0)
            glVertex3f(x + tile_size, y, 0.0)
            glVertex3f(x + tile_size, y + tile_size, 0.0)
            glVertex3f(x, y + tile_size, 0.0)
            glEnd()

    glPushMatrix()
    glTranslatef(-50, -700, 0)
    glScalef(2.0, 2.0, 2.0)
    draw_castle()
    glPopMatrix()

# ------------------ Player ------------------
def draw_player_on_keep():
    glPushMatrix()

    # Base placement
    glTranslatef(*player_base)
    glRotatef(player_tilt, 1, 0, 0)   # tilt forward (look at ground)
    glRotatef(player_angle, 0, 0, 1)      # yaw
    glRotatef(player_pitch, 1, 0, 0)  # up/down tilt
    glScalef(player_scale, player_scale, player_scale)

    # Legs
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.9)
    glTranslatef(-10, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 8, 50, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.2, 0.2, 0.9)
    glTranslatef(10, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 8, 50, 20, 20)
    glPopMatrix()

    # Torso
    glPushMatrix()
    glColor3f(0.5, 0.0, 0.0)
    glTranslatef(0, 0, 60)
    glScalef(0.8, 0.4, 2.0)
    glutSolidCube(35)
    glPopMatrix()

    # Neck
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.7)
    glTranslatef(0, 0, 90)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 3, 20, 20, 20)
    glPopMatrix()

    # Arms (forward/down)
    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslatef(-20, 15, 100)
    glRotatef(-70, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 3, 40, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslatef(20, 15, 100)
    glRotatef(-70, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 3, 40, 20, 20)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(0, 0, 118)
    glutSolidSphere(18, 20, 20)
    glPopMatrix()

    # Simple bow between hands (basic shapes only)
    # A vertical grip + two angled limbs (3 cubes) to suggest a bow
    glPushMatrix()
    glColor3f(0.4, 0.25, 0.1)
    glTranslatef(0, 66, 100)       # center between hands
    glRotatef(180, 0, 0, 1)
    
    # Upper limb
    glPushMatrix()
    glTranslatef(0, 22, 16)
    glRotatef(70, 1, 0, 0)
    glScalef(2, 22, 2)
    glutSolidCube(2)
    glPopMatrix()
    # Lower limb
    glPushMatrix()
    glTranslatef(0, 22, -16)
    glRotatef(-70, 1, 0, 0)
    glScalef(2, 22, 2)
    glutSolidCube(2)
    glPopMatrix()
    glPopMatrix()

    glPopMatrix()

# ---- Compute bow world position (so arrows start from hands) ----
def get_bow_world_pos_and_yaw():
    """
    Returns (x, y, z, yaw_deg) for the bow center between hands,
    applying: scale -> tilt(X) -> yaw(Z) -> translate.
    """
    bx, by, bz = bow
    # apply uniform scale in local
    bx *= player_scale
    by *= player_scale
    bz *= player_scale

    # tilt around +X by player_tilt
    tilt = math.radians(player_tilt)
    c = math.cos(tilt)
    s = math.sin(tilt)
    # Rx(θ): y' = y*cosθ - z*sinθ ; z' = y*sinθ + z*cosθ
    y1 = by * c - bz * s
    z1 = by * s + bz * c
    x1 = bx

    # yaw around Z by player_angle
    yaw = math.radians(player_angle)
    cy = math.cos(yaw)
    sy = math.sin(yaw)
    # Rz(α): x'' = x*cosα - y*sinα ; y'' = x*sinα + y*cosα
    x2 = x1 * cy - y1 * sy
    y2 = x1 * sy + y1 * cy

    # translate to world
    wx = player_base[0] + x2
    wy = player_base[1] + y2
    wz = player_base[2] + z1

    return wx, wy, wz, player_angle, player_pitch

# ------------------ Arrows ------------------
def draw_arrows():
    global arrows
    updated = []
    for (x, y, z, angle_deg, pitch_deg, vz) in arrows:
        speed = 18.0
        rad = math.radians(angle_deg)
        pitch_rad = math.radians(pitch_deg)

        # Move forward using yaw and pitch
        x += speed * math.cos(rad) * math.cos(pitch_rad)
        y += speed * math.sin(rad) * math.cos(pitch_rad)
        z += speed * math.sin(pitch_rad)

        # Drop effect (gravity)
        vz -= 0.35
        z += vz

        # keep a while
        if abs(x) < 4000 and abs(y) < 4000 and z > 0:
            updated.append((x, y, z, angle_deg, pitch_deg, vz))

            # Draw the arrow oriented with yaw and pitched by its vertical velocity
            # Pitch approximation from vz (more negative -> more nose-down)
            pitch_deg = max(-45, min(45, -vz * 2.0))

            glPushMatrix()
            glTranslatef(x, y, z)
            glRotatef(angle_deg - 90, 0, 0, 1)   # yaw so +Y is forward
            glRotatef(0, 0, 0, 1)        # pitch
            glScalef(2.0, 2.0, 2.0)

            # Shaft (thin cube stick)
            glColor3f(0.5, 0.3, 0.1)
            glPushMatrix()
            glScalef(2.0, 30.0, 2.0)             # long along +Y
            glutSolidCube(1)
            glPopMatrix()

            # Arrowhead (cone via cylinder → tip forward)
            glColor3f(0.8, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(0, 16, 0)               # tip at front
            glRotatef(-90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 2.5, 0.0, 7.0, 10, 1)
            glPopMatrix()

            # Simple tail (fletching) as a tiny cube
            glColor3f(0.9, 0.9, 0.9)
            glPushMatrix()
            glTranslatef(0, -15, 0)
            glScalef(3.0, 3.0, 1.0)
            glutSolidCube(1)
            glPopMatrix()

            glPopMatrix()

    arrows = updated

# ------------------ Enemies ------------------
enemies = []   # list of (x, y, z)

def init_enemies(num=5):
    global enemies
    enemies = []
    for _ in range(num):
        spawn_enemy()

def spawn_enemy():
    """Spawn a new enemy randomly in front of the castle on the ground"""
    x = random.randint(-200, 200)   # spread left/right
    y = random.randint(600, 900)    # in front of castle gate
    z = 0                           # ground level
    enemies.append([x, y, z])

def draw_enemy(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)

    # Body
    glColor3f(0.1, 0.6, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glutSolidSphere(20, 20, 20)
    glPopMatrix()

    # Head
    glColor3f(0.0, 0.4, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 50)
    glutSolidSphere(12, 20, 20)
    glPopMatrix()

    # Eyes
    glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(-4, 8, 52)
    glutSolidSphere(3, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(4, 8, 52)
    glutSolidSphere(3, 10, 10)
    glPopMatrix()

    # Arms
    glColor3f(0.1, 0.5, 0.1)
    glPushMatrix()
    glTranslatef(-20, 0, 20)
    gluCylinder(gluNewQuadric(), 3, 3, 25, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(20, 0, 20)
    gluCylinder(gluNewQuadric(), 3, 3, 25, 10, 10)
    glPopMatrix()

    glPopMatrix()

def update_enemies():
    global enemies
    updated = []
    for (x, y, z) in enemies:
        # Move toward castle (negative Y direction)
        y -= 0.3  

        # If reached the castle gate, respawn
        if y <= 10:
            spawn_enemy()
        else:
            updated.append([x, y, z])

    # Ensure always 5 enemies
    while len(updated) < 5:
        spawn_enemy()

    enemies = updated

def draw_enemies():
    for (x, y, z) in enemies:
        draw_enemy(x, y, z)

# ------------------ Fire Line ------------------
fire_particles = []

def init_fire_line(length=400, spacing=20):
    """Create fire particles along a line in front of the castle."""
    global fire_particles
    fire_particles = []
    for i in range(-length//2, length//2 + 1, spacing):
        # x = along the line, y = front of castle, z = ground level
        fire_particles.append([i, -420, 0, random.uniform(10, 20)])  
        # each particle = [x, y, base_z, height]

def draw_fire_line():
    global fire_particles
    for p in fire_particles:
        x, y, base_z, h = p

        # Flicker animation
        flicker = random.uniform(-3, 3)
        flame_height = h + flicker

        # Flicker color
        r = 1.0
        g = random.uniform(0.3, 0.7)
        b = 0.0

        glPushMatrix()
        glTranslatef(x, y+400, base_z)

        # Draw low flame as stacked spheres
        glColor3f(r, g, b)
        glutSolidSphere(6, 10, 10)

        glTranslatef(0, 0, flame_height * 0.5)
        glColor3f(1.0, g + 0.2, 0.0)
        glutSolidSphere(5, 10, 10)

        glTranslatef(0, 0, flame_height * 0.5)
        glColor3f(1.0, 1.0, 0.2)
        glutSolidSphere(3, 10, 10)

        glPopMatrix()

# ------------------ Controls ------------------
def keyboardListener(key, x, y):
    global player_angle, player_pitch
    if key == b'a':
        player_angle += 5
    elif key == b'd':
        player_angle -= 5
    elif key == b'w':
        player_pitch = min(player_pitch + 5, 45)   # look up, clamp
    elif key == b's':
        player_pitch = max(player_pitch - 5, -45)  # look down, clamp

def specialKeyListener(key, x, y):
    global camera_pos
    x0, y0, z0 = camera_pos
    if key == GLUT_KEY_LEFT: x0 -= 10
    if key == GLUT_KEY_RIGHT: x0 += 10
    camera_pos = (x0, y0, z0)

def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Spawn from bow/hands world position, with current yaw,
        # and a small initial upward velocity so it doesn't clip the bow
        bx, by, bz, yaw_deg, pitch_deg = get_bow_world_pos_and_yaw()
        arrows.append((bx, by, bz, yaw_deg+90, pitch_deg, 0.8))

# ------------------ Camera / Display ------------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def idle():
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    
    draw_grid_and_walls()
    draw_clouds()
    draw_player_on_keep()
    draw_arrows()
    update_enemies()
    draw_fire_line()
    draw_enemies()

    draw_text(10, 770, "Big Castle Prototype")
    draw_text(10, 740, f"rand_var: {rand_var}")

    glutSwapBuffers()

# ------------------ Main ------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Castle Defense 3D")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glClearColor(0.5, 0.81, 0.9, 1.0)
    init_clouds(15)
    init_enemies(5)
    init_fire_line(2280, 10)   # fire trench 500 units wide
    glutMainLoop()

if __name__ == "__main__":
    main()
