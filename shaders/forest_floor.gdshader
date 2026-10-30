// The eastern wood's floor (round 20b): leaf litter, grass or sand, by how much light each patch gets over a
// day (shared/forest.py, forest_light(): the sun across the game's summer day and the open sky, through
// every crown and bush). The light map's red is how green the floor is, its green how sandy (where the
// wood meets the beach), its blue the light itself. The grass is the meadow's own lawn and the sand the
// beach's, with the same texture coordinates as theirs, so where the floor meets them there is no seam;
// in between, the grass comes and goes in small, uneven patches rather than fading.
// Round 20d: three steps by the light, so the trees' shade shows: the lawn where it is light, patchy grass
// (grass in small pieces, litter between) in the half shade (the light map's alpha), golden needles and leaves only in the deepest shade. Each
// step comes in over the last in ragged patches, like the grass.
shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx;

uniform sampler2D mid_tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D litter_tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D lawn_tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D sand_tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D light_map : filter_linear, repeat_disable;
uniform vec4 rect = vec4(0.0, 0.0, 1.0, 1.0);    // the light map's corner (x, z) and size (metres)
uniform float sat = 1.0;        // (round 34: Park Güell's floor, its green toned down towards grey — not yellow)

varying vec3 wpos;
varying vec3 wnrm;
// (round 41, the user: "fix the grass on the steep bank") the floor's pictures are laid flat from above, 3 m to a repeat,
// so on a steep bank one repeat ran 6–10 m up the slope and read as streaks close to the camera. Where the ground
// tips, each picture and each patch's noise is also laid from the side (from the east and from the south), and the
// three are blended by how the ground faces: no stretch on any slope, the flat floor exactly as before.
const float SIDE_M = 3.0;       // metres to a repeat, as the flat floor

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

// how much each of the three projections counts: from above, from the east (x), from the south (z)
vec3 tri_w() {
	vec3 w = pow(abs(normalize(wnrm)), vec3(8.0));
	return w / (w.x + w.y + w.z);
}

// a picture laid three ways: from above on the mesh's own coordinates (the flat floor unchanged), from the sides on
// the world's, the same size
vec3 tri_tex(sampler2D tex, vec2 top_uv, vec3 w) {
	vec3 c = texture(tex, top_uv).rgb * w.y;
	if (w.y < 0.999) {
		c += texture(tex, vec2(wpos.z, -wpos.y) / SIDE_M).rgb * w.x;
		c += texture(tex, vec2(wpos.x, -wpos.y) / SIDE_M).rgb * w.z;
	}
	return c;
}

// the patches' noise the same way, so their edges don't streak up a bank either
float tri_noise(vec2 off, float f, vec3 w) {
	float n = vnoise(wpos.xz * f + off) * w.y;
	if (w.y < 0.999) {
		n += vnoise(vec2(wpos.z, wpos.y) * f + off) * w.x;
		n += vnoise(vec2(wpos.x, wpos.y) * f + off) * w.z;
		// (blending three noises flattens them towards grey, and the patches with them: given back their contrast)
		n = 0.5 + (n - 0.5) / sqrt(dot(w, w));
	}
	return n;
}

void fragment() {
	vec4 lm = texture(light_map, (wpos.xz - rect.xy) / rect.zw);
	vec3 w = tri_w();
	// patches: a few metres across, with ragged edges a hand across
	float n = tri_noise(vec2(0.0), 0.55, w) * 0.55 + tri_noise(vec2(0.0), 1.9, w) * 0.3 + tri_noise(vec2(0.0), 6.0, w) * 0.15;
	float g = smoothstep(0.45, 0.55, lm.r + (n - 0.5) * 0.85);
	// (the patchy grass's patches: the same kind of ragged edge, from its own noise so the two edges don't line up)
	float n2 = tri_noise(vec2(11.0), 0.7, w) * 0.55 + tri_noise(vec2(5.0), 2.3, w) * 0.3 + tri_noise(vec2(2.0), 6.5, w) * 0.15;
	float mo = smoothstep(0.45, 0.55, lm.a + (n2 - 0.5) * 0.85);
	float s = smoothstep(0.42, 0.58, lm.g + (tri_noise(vec2(7.0), 1.3, w) - 0.5) * 0.36);
	// (the needles and the patchy grass each twice, at two sizes and turned, blended by a slow noise, so their
	// drifts don't repeat)
	vec2 uv2 = vec2(UV.y, -UV.x) * 0.61 + vec2(0.37, 0.11);
	float twice = smoothstep(0.3, 0.7, tri_noise(vec2(3.0), 0.21, w));
	vec3 litter = mix(tri_tex(litter_tex, UV, w), tri_tex(litter_tex, uv2, w), twice);
	vec3 mid = mix(tri_tex(mid_tex, UV, w), tri_tex(mid_tex, uv2, w), twice);
	vec3 lawn = tri_tex(lawn_tex, UV, w);
	// (the beach's sand is laid 2.5 m to a repeat, the floor 3 m: the same grain, lined up with the beach's)
	vec3 sand = tri_tex(sand_tex, UV * 1.2 - vec2(0.0, 0.2), w);
	vec3 col = mix(mix(mix(litter, mid, mo), lawn, g), sand, s);
	ALBEDO = mix(vec3(dot(col, vec3(0.3, 0.59, 0.11))), col, sat);
	ROUGHNESS = mix(0.98, 0.95, max(g, s));
}
