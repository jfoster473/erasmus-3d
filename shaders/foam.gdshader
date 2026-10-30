// The line of foam where the little waves break on the sand: it comes and goes along the shore.
shader_type spatial;
render_mode blend_mix, depth_draw_never, cull_disabled, shadows_disabled;

uniform sampler2D noise : filter_linear_mipmap;

void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float n = texture(noise, vec2(w.x * 0.05 + TIME * 0.02, w.z * 0.25 + TIME * 0.05)).r;
	float swell = 0.5 + 0.5 * sin(TIME * 0.9 + w.x * 0.11);
	float across = smoothstep(0.0, 0.35, UV.y) * smoothstep(1.0, 0.55, UV.y);
	ALBEDO = vec3(0.95, 0.97, 0.96);
	ALPHA = clamp(n * 1.5 - 0.45 + 0.35 * swell, 0.0, 0.85) * across;
	ROUGHNESS = 0.6;
}
