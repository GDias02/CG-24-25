#version 120

varying vec3 vNormal;
varying vec3 vPosition;

uniform sampler2D textureSampler;

void main() {
    vec3 N = normalize(vNormal);
    vec3 V = normalize(-vPosition);
    
    // Sample texture using the varying texture coordinate from vertex shader
    vec4 texColor = texture2D(textureSampler, gl_TexCoord[0].st);
    
    // Ambient light (so you can always see something)
    vec4 ambient = gl_LightSource[0].ambient * gl_FrontMaterial.ambient;
    
    // Accumulate diffuse and specular from all lights
    vec4 diffuse = vec4(0.0);
    vec4 specular = vec4(0.0);
    
    // Process each light (0=sun, 1=headlight, 2=point light)
    for (int i = 0; i < 3; i++) {
        vec3 lightPos = gl_LightSource[i].position.xyz;
        
        // Handle directional vs positional lights
        vec3 L;
        float attenuation = 1.0;
        
        if (gl_LightSource[i].position.w == 0.0) {
            // Directional light (like sun)
            L = normalize(lightPos);
        } else {
            // Point/spot light
            vec3 lightDir = lightPos - vPosition;
            float distance = length(lightDir);
            L = normalize(lightDir);
            
            // Distance attenuation
            float constantAtt = gl_LightSource[i].constantAttenuation;
            float linearAtt = gl_LightSource[i].linearAttenuation;
            float quadraticAtt = gl_LightSource[i].quadraticAttenuation;
            attenuation = 1.0 / (constantAtt + linearAtt * distance + quadraticAtt * distance * distance);
            
            // Spotlight cone attenuation
            if (gl_LightSource[i].spotCutoff < 180.0) {
                vec3 spotDir = normalize(gl_LightSource[i].spotDirection);
                float spotDot = dot(-L, spotDir);
                float spotCutoffCos = cos(radians(gl_LightSource[i].spotCutoff));
                
                if (spotDot < spotCutoffCos) {
                    // Outside spotlight cone
                    attenuation = 0.0;
                } else {
                    // Inside cone - apply spot exponent for soft edges
                    float spotEffect = pow(spotDot, gl_LightSource[i].spotExponent);
                    attenuation *= spotEffect;
                }
            }
        }
        
        // Diffuse
        float diff = max(dot(N, L), 0.0);
        diffuse += gl_LightSource[i].diffuse * gl_FrontMaterial.diffuse * diff * attenuation;
        
        // Specular
        vec3 R = reflect(-L, N);
        float spec = pow(max(dot(R, V), 0.0), gl_FrontMaterial.shininess);
        specular += gl_LightSource[i].specular * gl_FrontMaterial.specular * spec * attenuation;
    }
    
    // Combine everything with texture
    gl_FragColor = (ambient + diffuse) * texColor + specular;
}
