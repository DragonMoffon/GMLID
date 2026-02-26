#version 330
/*
The critical curve is the locations in the lens plane which have "infinite" amplification.
The caustic map is the projected amplifications on the source plane.

This shader samples the IRS histogram (caustic map) based on the deflection map
to reconstruct the critical curve.
*/

uniform sampler2D deflectionMap
uniform sampler2D causticMap

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    vec2 target = 2.0 * texture(deflectionMap, vs_uv).rg + 1.0; // convert -2.0 to 2.0 -> 0.0 to 1.0
    // is the target outside of the -2.0 to 2.0 range of the image? If it isn't then discard the sample
    fs_colour = (target.x < 0.0 || 1.0 < target.x || target.y < 0.0 || 1.0 < target.y)? vec4(0.0, 0.0, 0.0, 1.0) : texture(caustic, target);
}