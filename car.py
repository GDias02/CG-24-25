import sys, math, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

from loaders_lib import *

#Global vars
#-Janela dimensões
WIN_W, WIN_H = 800, 600
#-FOV
FOV = 40.0
#-Último tempo
last_time = 0.0

tex_car = None
tex_terrain = None

CAR_MODEL_PATH = "models/car.obj"
CAR_TEXTURE_PATH = "tex/car.jpg"
TERRAIN_MODEL_PATH = "models/terrain.obj"
TERRAIN_TEXTURE_PATH = "tex/terrain.jpg"

def draw_car():
    glBindTexture(GL_TEXTURE_2D, tex_car)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(CAR_MODEL_PATH, scale=1)

def draw_terrain():
    glBindTexture(GL_TEXTURE_2D, tex_terrain)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(TERRAIN_MODEL_PATH, scale=1)

def draw_sphere(color=(0.8, 0.85, 0.95)):
    glColor3f(*color)
    glutSolidSphere(1.0, 24, 24)

def geo_star():
    draw_sphere((0.95, 0.75, 0.35))

def tf_scale(sx, sy, sz):
    def _tf(node):
        glScalef(sx, sy, sz)
    return _tf

class Node:
    def __init__(self, name, geom=None, transform=None, updater=None, state=None):
        self.name = name
        self.geom = geom
        self.transform = transform  #função de transformação
        self.updater = updater      #será uma função (actualiza o state)
        self.state = state or {}    #parametros da função de update e transform
        self.children = []

    #aqui acrescentam-se os filhos de cada nó
    def add(self, *kids):
        for k in kids:
            self.children.append(k)
        return self

    #aqui faz-se a actualização da geometria
    def update(self, dt):
        if self.updater:
            self.updater(self, dt)
        for c in self.children:
            c.update(dt)

    #é aqui que tudo é desenhado
    def draw(self):
        glPushMatrix()
        if self.transform:
            self.transform(self)
        if self.geom:
            self.geom()
        for c in self.children:
            c.draw()
        glPopMatrix()



def build_scene():
    # Nó raiz (mundo) - apenas um contentor
    world = Node("World")

    terrain = Node("Terrain",
                   geom = draw_terrain,
                   transform=tf_scale(1.0, 1.0, 1.0))

    car = Node("Car",
               geom = draw_car,
               transform=tf_scale(1.0, 1.0, 1.0))
    
    world.add(terrain, car)

    return world

SCENE = None

# Setup do OpenGL
def init_gl():
    global tex_car, tex_terrain

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)

    # Iluminação
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.45, 0.9, 0.35, 0.0)) 
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 2, 1, 0.0))  # direccional

    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.18, 0.18, 0.22, 1.0))

    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_TEXTURE_2D)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    tex_car = load_texture(CAR_TEXTURE_PATH, repeat=False)
    tex_terrain = load_texture(TERRAIN_TEXTURE_PATH, repeat=True)

def reshape(w, h):
    global WIN_W, WIN_H, FOV
    WIN_W, WIN_H = max(1, w), max(1, h)
    glViewport(0, 0, WIN_W, WIN_H)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, WIN_W/float(WIN_H), 0.1, 1000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    glClearColor(0.05, 0.05, 0.25, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Câmara
    gluLookAt(20.0, 12.0, 22.0,   0.0, 0.0, 0.0,   0.0, 1.0, 0.0)
    # Inclinação para melhor percepção de profundidade
    glRotatef(18.0, 1, 0, 0)
    glRotatef(28.0, 0, 1, 0)

    # Desenhar a cena inteira
    SCENE.draw()

    glutSwapBuffers()

def keyboard(key, x, y):
    x_axis = 0.0
    y_axis = 0.0
    if key == b'\x1b':  # ESC
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)
    if key == b'w':
        y_axis = y_axis + 1.0
    if key == b's':
        y_axis = y_axis - 1.0
    if key == b'a':
        x_axis = x_axis - 1.0
    if key == b'd':
        x_axis = x_axis + 1.0
    
    return (x_axis, y_axis)


def idle():
    global last_time
    t_ms = glutGet(GLUT_ELAPSED_TIME)
    t = t_ms * 0.001
    if last_time == 0.0:
        last_time = t
    dt = t - last_time
    last_time = t

    # Actualiza toda a árvore (ângulos/estados)
    SCENE.update(dt)

    glutPostRedisplay()

def main():
    global SCENE
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"Grafo de Cena OO - Classic OpenGL")

    init_gl()
    SCENE = build_scene()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()








