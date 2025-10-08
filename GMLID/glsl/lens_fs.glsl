#version 430

struct lensData{
  float mass;
  float reserved;
  vec2 pos;
};


layout(std430) readonly buffer lensBlock
{
  int count;
  float reserved;
  lensData lens[];
} lenses;

uniform vec4 plane; // (x) Lens distance; (y) source distance; (z) total distance; (w) reserved;

uniform sampler2D sourceImage;

in vec2 vs_uv; // Interpolated Coordinate in lens plane (cartesian)

out vec4 fs_ray; // (x, y) IRS Coordinate in source plane; (z) Sampled intensity; (w) reserved

vec2 findDeflection(vec4 ray, lensData lens){
  vec2 rel = ray.xy - lens.pos;
  float sep = rel.x*rel.x + rel.y*rel.y;

  vec2 deflection = lens.mass * rel / sep;
  vec2 source = deflection - ray.zw;
  return plane.y * tan(source);
}

void main(){
  vec2 fs_uv = vs_uv;
  vec4 ray = vec4(vs_uv, atan(vs_uv / plane.x));

  for (int i = 0; i < lenses.count; i++){
    fs_uv = fs_uv - findDeflection(ray, lenses.lens[i]); //findDeflection(ray, lenses.lens[i]);
  }

  float b = 1.0 - step(100.0, dot(fs_uv, fs_uv));
  fs_ray = vec4(vec3(b), 1.0);

  // fs_uv = fs_uv / 2000 + 0.5;
  // fs_ray = vec4(texture(sourceImage, fs_uv).rgb, 1.0);


}
