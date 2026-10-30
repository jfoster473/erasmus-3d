// A shaft of sunlight through stained glass, as a soft glowing cone: brightest down its middle, fading
// to nothing at its sides (so it never shows a hard edge), at the window it starts from and towards
// the floor it ends on, and as the camera comes close (so walking through it never fills the screen).
// A slow drift of brightness along it, like dust turning in the light.
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, shadows_disabled, fog_disabled;

uniform vec3 colour : source_color = vec3(1.0, 0.85, 0.6);
uniform float strength = 0.15;

varying float along;
varying vec3 wpos;

void vertex() {
	along = UV.y;                         // 0 at the window, 1 at the far end
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float face = abs(dot(normalize(NORMAL), normalize(VIEW)));
	float soft = face * face;
	float ends = smoothstep(0.0, 0.18, along) * (1.0 - smoothstep(0.45, 1.0, along));
	float near = smoothstep(0.6, 3.5, length(VERTEX));
	float dust = 0.82 + 0.18 * sin(TIME * 0.35 + wpos.x * 0.9 + wpos.y * 0.6 + wpos.z * 0.7)
		* sin(TIME * 0.21 + wpos.y * 1.3 - wpos.z * 0.5);
	ALBEDO = colour;
	ALPHA = clamp(soft * ends * near * dust * strength, 0.0, 1.0);
}
