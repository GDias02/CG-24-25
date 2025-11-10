from OpenGL.GL import *

class Material:
    def __init__(self, ambient=(0.1,0.1,0.1), diffuse=(0.8,0.8,0.8),
                 specular=(0.0,0.0,0.0), shininess=0.0, emission=(0.0,0.0,0.0),
                 shader=None):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.emission = emission
        self.shader = shader

def apply_material(mat: Material):
    if mat is None:
        return
        
    if mat.shader:
        mat.shader.use()
        mat.shader.set_vec3("lightColor", (1.0, 1.0, 1.0))
        mat.shader.set_vec3("objectColor", mat.diffuse)
        mat.shader.set_vec3("lightPos", (5.0, 5.0, 5.0))
        mat.shader.set_vec3("viewPos", (0.0, 0.0, 5.0))
    else:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (*mat.ambient, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (*mat.diffuse, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (*mat.specular, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat.shininess)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (*mat.emission, 1.0))