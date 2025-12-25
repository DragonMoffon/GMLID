#version 460
/*
This summation is not very parellisable (as it is currently done)
however this keeps the data on the gpu for as long as possible which is better
from a memory management standpoint.
*/

layout(local_size_x=1024) in;

layout(binding=0) writeonly uniform image2D magMapTexture;
layout(binding=1) uniform sampler2DArray semiMagMapTexture;

// The number of hits in a lens event.
shared int inverseRayHitCount;

void main(){
  // Get the count of a vertical slice
  int count = int(texelFetch(semiMagMapTexture, ivec3(gl_WorkGroupID.xy, gl_LocalInvocationID.x), 0).r);
  // Add the count to total count for the pixel
  atomicAdd(inverseRayHitCount, count);

  barrier();
  if (gl_LocalInvocationID.x != 0){
    return;
  }
  // The 0th worker then writes to the final image
  atomicAdd(inverseRayHitCount, 100);
  imageStore(magMapTexture, ivec2(gl_WorkGroupID.xy), ivec4(inverseRayHitCount, inverseRayHitCount, inverseRayHitCount, 1));
}


