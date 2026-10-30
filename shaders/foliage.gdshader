// Leaf cards: alpha-cut foliage that sways in the wind and glows when the sun is behind it.
shader_type spatial;
render_mode cull_disabled, diffuse_burley;

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform float alpha_cut = 0.45;
uniform vec3 backlight_tint : source_color = vec3(0.5, 0.55, 0.28);
uniform float colour_variation = 0.14;
uniform float flutter_amp = 0.003;     // (round 23: a test can still it; round 26: 0.008 → 0.003, its sparkle on the alpha-cut edges)
// (round 25) leaf shadows only near Sandra: beyond shadow_r metres of her (0: no limit) the leaves cast none, the
// edge of that ring feathered over a few metres so it doesn't show as a line (main.gd LEAF_SHADOW_R)
uniform vec3 her_pos = vec3(0.0);
uniform float shadow_r = 0.0;
// (round 26, the user: "The dappled light in the forest is flickering from one moment to the next") in the sun's shadow
// pass the leaves hold still: their sway re-cut every leaf's alpha-cut shadow each frame and the dapples on the floor
// popped (measured, tests --flickermeter --floor: 30 pops in 3 s in the hill wood with the sway, at 0.3 of it 26,
// none without). The leaves themselves still sway and flutter.
uniform float shadow_motion = 0.0;

// per object: where the sway starts (trees bend above the trunk) and how far it goes
instance uniform float sway_base = 2.8;
instance uniform float sway_amp = 0.12;
// (round 41, rule 02 #39) the far stand-in trees' colour, matched to the near ones: they came out ~17% brighter and
// yellower, and where the two cross-fade (on the Ferris wheel) whole clumps flicked bright/dark from frame to frame
instance uniform vec3 tone = vec3(1.0);

varying float shade;
varying vec3 wpos;

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float f = clamp((VERTEX.y - sway_base) / 2.0, 0.0, 1.0);
	float t = TIME;
	vec3 sway = vec3(sin(t * 0.6 + wp.x * 0.35 + wp.z * 0.2), 0.0, cos(t * 0.5 + wp.z * 0.4)) * sway_amp;
	vec3 flutter = vec3(sin(t * 1.9 + wp.x * 2.1 + wp.y * 1.7), sin(t * 1.6 + wp.z * 2.3), cos(t * 2.2 + wp.y * 2.0)) * flutter_amp;
	if (PROJECTION_MATRIX[3][3] > 0.5) {          // (the shadow pass: orthographic)
		sway *= shadow_motion;
		flutter *= 0.0;
	}
	VERTEX += (sway + flutter) * f;
	shade = fract(sin(dot(floor(wp * 0.9), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
	wpos = wp;
}

void fragment() {
	// (in the sun's shadow pass the view is square-on, orthographic; the camera's is in perspective)
	if (shadow_r > 0.0 && PROJECTION_MATRIX[3][3] > 0.5) {
		float feather = fract(sin(dot(floor(wpos * 2.0), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
		if (distance(wpos.xz, her_pos.xz) > shadow_r - 4.0 * feather) {
			discard;
		}
	}
#ifdef CROWN
	// (round 41, the user: "make the trees not be like walls. The camera shouldn't come in") a tree's leaves within
	// about 2.5 m of the camera aren't drawn (the edge speckled, so it isn't a hard line): the camera under a street
	// tree's crown sees Sandra, not a wall of leaves. Not in the sun's shadow pass: the shade stays whole.
	if (PROJECTION_MATRIX[3][3] < 0.5) {
		float speck = fract(sin(dot(floor(wpos * 5.0), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
		if (distance(wpos, CAMERA_POSITION_WORLD) < 1.8 + 1.4 * speck) {
			discard;
		}
	}
#endif
	vec4 c = texture(albedo_tex, UV);
	ALBEDO = c.rgb * (1.0 - colour_variation * 0.5 + colour_variation * shade) * tone;
	ALPHA = c.a;
	ALPHA_SCISSOR_THRESHOLD = alpha_cut;
	ROUGHNESS = 0.75;
	SPECULAR = 0.2;
	BACKLIGHT = backlight_tint;
}
