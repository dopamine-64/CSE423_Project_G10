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
    """Simple gate in the front wall with two flanking mini-towers."""

    # Bridge/hoarding above gate
    glPushMatrix()
    glTranslatef(center_x, front_y - wall_thickness / 2 - 1, 120)
    glColor3f(0.6, 0.5, 0.45)
    glScalef(160, 10, 20)
    glutSolidCube(1)
    glPopMatrix()

    # Gate arch “opening” (visual panel)
    glPushMatrix()
    glTranslatef(center_x, front_y - wall_thickness / 2 - 1, 50)
    glColor3f(0.45, 0.35, 0.28)   # darker panel to imply opening
    glScalef(50, 4, 100)
    glutSolidCube(1)
    glPopMatrix()

    # Two mini-towers flanking the gate
    draw_tower(center_x - 80, front_y, base_r=25, height=150)
    draw_tower(center_x + 80, front_y, base_r=25, height=150)


def draw_merlon(w=20, d=30, h=40, color=(0.6, 0.45, 0.35)):
    """A single crenellation block."""
    glPushMatrix()
    glColor3f(*color)
    glScalef(w, d, h)
    glutSolidCube(1)
    glPopMatrix()


def draw_tower(x, y, base_r=45, height=160):
    """Round corner tower with a ring of merlons on top."""
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Tower shaft
    glColor3f(0.7, 0.6, 0.55)
    gluCylinder(gluNewQuadric(), base_r, base_r, height, 18, 4)

    # Cap (flat)
    glPushMatrix()
    glTranslatef(0, 0, height)
    glColor3f(0.6, 0.5, 0.45)
    glScalef(base_r * 2.2, base_r * 2.2, 8)
    glutSolidCube(1)
    glPopMatrix()

    # Merlons around the top
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
    """Straight wall along X with crenellations."""
    length = abs(x2 - x1)
    cx = (x1 + x2) / 2.0

    # Wall body
    glPushMatrix()
    glTranslatef(cx, y, height / 2)
    glColor3f(0.854, 0.706, 0.549)
    glScalef(length, thickness, height)
    glutSolidCube(1)
    glPopMatrix()

    # Crenellations on top
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
    """Straight wall along X with crenellations."""
    length = abs(x2 - x1)
    cx = (x1 + x2) / 2.0

    # Wall body
    glPushMatrix()
    glTranslatef(cx, y, height / 2)
    glColor3f(0.9, 0.8, 0.7)
    glScalef(length, thickness, height)
    glutSolidCube(1)
    glPopMatrix()

    # Crenellations on top
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
    """Straight wall along Y with crenellations."""
    length = abs(y2 - y1)
    cy = (y1 + y2) / 2.0

    # Wall body
    glPushMatrix()
    glTranslatef(x, cy, height / 2)
    glColor3f(0.9, 0.8, 0.7)
    glScalef(thickness, length, height)
    glutSolidCube(1)
    glPopMatrix()

    # Crenellations on top
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
    """Central square keep with four corner merlons."""
    glPushMatrix()
    glTranslatef(x, y, h / 2)
    glColor3f(0.68, 0.62, 0.56)
    glScalef(w, d, h)
    glutSolidCube(1)
    glPopMatrix()

    # Corner merlons on the keep roof
    for sx in (-1, 1):
        for sy in (-1, 1):
            glPushMatrix()
            glTranslatef(x + sx * (w / 2 - 15), y + sy * (d / 2 - 15), h + 15)
            draw_merlon(w=26, d=26, h=32, color=(0.55, 0.44, 0.34))
            glPopMatrix()


def draw_castle():
    """Square castle with walls, towers, gatehouse, keep."""
    half = 250
    t = 30
    h = 120

    # Ground pad
    glPushMatrix()
    glTranslatef(0, -20, 40)
    glColor3f(0.82, 0.50, 0.40)
    glScalef(2 * half + 60, 2 * half + 60, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    # Walls
    draw_wall_back(-half, half, -half, thickness=t, height=h)  # back
    
    # Towers (Back)
    draw_tower(-half, -half, base_r=45, height=200)
    draw_tower(half, -half, base_r=45, height=200)
    
    # Keep
    draw_keep(-5, 0, w=140, d=140, h=180)
    
    # Walls
    draw_wall_sides(-half, half, half, thickness=t, height=h)   # right
    draw_wall_sides(-half, half, -half, thickness=t, height=h)  # left
    draw_wall_front(-half, half, half, thickness=t, height=h)   # front

    # Gatehouse
    draw_gatehouse(center_x=0, front_y=half + 40, wall_thickness=t, height=h + 20)

    # Towers (Front)
    draw_tower(-half, half+15, base_r=45, height=190)
    draw_tower(half, half+15, base_r=45, height=190)

# ------------------ Clouds ------------------
cloud_positions = []  # store cloud positions

def init_clouds(num_clouds):
    global cloud_positions
    cloud_positions = []
    
    for _ in range(num_clouds):
        # Generate random coordinates within a range
        x = random.randint(-740, 740)   # Left/right spread
        y = random.randint(-1500, -100)  # Depth (further back in negative y)
        z = random.randint(520, 680)    # Height range for clouds
        cloud_positions.append((x, y, z))

def draw_cloud(x, y, z):
    glColor3f(1, 1, 1)  # white
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

    # Castle
    glPushMatrix()
    glTranslatef(-50, -700, 0)
    glScalef(2.0, 2.0, 2.0)
    draw_castle()
    glPopMatrix()


# ------------------ Controls ------------------
def keyboardListener(key, x, y):
    pass


def specialKeyListener(key, x, y):
    global camera_pos
    x0, y0, z0 = camera_pos
    if key == GLUT_KEY_LEFT: x0 -= 10
    if key == GLUT_KEY_RIGHT: x0 += 10
    camera_pos = (x0, y0, z0)


def mouseListener(button, state, x, y):
    pass

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
    glutMainLoop()


if __name__ == "__main__":
    main()