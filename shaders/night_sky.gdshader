// The sky at every hour, so day turns to night without a cut: a blue gradient by day with a small sun;
// at sunrise and sunset a warm glow and a bright horizon on the sun's side only; by night ("night" 1) a deep
// blue down to the horizon, stars, and the full moon with its grey seas.
shader_type sky;

uniform vec3 top_color : source_color = vec3(0.02, 0.035, 0.09);
uniform vec3 horizon_color : source_color = vec3(0.1, 0.11, 0.2);
uniform vec3 glow_color : source_color = vec3(0.32, 0.2, 0.15);   // the horizon glow towards the sun (city light at night)
uniform vec3 sun_color : source_color = vec3(1.0, 0.9, 0.7);
uniform vec3 moon_color : source_color = vec3(0.93, 0.94, 0.92);   // pale, not yellow
uniform vec3 sun_dir = vec3(0.0, 1.0, 0.0);
uniform vec3 moon_dir = vec3(0.0, -1.0, 0.0);
uniform float night = 0.0;
uniform float moon_size = 0.035;       // radians
uniform float sun_size = 0.03;
// looking towards the sun (main.gd update_glare): its light floods the sky, and only the sky. Round 38, the user:
// the glare over the whole view dimmed and lifted everything; the trees and buildings in front keep their own
// light, and only the sky between the leaves and past the rooftops shines
uniform float glare = 0.0;
uniform float glare_high = 1.0;          // 0 on the horizon .. 1 well up in the sky
uniform vec3 glare_tint = vec3(1.0, 0.92, 0.78);       // (as the finished picture's colour, sRGB)
uniform vec2 sun_uv = vec2(0.5);         // the sun's place on screen
uniform float aspect = 1.6;
uniform float exposure = 1.0;            // the environment's exposure and filmic white (main.gd), to work back through
uniform float white = 6.0;

// Godot's filmic curve (tonemap_filmic) and its inverse, and the sRGB curve both ways
const float FA = 0.22 * 4.0;
const float FB = 0.30 * 2.0;
const float FC = 0.10;
const float FD = 0.20;
const float FE = 0.01;
const float FF = 0.30;
float film1(float c) {
	return (c * (FA * c + FC * FB) + FD * FE) / (c * (FA * c + FB) + FD * FF) - FE / FF;
}
vec3 filmic(vec3 c) {
	float w = film1(white);
	return vec3(film1(max(c.r, 0.0)), film1(max(c.g, 0.0)), film1(max(c.b, 0.0))) / w;
}
float unfilm1(float y) {
	float t = y * film1(white) + FE / FF;
	float a = FA * (1.0 - t);
	float b = FC * FB - t * FB;
	float cc = FD * FE - t * FD * FF;
	if (abs(a) < 1e-5) {
		return -cc / b;
	}
	return (-b + sqrt(max(b * b - 4.0 * a * cc, 0.0))) / (2.0 * a);
}
vec3 unfilmic(vec3 y) {
	return vec3(unfilm1(y.r), unfilm1(y.g), unfilm1(y.b));
}
vec3 to_srgb(vec3 c) {
	c = clamp(c, 0.0, 1.0);
	return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c));
}
vec3 to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

float hash(vec3 p) {
	p = fract(p * 0.3183099 + 0.1);
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

void sky() {
	vec3 d = normalize(EYEDIR);
	float up = clamp(d.y, 0.0, 1.0);
	vec3 sd = normalize(sun_dir);
	vec2 dh = normalize(d.xz + vec2(1e-4));
	vec2 sh = normalize(sd.xz + vec2(1e-4));
	// (round 20e, the user's wish: with the sun low, morning and evening, the horizon is bright and warm only on
	// its side, the east at sunrise and the west at sunset; the other way it is a soft, hazy blue)
	float low = (1.0 - smoothstep(0.08, 0.45, sd.y)) * (1.0 - smoothstep(0.6, 1.0, night));
	float sunward = mix(1.0, smoothstep(-0.3, 0.6, dot(dh, sh)), low);
	vec3 far_side = mix(top_color, vec3(dot(horizon_color, vec3(0.3, 0.5, 0.2))) * vec3(0.82, 0.9, 1.05), 0.45);
	vec3 hor = mix(far_side, horizon_color, sunward);
	// horizon to zenith through a pale, slightly warm band rather than straight across: an orange horizon
	// blended straight into a blue top went through mauve, and the sunset read as magenta
	vec3 pale = mix(hor, top_color, 0.5);
	float lum = dot(pale, vec3(0.3, 0.5, 0.2));
	pale = mix(pale, vec3(lum) * vec3(1.06, 1.0, 0.84), 0.7 * (1.0 - night) * sunward);  // a creamy band low down
	vec3 high = mix(top_color, vec3(dot(top_color, vec3(0.3, 0.5, 0.2))) * vec3(0.8, 1.02, 1.12), 0.5 * (1.0 - night));   // then clear, slightly cyan blue
	high = mix(high, top_color, 0.35);
	float u = pow(up, 0.45);
	vec3 col = u < 0.3 ? mix(hor, pale, u / 0.3) : (u < 0.65 ? mix(pale, high, (u - 0.3) / 0.35) : mix(high, top_color, (u - 0.65) / 0.35));
	// the glow low in the sky: towards the sun by day and at dusk; none at night (round 20e, the user: the warm
	// city glow all round the horizon read as a purple blur; the night sky is just dark blue down to it)
	float towards = max(dot(dh, sh), 0.0);
	float side = (0.15 * (1.0 - low) + 0.85 * pow(towards, 3.0)) * (1.0 - smoothstep(0.6, 1.0, night));
	col += glow_color * side * exp(-max(d.y, 0.0) * 6.0);
	if (d.y < 0.0) {
		// (round 26: below the horizon the sky stays the haze's own colour, so the far land, fogged to the same
		// haze, fades into it instead of ending at a dark blue "sea")
		col = mix(hor, hor * 0.9 + top_color * 0.05, clamp(-d.y * 4.0, 0.0, 1.0));
	}
	// the sun: a small bright disc with a soft, tight halo (not a big fuzzy ball)
	float cs = dot(d, sd);
	float sun_up = smoothstep(-0.03, 0.02, sd.y) * (1.0 - night);
	float sdisc = smoothstep(cos(sun_size), cos(sun_size * 0.8), cs);
	// (the disc far brighter than anything else, so the bloom catches it and it shines rather than sitting
	// there as a flat white ball; round it a hot corona and a wide soft glow in the sun's own colour)
	// (low on the horizon, through far more air, it is much dimmer: a disc you can nearly look at, not a
	// blinding burst that the bloom smears over everything in front of it)
	float sun_hi = smoothstep(0.0, 0.4, sd.y);
	// (round 23, the user: an hour after sunrise the sun was "a bomb": the disc and corona dimmer, so the bloom round
	// them stays small; the dazzle is the glare below, over the sky alone since round 38)
	col += sun_color * sun_up * (sdisc * mix(1.4, 4.0, sun_hi) + pow(max(cs, 0.0), 2500.0) * mix(0.4, 1.2, sun_hi)
		+ pow(max(cs, 0.0), 300.0) * mix(0.2, 0.35, sun_hi) + pow(max(cs, 0.0), 40.0) * 0.08);
	// the moon, kept just under the glow threshold: a clear pale disc with its grey seas
	vec3 m = normalize(moon_dir);
	float c = dot(d, m);
	float moon_vis = smoothstep(0.25, 0.75, night) * smoothstep(-0.03, 0.02, m.y);
	float disc = smoothstep(cos(moon_size), cos(moon_size * 0.85), c) * moon_vis;
	col += moon_color * moon_vis * pow(max(c, 0.0), 4000.0) * 0.06;     // (only the faintest rim of light: no fuzzy halo)
	vec3 mside = normalize(cross(m, vec3(0.0, 1.0, 0.0)));
	vec3 upm = cross(mside, m);
	vec2 q = vec2(dot(d, mside), dot(d, upm)) / moon_size;
	float seas = smoothstep(0.32, 0.18, length(q - vec2(-0.25, 0.2))) * 0.55 + smoothstep(0.26, 0.12, length(q - vec2(0.2, -0.05))) * 0.45
		+ smoothstep(0.2, 0.08, length(q - vec2(-0.05, -0.38))) * 0.35;
	col = mix(col, moon_color * 0.82 * (1.0 - 0.22 * seas), disc);
	// the stars come out as the last of the red goes
	float stars = smoothstep(0.6, 0.95, night);
	if (!AT_CUBEMAP_PASS && stars > 0.0 && d.y > 0.05 && disc < 0.01) {
		vec3 cell = floor(d * 260.0);
		float h = hash(cell);
		if (h > 0.9965) {
			vec3 ctr = (cell + 0.5) / 260.0;
			float s = smoothstep(0.0022, 0.0, length(d - normalize(ctr)));
			col += vec3(0.85, 0.88, 1.0) * s * stars * (0.6 + 1.4 * fract(h * 97.0)) * smoothstep(0.05, 0.35, d.y);
		}
	}
	if (!AT_CUBEMAP_PASS && glare > 0.0) {
		// (not in the cubemap the ground's light is taken from: it must not brighten the scene as she turns)
		// Round 38: the user liked the old glare's sky ("Before whole picture is good") but not what it did to the
		// trees and buildings in front. So the sky gets exactly the old veil (sun_glare.gdshader: a soft core, a broad
		// halo, an even wash, added to the finished picture), worked out backwards through the exposure and the
		// filmic curve so it comes out the same once tonemapped; whatever stands in front of the sky is untouched.
		vec2 dd = (SCREEN_UV - sun_uv) * vec2(aspect, 1.0);
		float r = length(dd);
		float core = exp(-r * r * 60.0) * mix(0.06, 0.22, glare_high);
		float halo = exp(-r * mix(1.1, 1.6, glare_high)) * mix(0.2, 0.28, glare_high);
		float wash = mix(0.14, 0.24, glare_high);
		vec3 veil = glare_tint * (core + halo + wash) * glare;
		vec3 shown = to_srgb(filmic(col * exposure));
		vec3 want = min(shown + veil, vec3(0.985));
		col = max(col, unfilmic(to_linear(want)) / exposure);
	}
	COLOR = col;
}
