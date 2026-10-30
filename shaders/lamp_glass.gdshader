// The street lamps' lanterns (the Meshy lamp): a warm glow from the glass of the cage after dark, drawn over
// the lamp's own material (as its next pass, added on), so by day the lamp is exactly as it was (round 20e:
// the light used to come from a glowing ball hung under the lantern, which looked wrong close to). The
// glass is everything in the lantern's cage that isn't its dark green metal (some panes are painted pale,
// one darker: all glow alike), between the cage's foot and its roof (the model's height, 0 at the foot, 1 at
// the top) and close to the lantern's middle (not the arm that holds it), so nothing else lights up.
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, shadows_disabled, fog_disabled;

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic;
uniform vec3 glow_color : source_color = vec3(1.0, 0.8, 0.5);
uniform float glow = 0.0;
uniform vec2 band = vec2(0.765, 0.875);          // the cage, foot to roof
uniform vec2 axis = vec2(-0.0496, -0.0035);       // the lantern's middle (model x, z)
uniform float reach = 0.065;                      // how far out the cage goes from it

varying vec3 mp;

void vertex() {
	mp = VERTEX;
}

void fragment() {
	vec3 a = texture(albedo_tex, UV).rgb;
	// (the metal is dark, below about 0.18 as the picture stores it; the glass, pale or dark, above it; the
	// texture is read in linear light, where those are about 0.027 and 0.042)
	float pane = smoothstep(0.027, 0.042, dot(a, vec3(0.3, 0.5, 0.2)));
	float in_lantern = smoothstep(band.x, band.x + 0.01, mp.y) * (1.0 - smoothstep(band.y - 0.01, band.y, mp.y))
		* (1.0 - smoothstep(reach - 0.005, reach, length(mp.xz - axis)));
	ALBEDO = glow_color * glow * pane * in_lantern;
}
