import sys, math, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

from loaders_lib import *
from materials import *

#Global vars
#-Janela dimensões
WIN_W, WIN_H = 800, 600
#-FOV
FOV = 60.0
#-Último tempo
last_time = 0.0

user_input = (0.0, 0.0)

#-Contentores de texturas
tex_car = None
tex_terrain = None
tex_wheel = None
tex_steering_wheel = None

# Default material
DEFAULT_MATERIAL = Material(
    ambient=(0.2, 0.2, 0.2),
    diffuse=(0.8, 0.8, 0.8),
    specular=(0.0, 0.0, 0.0),
    shininess=0.0
)

SHADER_PROGRAM = None
CAR_MATERIAL = None
WHEEL_MATERIAL = None
TERRAIN_MATERIAL = None

# Paths
# -Carro
CAR_MODEL_PATH = "models/car.obj"
CAR_TEXTURE_PATH = "tex/car.jpg"
# -Roda
WHEEL_MODEL_PATH = "models/wheel.obj"
WHEEL_TEXTURE_PATH = "tex/car.jpg"
# -Volante
STEERING_WHEEL_MODEL_PATH = "models/steering_wheel.obj"
STEERING_WHEEL_TEXTURE_PATH = "tex/car.jpg"
# -Porta
DOOR_MODEL_PATH = "models/door.obj"
DOOR_STEERING_WHEEL_MODEL_PATH = "tex/car.jpg"
# -Terreno
TERRAIN_MODEL_PATH = "models/terrain.obj"
TERRAIN_TEXTURE_PATH = "tex/terrain.jpg"


car_pos = [0.0, 0.0, 0.0]
car_theta = 0.0
FORWARD_SPEED = 7.0
ROTATE_SPEED = -90.0

CAR_LIFT = 0.5

FRONT_WHEEL_RADIUS = 0.5
FRONT_WHEEL_OFFSET_X = 1.0
FRONT_WHEEL_OFFSET_Z = 1.2

REAR_WHEEL_RADIUS = 0.7
REAR_WHEEL_OFFSET_X = 0.9
REAR_WHEEL_OFFSET_Z = -1.2

STEERING_WHEEL_RADIUS = 0.5 #este é o scaling correto, abaixo está o de debugging
#STEERING_WHEEL_RADIUS = 2
STEERING_WHEEL_OFFSET_X = 0.23
STEERING_WHEEL_OFFSET_Y = 0.62
STEERING_WHEEL_OFFSET_Z = 0.6

def draw_car():
    glBindTexture(GL_TEXTURE_2D, tex_car)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(CAR_MODEL_PATH, scale=1)

def draw_wheel(radius):
    glBindTexture(GL_TEXTURE_2D, tex_wheel)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(WHEEL_MODEL_PATH, scale=radius)

def draw_terrain():
    glBindTexture(GL_TEXTURE_2D, tex_terrain)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(TERRAIN_MODEL_PATH, scale=1)

def draw_steering_wheel():
    glBindTexture(GL_TEXTURE_2D, tex_steering_wheel)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(STEERING_WHEEL_MODEL_PATH, scale=1)

def tf_scale(sx, sy, sz):
    def _tf(node):
        glScalef(sx, sy, sz)
    return _tf

def tf_translate(x, y, z):
    def _tf(node):
        glTranslatef(x, y, z)
    return _tf

def tf_rotate_y(theta):
    def _tf(node):
        glRotatef(theta, 0, 1, 0)
    return _tf

def move_car():
    def _tf(node):
        glTranslatef(car_pos[0], car_pos[1] + CAR_LIFT, car_pos[2])
        glRotatef(car_theta, 0, 1, 0)
    return _tf

def move_wheel(x, y, z):
    def _tf(node):
        global user_input
        x_axis, y_axis = user_input
        glTranslatef(x, y, z)
        glRotatef(-x_axis * node.state.get('turn_factor', 1) * 30, 0, 1, 0)
        glRotatef(node.state.get('rotation', 0), 1, 0, 0)
    return _tf

def rotate_steering_wheel(x,y,z):
    def _tf(node):
        global user_input
        radius = node.state.get('radius',0)
        x_axis, y_axis = user_input
        glTranslate(x,y,z)
        glRotatef(-55.0 ,1,0,0)
        glRotatef(node.state.get('rotation', 0), 0, 1, 0)
        glScalef(radius,radius,radius)
    return _tf


class Car:
    def car_updater(self, node, dt):
        global car_pos, car_theta, user_input
        x, y = user_input
        car_theta = car_theta + x * ROTATE_SPEED * dt * y
        rad = math.radians(car_theta)
        dir_x = math.sin(rad)
        dir_z = math.cos(rad)
        car_pos[0] += dir_x * y * FORWARD_SPEED * dt
        car_pos[2] += dir_z * y * FORWARD_SPEED * dt
        
        node.state['pos'] = (car_pos[0], car_pos[1], car_pos[2])
        node.state['theta'] = car_theta
    
    def wheel_updater(self, node, dt):
        global user_input
        radius = node.state.get('radius')
        distance = FORWARD_SPEED * dt
        rotation_angle = (distance / (2 * math.pi * radius)) * 360 * user_input[1]
        node.state['rotation'] = node.state.get('rotation', 0) + rotation_angle
    
    def steering_wheel_updater(self, node, dt):
        def st_wheel_rotation_calc():
            """
            Define the angle that the steering wheel should turn to
            If the user isn't pressing a valid key (a or d) then 
            the wheel returns to idle, else, follow user's instructions
            and the wheel stops turning when it does an 120º rotation
            """
            global user_input
            x_axis, y_axis = user_input
            rotation = node.state.get('rotation', 0) #current rotation of the st_wheel
            max_rotation = 160  #wheel can't rotate more than max_rotation degrees
            factor = 20.0         #increase factor for a faster rotation, should be a positive float
            direction = -x_axis
            alpha = direction * factor
            if x_axis != 0.0: #if increasing the rotation 'overflows' then set it to max_rotation, or -max_rotation in case curr rotation is < 0
                return rotation + alpha if abs(rotation + alpha) < max_rotation else max_rotation if rotation > 0 else -max_rotation
            #else, the user is idle, and the steering wheel goes to idle pos
            direction = 1 if rotation < 0 else -1
            alpha = factor * direction #the bellow interval is needed (we're working with floats)
            return rotation if -factor < rotation and rotation < factor else rotation + alpha
            
        node.state['rotation'] = st_wheel_rotation_calc()

class Node:
    def __init__(self, name, geom=None, transform=None, updater=None, state=None):
        self.name = name
        self.geom = geom
        self.transform = transform  #função de transformação
        self.updater = updater      #será uma função (actualiza o state)
        self.state = state or {}    #parametros da função de update e transform
        self.children = []
        self.material = self.state.get('material', None)

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
    
        # Apply material (or default if none specified)
        apply_material(self.material or DEFAULT_MATERIAL)
    
        if self.geom:
            self.geom()
    
        for c in self.children:
            c.draw()
        glPopMatrix()



def build_scene():
    # Nó raiz (mundo) - apenas um contentor
    world = Node("World")

    terrain = Node("Terrain",
                   geom=draw_terrain,
                   transform=tf_scale(1.0, 1.0, 1.0),
                   state={"material": TERRAIN_MATERIAL})

    car = Node("Car",
               geom=draw_car,
               transform=move_car(),
               updater=Car().car_updater,
               state={"material": CAR_MATERIAL})
    
    wheel_f_r = Node("Wheel Front Right",
                    geom=lambda: draw_wheel(FRONT_WHEEL_RADIUS),
                    updater=Car().wheel_updater,
                    transform=move_wheel(FRONT_WHEEL_OFFSET_X,
                                      FRONT_WHEEL_RADIUS-CAR_LIFT, 
                                      FRONT_WHEEL_OFFSET_Z),
                    state={"radius": FRONT_WHEEL_RADIUS, 
                          "turn_factor": 1.0,
                          "material": WHEEL_MATERIAL})
    
    wheel_f_l = Node("Wheel Front Left",
                    geom=lambda: draw_wheel(FRONT_WHEEL_RADIUS),
                    updater=Car().wheel_updater,
                    transform=move_wheel(-FRONT_WHEEL_OFFSET_X,
                                      FRONT_WHEEL_RADIUS-CAR_LIFT, 
                                      FRONT_WHEEL_OFFSET_Z),
                    state={"radius": FRONT_WHEEL_RADIUS, 
                          "turn_factor": 1.0,
                          "material": WHEEL_MATERIAL})
    
    wheel_r_r = Node("Wheel Rear Right",
                    geom=lambda: draw_wheel(REAR_WHEEL_RADIUS),
                    updater=Car().wheel_updater,
                    transform=move_wheel(REAR_WHEEL_OFFSET_X,
                                      REAR_WHEEL_RADIUS-CAR_LIFT, 
                                      REAR_WHEEL_OFFSET_Z),
                    state={"radius": REAR_WHEEL_RADIUS, 
                          "turn_factor": 0.0,
                          "material": WHEEL_MATERIAL})
    
    wheel_r_l = Node("Wheel Rear Left",
                    geom=lambda: draw_wheel(REAR_WHEEL_RADIUS),
                    updater=Car().wheel_updater,
                    transform=move_wheel(-REAR_WHEEL_OFFSET_X,
                                      REAR_WHEEL_RADIUS-CAR_LIFT, 
                                      REAR_WHEEL_OFFSET_Z),
                    state={"radius": REAR_WHEEL_RADIUS, 
                          "turn_factor": 0.0,
                          "material": WHEEL_MATERIAL})

    steering_wheel = Node("Steering Wheel",
                        geom=lambda: draw_steering_wheel(),
                        updater=Car().steering_wheel_updater,
                        transform=rotate_steering_wheel(STEERING_WHEEL_OFFSET_X,
                                                        STEERING_WHEEL_OFFSET_Y,
                                                        STEERING_WHEEL_OFFSET_Z),
                    state={"radius": STEERING_WHEEL_RADIUS,
                           "turn_factor": 0.0,
                           "material": WHEEL_MATERIAL})
    
    world.add(
        terrain, 
        car.add(
            wheel_f_r, 
            wheel_f_l, 
            wheel_r_r, 
            wheel_r_l,
            steering_wheel,
        )
    )

    return world

SCENE = None

def instance_materials():
    global CAR_MATERIAL, WHEEL_MATERIAL, TERRAIN_MATERIAL

    CAR_MATERIAL = Material(
        ambient=(0.3, 0.3, 0.3),
        diffuse=(0.8, 0.3, 0.3),
        specular=(1.0, 1.0, 1.0),
        shininess=100.0
    )
    WHEEL_MATERIAL = Material(
        ambient=(0.3, .3, .3),
        diffuse=(0.2, 0.2, 0.2),
        specular=(0, 0, 0),
        shininess=32.0
    )
    TERRAIN_MATERIAL = Material(
        ambient=(0.2, 0.2, 0.2),
        diffuse=(0.6, 0.6, 0.6),
        specular=(0.1, 0.1, 0.1),
        shininess=8.0
    )

# Setup do OpenGL
def init_gl():
    global tex_car, tex_terrain, tex_wheel, tex_steering_wheel

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)

    # Iluminação
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 2, 1, 0.0))  # direccional

    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 0.7, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.18, 0.18, 0.22, 1.0))

    instance_materials()

    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_TEXTURE_2D)

    # Disable color material to use explicit materials
    glDisable(GL_COLOR_MATERIAL)
    
    tex_car = load_texture(CAR_TEXTURE_PATH, repeat=False)
    tex_terrain = load_texture(TERRAIN_TEXTURE_PATH, repeat=True)
    tex_wheel = load_texture(WHEEL_TEXTURE_PATH, repeat=False)
    tex_steering_wheel = load_texture(STEERING_WHEEL_TEXTURE_PATH, repeat=False)

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

_pressed_keys = set()

def _recompute_user_input():
    global user_input
    x = 0.0
    y = 0.0
    if b'a' in _pressed_keys:
        x -= 1.0
    if b'd' in _pressed_keys:
        x += 1.0
    if b'w' in _pressed_keys:
        y += 1.0
    if b's' in _pressed_keys:
        y -= 1.0
    user_input = (x, y)

def keyboard(key, x, y):
    _pressed_keys.add(key)
    _recompute_user_input()
    if key == b'\x1b':
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)

def keyboard_up(key, x, y):
    if key in _pressed_keys:
        _pressed_keys.remove(key)
    _recompute_user_input()

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
    glutCreateWindow(b"Car Project - Classic OpenGL")

    init_gl()
    SCENE = build_scene()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutMainLoop()

if __name__ == "__main__":
    main()








