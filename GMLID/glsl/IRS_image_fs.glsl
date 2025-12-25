#version 330

uniform sampler2D texture0;

uniform vec4 source;

in vec2 vs_uv;
out vec4 fs_colour;

void main(){
  vec2 pos = texture(texture0, vs_uv).xy;

  fs_colour = texture(texture0, vs_uv)*0.5 + 0.5 + vec4(vec3(1.0 - step(source.z, length(pos - source.xy))), 1.0);

  //fs_colour = texture(texture0, vs_uv);
}
