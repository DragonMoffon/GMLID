#version 330

#include :system:shaders/lib/random.glsl

uniform sampler2D deflection_map;

uniform float seed;

in vec2 origin;
out vec2 vs_uv;

void main(){
  float shift_x = random(vec3(seed, origin));
  float shift_y = random(shift_x);
  // Adjust origin to get rays various final ray locations.
  // The mod wraps the ray around to avoid the bias the clamp sample mode has.
  // 1.0 is added to ensure the resulting origin is always positive before modulo.
  vec2 shifted = mod(origin + vec2(shift_x*2.0-1.0, shift_y*2.0-1.0)+1.0, 1.0);
  vec2 target = texture(deflection_map, shifted).rg;
  gl_Position = vec4(target, 0.0, 1.0);
}
