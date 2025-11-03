import sys, math, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

MESH_CACHE = {}

def _sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

# cross product para calcular normais
def _cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

def _normalize(v):
    l = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if l == 0.0:
        return (0.0, 0.0, 0.0)
    return (v[0]/l, v[1]/l, v[2]/l)

def read_obj(path):
    verts = []
    norms = []
    texs = []
    faces = []
    with open(path, 'r') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            parts = ln.split()
            # formato OBJ:
            # v - vertice
            # vn - normal
            # vt - UV
            # f - face 
            if parts[0] == 'v' and len(parts) >= 4:
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif parts[0] == 'vn' and len(parts) >= 4:
                norms.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif parts[0] == 'vt' and len(parts) >= 3:
                texs.append((float(parts[1]), float(parts[2])))
            elif parts[0] == 'f' and len(parts) >= 4:
                face = []
                for v in parts[1:]:
                    vp = v.split('/')
                    vi = int(vp[0]) - 1 if vp[0] else None
                    vti = int(vp[1]) - 1 if len(vp) > 1 and vp[1] != '' else None
                    vni = int(vp[2]) - 1 if len(vp) > 2 and vp[2] != '' else None
                    face.append((vi, vti, vni))
                faces.append(face)
    return {'verts': verts, 'norms': norms, 'texs': texs, 'faces': faces}

def draw_mesh(path, scale=1.0):
    mesh = MESH_CACHE.get(path)
    if mesh is None:
        mesh = read_obj(path)
        MESH_CACHE[path] = mesh

    verts = mesh['verts']
    norms = mesh['norms']
    texs = mesh['texs']
    faces = mesh['faces']

    glPushMatrix()
    if scale != 1.0:
        glScalef(scale, scale, scale)

    glBegin(GL_TRIANGLES)
    for face in faces:
        if len(face) < 3:
            continue
        # triangular faces
        for i in range(1, len(face)-1):
            tri = (face[0], face[i], face[i+1])
            # calcula normal caso não haja norm por vertice
            use_face_normal = (tri[0][2] is None or tri[1][2] is None or tri[2][2] is None)
            face_normal = None
            if use_face_normal:
                p0 = verts[tri[0][0]]
                p1 = verts[tri[1][0]]
                p2 = verts[tri[2][0]]
                face_normal = _normalize(_cross(_sub(p1, p0), _sub(p2, p0)))

            for vert in tri:
                vi, vti, vni = vert
                if vni is not None and 0 <= vni < len(norms):
                    glNormal3fv(norms[vni])
                else:
                    glNormal3fv(face_normal)
                if vti is not None and 0 <= vti < len(texs):
                    glTexCoord2fv(texs[vti])
                glVertex3fv(verts[vi])
    glEnd()

    glPopMatrix()

def load_texture(path, repeat=True):
    if not os.path.isfile(path):
        print("Texture not found:", path); sys.exit(1)

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    data = img.tobytes("raw", "RGBA", 0, -1)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    # filtros  e  mipmaps (veremos esta parte mais tarde )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)

    # Criação de mipmaps com o GLU
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)

    #devolve o ID de cada textura carregada que será usado quando os objectos forem desenhados
    return tex_id