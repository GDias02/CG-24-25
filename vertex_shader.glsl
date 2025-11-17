#version 120

varying vec3 vNormal;
varying vec3 vPosition;

void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

    vNormal   = normalize(gl_NormalMatrix * gl_Normal);
    vPosition = vec3(gl_ModelViewMatrix * gl_Vertex);
    
    // Pass through texture coordinates
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
