// Looking towards the sun: not a lens flare's rings and streaks, just its light, the way the sun floods
// your eyes. A soft core round the sun, a wide halo, and a wash over the whole view that lifts the darks
// (veiling glare), so things near the sun are hard to make out. Added on top of the picture, under the HUD;
// main.gd sets where the sun is on screen, how strongly it shines in (0 when it's hidden) and how high it
// is: high in the sky it is hard to look at (a bright core); low on the horizon, through more air, it is
// dimmer and redder and the light spreads wide and soft rather than bursting from one point (round 20).
shader_type canvas_item;
render_mode blend_add;

uniform vec2 sun_uv = vec2(0.5);       // the sun's place on screen (0..1, may be off the edge)
uniform float strength = 0.0;
uniform float high = 1.0;              // 0 on the horizon .. 1 well up in the sky
uniform vec3 tint : source_color = vec3(1.0, 0.92, 0.78);
uniform float aspect = 1.6;

void fragment() {
	vec2 d = (SCREEN_UV - sun_uv) * vec2(aspect, 1.0);
	float r = length(d);
	// (round 23, the user: "the brightness should cover most of the screen, like it is actual glare, not turn the sun
	// into a bomb"): only a small, soft core; most of it a broad halo and an even veil over the whole view
	float core = exp(-r * r * 60.0) * mix(0.06, 0.22, high);
	float halo = exp(-r * mix(1.1, 1.6, high)) * mix(0.2, 0.28, high);
	float wash = mix(0.14, 0.24, high);
	vec3 c = tint * (core + halo + wash) * strength;
	COLOR = vec4(c, 1.0);
}
