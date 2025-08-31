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
FIRST_PERSON = False
sky_time = 0.0
sky_speed = 0.002
GRID_LENGTH = 600  # Length of grid lines
PLAYER_SCORE = 0
player_health = 5
GAME_OVER = False
rand_var = 423
DAY_COLOR = (0.5, 0.81, 0.9)
SUNSET_COLOR = (1.0, 0.5, 0.2)
NIGHT_COLOR = (0.05, 0.05, 0.2)
DAWN_COLOR = (1.0, 0.6, 0.4)
CASTLE_HEALTH = 10
GAME_OVER = False
FIRE_LINE_Y = -20  # adjust so it matches your fire line (castle front)


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
kill_count = 0

god_mode = False
god_players = []   # list of {"x","y","z","angle","sweep_dir","ready"}

god_mode_cooldown = 0
god_shooter_index = 0   # 0 or 1 → which god archer shoots next

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
    
    # Torso
    glPushMatrix()
    glColor3f(0.5, 0.0, 0.0)
    glTranslatef(0, 0, 60)
    glScalef(0.8, 0.4, 2.0)
    glutSolidCube(35)
    glPopMatrix()

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
    speed = 35.0

    # Update positions in place
    for i in range(len(arrows)):
        arrows[i][0] += arrows[i][3] * speed  # x += fx * speed
        arrows[i][1] += arrows[i][4] * speed  # y += fy * speed
        arrows[i][2] += arrows[i][5] * speed  # z += fz * speed

    # Remove arrows out of bounds

    arrows[:] = [a for a in arrows if a[2] > -50 and abs(a[0]) < 10000 and abs(a[1]) < 10000]


    # Draw arrows
    for (x, y, z, fx, fy, fz) in arrows:
        # Arrow orientation
        yaw_deg = math.degrees(math.atan2(fy, fx))
        pitch_deg = math.degrees(math.asin(fz))

        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(yaw_deg - 90, 0, 0, 1)
        glRotatef(pitch_deg, 1, 0, 0)
        glScalef(2.0, 2.0, 2.0)

        # Shaft
        glColor3f(0.5, 0.3, 0.1)
        glPushMatrix()
        glScalef(2.0, 30.0, 2.0)
        glutSolidCube(1)
        glPopMatrix()

        # Arrowhead
        glColor3f(0.8, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0, 16, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.5, 0.0, 7.0, 10, 1)
        glPopMatrix()

        # Tail (fletching)
        glColor3f(0.9, 0.9, 0.9)
        glPushMatrix()
        glTranslatef(0, -15, 0)
        glScalef(3.0, 3.0, 1.0)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()
# ------------------ Enemies ------------------
enemies = []   # list of (x, y, z)

def init_enemies(num=5):
    global enemies
    enemies = []
    for _ in range(num):
        spawn_enemy()

def spawn_enemy():
    """Spawn a new enemy randomly in front of the castle on the ground"""
    x = random.randint(-700, 700)   # spread left/right
    y = random.randint(600, 900)    # in front of castle gate
    z = 0                           # ground level
    enemies.append([x, y, z])

def draw_enemy(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)

    # --- Body (bulky, green) ---
    glColor3f(0.05, 0.4, 0.05)
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glutSolidSphere(35, 25, 25)   # big torso
    glPopMatrix()

    # --- Head (bigger, darker green) ---
    glColor3f(0.0, 0.3, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 90)
    glutSolidSphere(22, 20, 20)
    glPopMatrix()

    # --- Eyes (red, glowing) ---
    glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(-7, 20, 95)
    glutSolidSphere(4, 12, 12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(7, 20, 95)
    glutSolidSphere(4, 12, 12)
    glPopMatrix()

    # --- Horns (white) ---
    glColor3f(1, 1, 1)
    glPushMatrix()
    glTranslatef(-10, -5, 105)
    glRotatef(-40, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2, 0.5, 20, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(10, -5, 105)
    glRotatef(-40, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2, 0.5, 20, 10, 10)
    glPopMatrix()

    # --- Mouth (black) ---
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 15, 90)
    glScalef(10, 5, 5)
    glutSolidCube(1)
    glPopMatrix()

    # --- Teeth (spikes) ---
    glColor3f(1, 1, 1)
    for dx in (-4, 0, 4):
        glPushMatrix()
        glTranslatef(dx, 23, 87)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 1.2, 0.2, 6, 6, 6)
        glPopMatrix()

    # --- Spikes on back ---
    glColor3f(0.2, 0.2, 0.2)
    for i in range(5):
        glPushMatrix()
        glTranslatef(0, -25, 60 + i * 15)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.5, 0.0, 12, 10, 10)
        glPopMatrix()

    glPopMatrix()

def update_enemies():
    global enemies, CASTLE_HEALTH, GAME_OVER

    if GAME_OVER:
        return

    updated = []
    for (x, y, z) in enemies:
        y -= 0.3  # Enemy movement speed

        # If enemy reaches fire line
        if y <= FIRE_LINE_Y:
            CASTLE_HEALTH -= 1
            if CASTLE_HEALTH <= 0:
                CASTLE_HEALTH = 0
                GAME_OVER = True
            else:
                spawn_enemy()  # Respawn a new one
        else:
            updated.append([x, y, z])

    # Keep enemy count constant
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

def check_arrow_enemy_collision():
    global arrows, enemies, kill_count
    updated_arrows = []

    for i in range(len(arrows)):
        ax, ay, az, angle_deg, pitch_deg, vz = arrows[i]

        # Compute previous position
        speed = 18.0
        rad = math.radians(angle_deg)
        pitch_rad = math.radians(pitch_deg)
        prev_x = ax - speed * math.cos(rad) * math.cos(pitch_rad)
        prev_y = ay - speed * math.sin(rad) * math.cos(pitch_rad)
        prev_z = az - speed * math.sin(pitch_rad)

        hit = False
        for enemy in enemies:
            ex, ey, ez = enemy
            # Treat enemy as sphere at center + radius
            cx, cy, cz = ex, ey, ez + 30
            r = 40

            # Vector from previous to current arrow pos
            vx, vy, vz_arrow = ax - prev_x, ay - prev_y, az - prev_z
            # Vector from previous arrow pos to enemy center
            wx, wy, wz_arrow = cx - prev_x, cy - prev_y, cz - prev_z

            # Project w onto v to find closest point along line
            v_len2 = vx*vx + vy*vy + vz_arrow*vz_arrow
            if v_len2 == 0:
                closest_dist2 = (wx*wx + wy*wy + wz_arrow*wz_arrow)
            else:
                t = max(0, min(1, (wx*vx + wy*vy + wz_arrow*vz_arrow)/v_len2))
                closest_x = prev_x + t*vx
                closest_y = prev_y + t*vy
                closest_z = prev_z + t*vz_arrow
                dx = cx - closest_x
                dy = cy - closest_y
                dz = cz - closest_z
                closest_dist2 = dx*dx + dy*dy + dz*dz

            if closest_dist2 < r*r:
                # Arrow hit enemy
                kill_count += 1
                enemies.remove(enemy)
                spawn_enemy()
                hit = True
                break

        if not hit:
            updated_arrows.append((ax, ay, az, angle_deg, pitch_deg, vz))

    arrows = updated_arrows

# --- draw only the geometry, no transforms here ---
def draw_player_model():
    # Torso
    glPushMatrix()
    glColor3f(0.5, 0.0, 0.0)
    glTranslatef(0, 0, 60)
    glScalef(0.8, 0.4, 2.0)
    glutSolidCube(35)
    glPopMatrix()

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

    # Neck
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.7)
    glTranslatef(0, 0, 90)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 3, 20, 20, 20)
    glPopMatrix()

    # Arms
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

    # Bow (simple)
    glPushMatrix()
    glColor3f(0.4, 0.25, 0.1)
    glTranslatef(0, 66, 100)
    glRotatef(180, 0, 0, 1)
    glPushMatrix()
    glTranslatef(0, 22, 16); glRotatef(70, 1, 0, 0); glScalef(2, 22, 2); glutSolidCube(2); glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 22, -16); glRotatef(-70, 1, 0, 0); glScalef(2, 22, 2); glutSolidCube(2); glPopMatrix()
    glPopMatrix()

def draw_god_players():
    if not god_mode: return
    for gp in god_players:
        glPushMatrix()
        glTranslatef(*gp["base"])
        glRotatef(player_tilt, 1, 0, 0)   # same tilt
        glRotatef(gp["angle"], 0, 0, 1)
        glRotatef(gp["pitch"], 1, 0, 0)
        glScalef(0.9, 0.9, 0.9)
        draw_player_model()
        glPopMatrix()

def get_bow_world_pos_and_forward():
    """
    Returns:
        (bx, by, bz, fx, fy, fz)
        bow world coordinates and normalized forward unit vector
    """
    # Local bow position scaled
    bx, by, bz = bow
    bx *= player_scale
    by *= player_scale
    bz *= player_scale

    # Apply tilt (X-axis)
    tilt = math.radians(player_tilt)
    c, s = math.cos(tilt), math.sin(tilt)
    y1 = by * c - bz * s
    z1 = by * s + bz * c
    x1 = bx

    # Apply yaw (Z-axis)
    yaw = math.radians(player_angle)
    cy, sy = math.cos(yaw), math.sin(yaw)
    x2 = x1 * cy - y1 * sy
    y2 = x1 * sy + y1 * cy
    wx = player_base[0] + x2
    wy = player_base[1] + y2
    wz = player_base[2] + z1

    # Forward vector in local space (+Y)
    fx, fy, fz = 0, 1, 0

    # Tilt
    fy_tilt = fy * c - fz * s
    fz_tilt = fy * s + fz * c
    fx_tilt = fx

    # Yaw
    fx_world = fx_tilt * cy - fy_tilt * sy
    fy_world = fx_tilt * sy + fy_tilt * cy
    fz_world = fz_tilt

    # Normalize
    length = math.sqrt(fx_world**2 + fy_world**2 + fz_world**2)
    fx_world /= length
    fy_world /= length
    fz_world /= length

    return wx, wy, wz, fx_world, fy_world, fz_world

def god_mode_behavior():
    global god_mode_cooldown, god_shooter_index

    if not god_mode or not enemies:
        return

    # slow rotation
    for gp in god_players:
        gp["angle"] = (gp["angle"] + 1) % 360   # sweep in 180° arc

    if god_mode_cooldown > 0:
        god_mode_cooldown -= 1
        return

    shooter = god_players[god_shooter_index]
    sx, sy, sz = shooter["base"]

    target_enemy = None
    min_dist = float("inf")
    for e in enemies:
        dx, dy = e[0] - sx, e[1] - sy
        dist = math.hypot(dx, dy)
        angle_to_enemy = math.degrees(math.atan2(dy, dx)) % 360
        diff = abs((shooter["angle"] % 360) - angle_to_enemy)
        if diff < 5 and dist < min_dist:
            min_dist = dist
            target_enemy = e

    if target_enemy:
        bx, by, bz, yaw, pitch = get_bow_world_pos(
            base=shooter["base"], yaw_deg=shooter["angle"], pitch_deg=shooter["pitch"], scale=0.9
        )
        arrows.append((bx, by, bz, yaw, pitch, 0.8))
        god_mode_cooldown = 30
        god_shooter_index = (god_shooter_index + 1) % len(god_players)
        
# ------------------ Controls ------------------
def keyboardListener(key, x, y):
    global player_angle, player_pitch
    global god_mode, god_players
    global GAME_OVER, player_score, player_health
    global arrows, enemies

    # Debug print to see which key is pressed
    print(f"Key pressed: {key}")

    # ESC → exit
    if key == b'\x1b':
        glutLeaveMainLoop()

    # Restart / reset
    elif key in (b'r', b'R'):
        if GAME_OVER:
            player_score = 0
            player_health = 5
            GAME_OVER = False
            arrows = []
            enemies = []
            init_enemies(5)
        else:
            restart_game()

    # Movement
    elif key == b'a':
        player_angle += 5
    elif key == b'd':
        player_angle -= 5
    elif key == b'w':
        player_pitch = min(player_pitch + 5, 45)
    elif key == b's':
        player_pitch = max(player_pitch - 5, -45)

    # God mode toggle
    elif key == b'g':  # only lowercase 'g'
        god_mode = not god_mode
        print("God Mode:", god_mode)  # debug
        if god_mode:
            god_players = [
                {"base": (-550.0, -200.0, 380.0), "angle": 0, "pitch": 0},
                {"base": (450.0, -200.0, 380.0), "angle": 0, "pitch": 0}
            ]
        else:
            god_players = []


def specialKeyListener(key, x, y):
    global camera_pos
    x0, y0, z0 = camera_pos
    if key == GLUT_KEY_LEFT: x0 -= 10
    if key == GLUT_KEY_RIGHT: x0 += 10
    camera_pos = (x0, y0, z0)

def mouseListener(button, state, x, y):
    global FIRST_PERSON
    
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        FIRST_PERSON = not FIRST_PERSON
        glutPostRedisplay()
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bx, by, bz, fx, fy, fz = get_bow_world_pos_and_forward()
        # Append arrow: position + normalized forward vector
        arrows.append([bx, by, bz, fx, fy, fz])
def restart_game():
    global CASTLE_HEALTH, GAME_OVER, enemies, arrows, kill_count
    CASTLE_HEALTH = 10
    GAME_OVER = False
    enemies = []
    arrows = []
    kill_count = 0
    init_enemies(5)  # Re-spawn enemies

# ------------------ Camera / Display ------------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1000/800, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if FIRST_PERSON:
        # Get bow position and forward vector
        bx, by, bz, fx, fy, fz = get_bow_world_pos_and_forward()

        # Adjust camera: slightly behind & above the bow
        cam_back = 50      # distance behind bow
        cam_up   = 200      # distance above bow
        eye_x = bx - cam_back * fx
        eye_y = by - cam_back * fy
        eye_z = bz + cam_up

        # Look along bow
        center_x = bx + 1000 * fx
        center_y = by + 1000 * fy
        center_z = bz + 1000 * fz

        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0, 0, 1)
    else:
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)
def idle():
    global sky_time   # <--- add this line!
    sky_time += sky_speed
    if sky_time > 1.0:
        sky_time -= 1.0
    glutPostRedisplay()

def showScreen():
    # Dynamic sky color
    r = 0.5 + 0.3 * math.sin(2 * math.pi * sky_time)
    g = 0.8 + 0.1 * math.sin(2 * math.pi * sky_time)
    b = 0.9 + 0.1 * math.sin(2 * math.pi * sky_time)
    glClearColor(r, g, b, 1.0)

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

    draw_text(10, 760, "Big Castle Prototype")
    draw_text(10, 700, f"rand_var: {rand_var}")
    draw_text(10, 720, f"Score: {PLAYER_SCORE}")       
    draw_text(10, 740, f"Castle Health: {CASTLE_HEALTH}")

    if GAME_OVER:
        draw_text(400, 400, "GAME OVER! Press R to Restart")


    glutSwapBuffers()

# ------------------ Main ------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Castle Defense 3D")
    glEnable(GL_DEPTH_TEST)
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
