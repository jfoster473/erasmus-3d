// The sea: one big flat sheet; the ripples are scrolling normal maps, deeper blue further out,
// and the sky and sun shining off it.
shader_type spatial;
render_mode specular_schlick_ggx;

uniform sampler2D wave_a : hint_normal, filter_linear_mipmap;
uniform sampler2D wave_b : hint_normal, filter_linear_mipmap;
uniform vec3 shallow : source_color = vec3(0.32, 0.62, 0.64);
uniform vec3 deep : source_color = vec3(0.1, 0.33, 0.47);
uniform float shore_z = 215.0;           // the water's edge (world z); it deepens beyond

void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 p = w.xz;
	vec3 n1 = texture(wave_a, p * 0.045 + vec2(TIME * 0.012, TIME * 0.007)).rgb;
	vec3 n2 = texture(wave_b, p * 0.11 + vec2(-TIME * 0.01, TIME * 0.016)).rgb;
	NORMAL_MAP = normalize(mix(n1, n2, 0.45));
	NORMAL_MAP_DEPTH = 0.55;
	ALBEDO = mix(shallow, deep, clamp((w.z - shore_z) / 45.0, 0.0, 1.0));
	ROUGHNESS = 0.07;
	SPECULAR = 0.55;
}
