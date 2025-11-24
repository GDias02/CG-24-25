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
FOV = 100.0
#-Último tempo
last_time = 0.0

user_input = (0.0, 0.0)
toggle_door = False
toggle_garage_door = False

#-Contentores de texturas
tex_car = None
tex_terrain = None
tex_wheel = None
tex_steering_wheel = None
tex_door = None
tex_garage = None
tex_garage_door = None

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
WHEEL_TEXTURE_PATH = "tex/wheel-marked.png" #use tex/wheel-marked.png to get rid of the white marks
# -Volante
STEERING_WHEEL_MODEL_PATH = "models/steering_wheel.obj"
STEERING_WHEEL_TEXTURE_PATH = "tex/car.jpg"
# -Porta
DOOR_MODEL_PATH = "models/door.obj"
DOOR_TEXTURE_PATH = "tex/car.jpg"
# -Terreno
TERRAIN_MODEL_PATH = "models/terrain.obj"
TERRAIN_TEXTURE_PATH = "tex/terrain.jpg"
# -Garagem
GARAGE_MODEL_PATH = "models/garage.obj"
GARAGE_TEXTURE_PATH = "tex/car.jpg"
# -PortaDaGaragem
GARAGE_DOOR_MODEL_PATH = "models/garage_door.obj"
GARAGE_DOOR_TEXTURE_PATH = "tex/car.jpg"


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

STEERING_WHEEL_RADIUS = 0.5 
STEERING_WHEEL_OFFSET_X = 0.23
STEERING_WHEEL_OFFSET_Y = 0.62
STEERING_WHEEL_OFFSET_Z = 0.6

CAR_L_LIGHT_OFFSET_X = 0.0
CAR_L_LIGHT_OFFSET_Y = 0.0
CAR_L_LIGHT_OFFSET_Z = 2.0

CAR_R_LIGHT_OFFSET_X = 0.0
CAR_R_LIGHT_OFFSET_Y = 0.0
CAR_R_LIGHT_OFFSET_Z = 0.0

DOOR_L_OFFSET_X = 0.9
DOOR_L_OFFSET_Y = 0.0
DOOR_L_OFFSET_Z = 1.0

DOOR_R_OFFSET_X = -0.9
DOOR_R_OFFSET_Y = 0.0
DOOR_R_OFFSET_Z = 1.0

camera_distance = 10.0
camera_height = 8.0
cam_dx = 0
cam_dz = 0

GARAGE_OFFSET_X = 0.0
GARAGE_OFFSET_Y = 0.0
GARAGE_OFFSET_Z = 0.0

GARAGE_DOOR_OFFSET_X = 0.0
GARAGE_DOOR_OFFSET_Y = 0.0
GARAGE_DOOR_OFFSET_Z = 0.0

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

def draw_door_left():
    glBindTexture(GL_TEXTURE_2D, tex_door)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(DOOR_MODEL_PATH, scale=1)

#the door model is a left side one
#we'll scale it (mirroring it) BUT,
#this extra function is needed to avoid back face culling
def draw_door_right(): 
    glFrontFace(GL_CW) #key part
    glBindTexture(GL_TEXTURE_2D, tex_door)
    glColor3f(1.0, 1.0, 1.0)
    draw_mesh(DOOR_MODEL_PATH, scale=1)
    glFrontFace(GL_CCW) #key part
    
def draw_car_light():
    # Posição do farol (em coordenadas do carro)
    glLightfv(GL_LIGHT1, GL_POSITION, (0, 0, 0, 1.0))  # Posicional
    # Direção do feixe (apontar para a frente do carro)
    glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (0, -0.2, 1))
    # Cor do farol
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (1.0, 1.0, 0.8, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, (1.0, 1.0, 0.8, 1.0))
    # Ângulo do feixe
    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 25.0)
    # Intensidade do feixe
    glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 90.0)

def draw_light_marker():
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.0)  # bright yellow sphere
    glutSolidSphere(0.2, 12, 12)
    glEnable(GL_LIGHTING)

def draw_garage():
    glBindTexture(GL_TEXTURE_2D, tex_garage)
    glColor3f(1.0,1.0,1.0)
    draw_mesh(GARAGE_MODEL_PATH, scale=1)

def draw_garage_door():
    glBindTexture(GL_TEXTURE_2D, tex_garage_door)
    glColor3f(1.0,1.0,1.0)
    draw_mesh(GARAGE_DOOR_MODEL_PATH, scale=1)


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

def move_steering_wheel(x,y,z):
    def _tf(node):
        global user_input
        radius = node.state.get('radius',0)
        x_axis, y_axis = user_input
        glTranslate(x,y,z)
        glRotatef(-55.0 ,1,0,0)
        glRotatef(node.state.get('rotation', 0), 0, 1, 0)
        glScalef(radius,radius,radius)
    return _tf

def move_car_light(x,y,z):
    def _tf(node):
        glTranslatef(x,y,z)
        rotation = node.state.get('rotation',0)
        glRotatef(rotation ,0,1,0)
    return _tf

def move_car_door(x,y,z):
    def _tf(node):
        glTranslatef(x,y,z)
        rotation = node.state.get('rotation', 0)
        glRotatef(rotation, 0, 1,0)
        if node.state.get('side', 0) == 'right':
            glScalef(-1.0, 1.0, 1.0)
    return _tf

def move_garage(x,y,z):
    def _tf(node):
        glTranslatef(x,y,z)
        #glRotatef(0, 0, 1, 0)
    return _tf

def move_garage_door(x,y,z):
    def _tf(node):
        glTranslatef(x,y,z)
        rotation = node.state.get('rotation', 0)
        glRotatef(rotation, 1, 0, 0) 
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

    def door_updater(self, node, dt):
        def door_rotation_calc():
            open = node.state.get('open', 0)
            rotation = node.state.get('rotation', 0)
            orientation = node.state.get('side', 0)
            factor = 15.0 if orientation == 'right' else -15.0
            max_rotation = 50 if orientation == 'right' else -50
            
            #open the door
            if open and orientation == 'right': #the door shall rotate only from 0 to 50 degrees
                return rotation + factor if rotation + factor <= max_rotation else max_rotation
            if open and orientation == 'left':
                return rotation + factor if rotation + factor >= max_rotation else max_rotation
            #close the door
            if not open and orientation == 'right':
                return rotation - factor if rotation - factor >= 0 else 0
            if not open and orientation == 'left':
                return rotation - factor if rotation - factor <= 0 else 0
            
            
        #determine if should open or close
        global toggle_door
        
        if toggle_door != node.state.get('toggle',0): #if toggle has changed:
            node.state['toggle'] = toggle_door #This avoids constante door flickering
            node.state['open'] = not node.state.get('open',0)
        node.state['rotation'] = door_rotation_calc()

class Garage:
    def door_updater(self, node, dt):
        def door_rotation_cal():
            open = node.state.get('open', 0)
            rotation = node.state.get('rotation', 0)
            factor = 10.0
            max_rotation = 90

            if open:
                return rotation + factor if rotation + factor <= max_rotation else max_rotation
            #else
            return rotation - factor if rotation - factor >= 0 else 0

        global toggle_garage_door
        if toggle_garage_door != node.state.get('toggle', 0):
            node.state['toggle'] = toggle_garage_door #this avoids door flickering
            node.state['open'] = not node.state.get('open', 0)
        node.state['rotation'] = door_rotation_cal()

def update_headlight(node, dt):
    # apply light position in world space
    glLightfv(GL_LIGHT1, GL_POSITION, (0, 0, 0, 1.0))
    glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (0, 0, 1))


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
    
    def find(self, name):
        for child in self.children:
            if child.name == name:
                return child
            
        return None



def build_scene():
    # Nó raiz (mundo) - apenas um contentor
    world = Node("World")

    terrain = Node("Terrain",
                   geom=draw_terrain,
                   transform=tf_scale(1.0, 1.0, 1.0),
                   state={"material": TERRAIN_MATERIAL})
    
    point_light_marker = Node(
        "Light2Marker",
        geom=draw_light_marker,
        transform=tf_translate(0.0, 0.5, 10.0)
    )

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
                        transform=move_steering_wheel(STEERING_WHEEL_OFFSET_X,
                                                        STEERING_WHEEL_OFFSET_Y,
                                                        STEERING_WHEEL_OFFSET_Z),
                    state={"radius": STEERING_WHEEL_RADIUS,
                           "turn_factor": 0.0,
                           "material": WHEEL_MATERIAL})
    
    car_door_l = Node("Car Left Door",
                      geom=lambda: draw_door_left(),
                      updater=Car().door_updater,
                      transform=move_car_door(DOOR_L_OFFSET_X,
                                              DOOR_L_OFFSET_Y,
                                              DOOR_L_OFFSET_Z),
                      state={"side" : "left",
                             "toggle": False,
                             "rotation" : 0.0})

    car_door_r = Node("Car Right Door",
                      geom=lambda: draw_door_right(),
                      updater=Car().door_updater,
                      transform=move_car_door(DOOR_R_OFFSET_X,
                                              DOOR_R_OFFSET_Y,
                                              DOOR_R_OFFSET_Z),
                      state={"side" : "right",
                             "toggle": False,
                             "rotation" : 0.0})
    
    garage = Node("Garage",
                  geom=lambda: draw_garage(),
                  transform=move_garage(GARAGE_OFFSET_X,
                                        GARAGE_OFFSET_Y,
                                        GARAGE_OFFSET_Z),
                  state={})

    garage_door = Node("Garage Door",
                       geom=lambda: draw_garage_door(),
                       updater=Garage().door_updater,
                       transform=move_garage_door(GARAGE_DOOR_OFFSET_X,
                                                  GARAGE_DOOR_OFFSET_Y,
                                                  GARAGE_DOOR_OFFSET_Z),
                       state={"toggle":False,
                              "rotation" : 0.0,
                              "open": False})
    camera = Node("Camera",
                  updater=camera_updater,
                  state={"mode": 0, "pos": (0, 0, 0), "look": (0, 0, 0)})

    world.add(
        terrain,
        camera,
        car.add(
            wheel_f_r,
            wheel_f_l, 
            wheel_r_r, 
            wheel_r_l,
            steering_wheel,
            car_door_l,
            car_door_r
        ),
        garage.add(
            garage_door
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

def load_shader(vs_path, fs_path):
    vs = glCreateShader(GL_VERTEX_SHADER)
    fs = glCreateShader(GL_FRAGMENT_SHADER)

    with open(vs_path, 'r') as f:
        vs_src = f.read()
    with open(fs_path, 'r') as f:
        fs_src = f.read()

    glShaderSource(vs, vs_src)
    glShaderSource(fs, fs_src)

    glCompileShader(vs)
    glCompileShader(fs)

    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)

    return prog


# Setup do OpenGL
def init_gl():
    global tex_car, tex_terrain, tex_wheel, tex_steering_wheel, tex_door, tex_garage, tex_garage_door, SHADER_PROGRAM

    SHADER_PROGRAM = load_shader("vertex_shader.glsl", "fragment_shader.glsl")
    glUseProgram(SHADER_PROGRAM)

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

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0) #luz ambiente
    glEnable(GL_LIGHT1) #luz do farol esquerdo
    glEnable(GL_LIGHT2) #luz do farol esquerdo
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0,0,0,0))


    # White test light above the floor
    glLightfv(GL_LIGHT2, GL_POSITION, (0.0, 2, -20.0, 1.0))   # 1.0 → point light
    #glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, (0.0, -1.0, 0.0)) # pointing down
    glLightf(GL_LIGHT2, GL_SPOT_CUTOFF, 30.0)
    glLightfv(GL_LIGHT2, GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT2, GL_AMBIENT,  (0.0, 0.0, 0.0, 1.0))
    #glLightf(GL_LIGHT2, GL_LINEAR_ATTENUATION,   0.0)
    glLightf(GL_LIGHT2, GL_QUADRATIC_ATTENUATION, 0.01)

    instance_materials()

    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_TEXTURE_2D)

    # Disable color material to use explicit materials
    glDisable(GL_COLOR_MATERIAL)
    
    tex_car = load_texture(CAR_TEXTURE_PATH, repeat=False)
    tex_terrain = load_texture(TERRAIN_TEXTURE_PATH, repeat=True)
    tex_wheel = load_texture(WHEEL_TEXTURE_PATH, repeat=False)
    tex_steering_wheel = load_texture(STEERING_WHEEL_TEXTURE_PATH, repeat=False)
    tex_door = load_texture(DOOR_TEXTURE_PATH, repeat=False)
    tex_garage = load_texture(GARAGE_TEXTURE_PATH, repeat = False)
    tex_garage_door = load_texture(GARAGE_DOOR_TEXTURE_PATH, repeat = False)

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

    glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, (0.0, -1.0, 0.0))

    # Câmara
    update_camera()

    # Inclinação para melhor percepção de profundidade
    #glRotatef(18.0, 1, 0, 0)
    #glRotatef(28.0, 0, 1, 0)

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
    global toggle_door, camera_distance, camera_height
    
    _pressed_keys.add(key)
    _recompute_user_input()
    if key == b'p': #p de porta -> this is in this function, because it's on keypress, not keydown
        toggle_door = not toggle_door
    if key == b'g':
        toggle_garage_door = not toggle_garage_door
    if key == b'\x1b':
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)

    if key == b'+':
        camera_height = max(4.0, round(camera_height - 0.8, 1))
        camera_distance = max(5.0, round(camera_distance - 1.0, 1))
        print(camera_height , "\n" , camera_distance)

    if key == b'-':
        camera_height = min(12.0, round(camera_height + 0.8, 1))
        camera_distance = min(15.0, round(camera_distance + 1.0, 1))
        print(camera_height , "\n" , camera_distance)
    
    if key == b'v':
        cam = SCENE.find("Camera").state
        cam["mode"] = (cam["mode"] + 1) % 3
    

def keyboard_up(key, x, y):
    if key in _pressed_keys:
        _pressed_keys.remove(key)
    _recompute_user_input()

def special_up(key, x, y):
    global cam_dx, cam_dz

    if key in [GLUT_KEY_UP, GLUT_KEY_DOWN]:
        cam_dz = 0
    if key in [GLUT_KEY_RIGHT, GLUT_KEY_LEFT]:
        cam_dx = 0


def special_down(key, x, y):
    global cam_dx, cam_dz

    if SCENE.find("Camera").state["mode"] == 1:
        if key == GLUT_KEY_UP:
            cam_dz = 1
        if key == GLUT_KEY_DOWN:
            cam_dz = -1
        if key == GLUT_KEY_RIGHT:
            cam_dx = -1
        if key == GLUT_KEY_LEFT:
            cam_dx = 1



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

def camera_updater(node, dt):
    global car_pos, car_theta
    global camera_distance, camera_height
    global cam_dx, cam_dz

    mode = node.state["mode"]
    rad = math.radians(car_theta)

    if(mode == 0):
        cam_x = car_pos[0] - math.sin(rad) * camera_distance
        cam_y = car_pos[1] + camera_height
        cam_z = car_pos[2] - math.cos(rad) * camera_distance

        node.state["pos"] = (cam_x, cam_y, cam_z)
        node.state["look"] = (car_pos[0], car_pos[1], car_pos[2])

    elif(mode == 1):
        cam_pos = node.state["pos"]
        cam_look = node.state["look"]

        node.state["pos"] = (cam_pos[0] + cam_dx, cam_pos[1], cam_pos[2] + cam_dz)
        node.state["look"] = (cam_look[0] + cam_dx, cam_look[1], cam_look[2] + cam_dz)

    else:
        cam_x = car_pos[0] + math.sin(rad) * 0.5
        cam_y = car_pos[1] + 2.0
        cam_z = car_pos[2] + math.cos(rad) * 0.5

        look_x = car_pos[0] + math.sin(rad) * 5.0
        look_y = car_pos[1] + 1.2
        look_z = car_pos[2] + math.cos(rad) * 5.0

        node.state["pos"] = (cam_x, cam_y, cam_z)
        node.state["look"] = (look_x, look_y, look_z)


def update_camera():
    cam = SCENE.find("Camera").state
    pos = cam["pos"]
    look = cam["look"]

    gluLookAt(
        pos[0], pos[1], pos[2],
        look[0], look[1], look[2],
        0, 1, 0
    )

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
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutMainLoop()

if __name__ == "__main__":
    main()
