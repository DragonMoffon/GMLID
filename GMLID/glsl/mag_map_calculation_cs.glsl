#version 460
/*
  The max GPU 
*/

#define RADIUS 1.0

layout(local_size_x=1024) in;

layout(binding=0) uniform sampler2D lensTexture; // Texture of lens transform
layout(binding=1) writeonly uniform image2DArray outputTexture; // Massive array object for output

// The number of hits in a vertical slice of a lens event.
shared int inverseRayHitCount;

void main(){

  vec2 source = 4.0 * (vec2(gl_WorkGroupID.xy + ivec2(0, 0)) / 1024.0 - 0.5); // map to -2.0 -> 2.0 range 
  vec2 diff = texelFetch(lensTexture, ivec2(gl_WorkGroupID.z, gl_LocalInvocationID.x), 0).xy - source;
  int result = int(1.0 - step(RADIUS, dot(diff, diff)));

  // Once every worker has checked for a source hit, the 0th worker writes to the output image
  barrier();
  if (gl_LocalInvocationID.x != 0){
    return;
  }
  atomicAdd(inverseRayHitCount, 100);
  imageStore(outputTexture, ivec3(gl_WorkGroupID.xyz), ivec4(inverseRayHitCount, inverseRayHitCount, inverseRayHitCount, 1));

}
