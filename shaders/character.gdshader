// Meshy character material, plus a gentle sway in the hair: it trails a little as she moves and
// settles when she stops. Hair is found by colour (chestnut brown) above shoulder height.
// It can also recolour parts of a character (hair, top, trousers...), so the same model can be
// someone else: up to three swaps, each a band of colour (hue range in degrees, minimum and maximum
// saturation and brightness) between two heights above her feet, repainted in a new colour keeping
// its shading. And it can hide whatever stands beside her feet (the watering can Rosa's model came with).
shader_type spatial;

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap;
uniform sampler2D orm_tex : hint_default_white, filter_linear_mipmap;   // glTF: G = roughness, B = metallic
uniform sampler2D normal_tex : hint_normal, filter_linear_mipmap;
uniform bool has_orm = false;
uniform bool has_normal = false;

uniform vec3 hair_offset = vec3(0.0);   // world space, metres, set every frame from main.gd
uniform float ground_y = 0.0;           // her feet, world space
uniform float head_top = 1.7;
uniform float hair_start = 0.95;        // nothing below this height moves
uniform bool hair_mask = false;         // the hair is marked in the vertex colours' alpha (main.hair_mask(): Sandra)

// recolouring: band = (hue from, hue to, saturation min, brightness max); limits = (saturation max,
// brightness min, height from, height to); colour; ref = the brightness that maps to the new colour
uniform int swaps = 0;
uniform vec4 swap0_band; uniform vec4 swap0_limits; uniform vec3 swap0_col : source_color; uniform float swap0_ref = 0.5;
uniform vec4 swap1_band; uniform vec4 swap1_limits; uniform vec3 swap1_col : source_color; uniform float swap1_ref = 0.5;
uniform vec4 swap2_band; uniform vec4 swap2_limits; uniform vec3 swap2_col : source_color; uniform float swap2_ref = 0.5;
// (round 39) the face — eyes, brows, mouth — keeps its own colours whatever the swaps: a band of heights above the feet,
// out to so far each side (model units), on what faces forwards (npcs.gd FACE)
uniform bool face_on = false;
uniform vec2 face_y = vec2(0.0);
uniform float face_w = 0.0;
uniform float top_shift = 0.0;           // turn the greens of her top round the colour wheel (degrees)...
uniform vec2 top_zone = vec2(0.42, 0.98);  // ...between these heights
uniform bool hide_side = false;          // hide anything low down, off to her side
uniform vec3 root_pos = vec3(0.0);       // her feet and her right, world space (set every frame)
uniform vec3 root_right = vec3(1.0, 0.0, 0.0);

uniform bool cap_on = false;            // a hat on: the hair under it is tucked in, inside the hat (model units)
uniform vec3 cap_c = vec3(0.0, 1.6, 0.0);   // the middle of the hat's rim
uniform vec3 cap_r = vec3(0.12, 0.12, 0.12);  // how far the hat reaches out (and up) from there
uniform bool apron_on = false;          // an apron painted on her front, chest to knee (the 2D shopkeepers')
uniform vec3 apron_col : source_color = vec3(0.95, 0.93, 0.88);
uniform vec2 apron_zone = vec2(0.3, 0.8);  // heights it runs between (metres above her feet)
uniform float apron_w = 0.2;            // half its width, in the model's own units

varying float height;
varying float front;                     // how much this bit faces forwards (+z in the model)
varying float side;                      // how far out to the side it is (model units)
varying float on_face;                   // 1 on the face (face_*): not recoloured

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float h = wp.y - ground_y;
	height = h;
	front = normalize(NORMAL).z;
	side = abs(VERTEX.x);
	on_face = (face_on && h >= face_y.x && h <= face_y.y && side < face_w && front > 0.2) ? 1.0 : 0.0;
	if (hide_side) {
		vec3 rel = wp - root_pos;
		if (abs(dot(rel, root_right)) > 0.24 && rel.y < 0.42) {
			VERTEX = (inverse(MODEL_MATRIX) * vec4(root_pos - vec3(0.0, 3.0, 0.0), 1.0)).xyz;
		}
	}
	if (cap_on && VERTEX.y > cap_c.y - cap_r.y * 0.15) {
		// anything of the head poking out of the hat (hair, a bun) is drawn back in under it; just below
		// the rim it eases in a little too, so no tuft shows round the edge
		vec3 q = (VERTEX - cap_c) / cap_r;
		q.y = max(q.y, 0.0);
		float L = length(q);
		float lim = VERTEX.y > cap_c.y ? 0.9 : mix(1.05, 0.9, clamp((VERTEX.y - (cap_c.y - cap_r.y * 0.15)) / (cap_r.y * 0.15), 0.0, 1.0));
		if (L > lim) {
			vec3 d = VERTEX - cap_c;
			float k = lim / L;
			VERTEX = cap_c + vec3(d.x * k, VERTEX.y > cap_c.y ? d.y * k : d.y, d.z * k);
		}
	}
	if (h > hair_start) {
		vec3 c = textureLod(albedo_tex, UV, 0.0).rgb;
		float mx = max(c.r, max(c.g, c.b));
		float mn = min(c.r, min(c.g, c.b));
		float sat = mx > 0.0 ? (mx - mn) / mx : 0.0;
		bool brown = hair_mask ? COLOR.a > 0.5 : (c.r >= c.g && c.g >= c.b * 0.9 && sat > 0.35 && mx > 0.12 && mx < 0.66);
		if (brown) {
			// the crown stays put; the lengths of hair move more the further down they hang
			float w = clamp((head_top - h) / 0.55, 0.0, 1.0);
			vec3 local = (inverse(MODEL_MATRIX) * vec4(hair_offset, 0.0)).xyz;
			VERTEX += local * w * w;
		}
	}
}

vec3 hsv(vec3 c) {
	float mx = max(c.r, max(c.g, c.b));
	float mn = min(c.r, min(c.g, c.b));
	float d = mx - mn;
	float h = 0.0;
	if (d > 1e-5) {
		if (mx == c.r) { h = mod((c.g - c.b) / d, 6.0); }
		else if (mx == c.g) { h = (c.b - c.r) / d + 2.0; }
		else { h = (c.r - c.g) / d + 4.0; }
	}
	return vec3(h * 60.0, mx > 0.0 ? d / mx : 0.0, mx);
}

bool in_band(vec3 q, vec4 band, vec4 limits, float h) {
	bool hue_ok = band.x <= band.y ? (q.x >= band.x && q.x <= band.y) : (q.x >= band.x || q.x <= band.y);
	return hue_ok && q.y >= band.z && q.y <= limits.x && q.z <= band.w && q.z >= limits.y && h >= limits.z && h <= limits.w;
}

vec3 rgb_of(vec3 q) {
	float h = mod(q.x, 360.0) / 60.0;
	float c = q.z * q.y;
	float x = c * (1.0 - abs(mod(h, 2.0) - 1.0));
	vec3 r = h < 1.0 ? vec3(c, x, 0.0) : h < 2.0 ? vec3(x, c, 0.0) : h < 3.0 ? vec3(0.0, c, x)
		: h < 4.0 ? vec3(0.0, x, c) : h < 5.0 ? vec3(x, 0.0, c) : vec3(c, 0.0, x);
	return r + vec3(q.z - c);
}

vec3 repaint(vec3 c, vec3 col, float ref) {
	// (round 41, the user: "the other guy's shirt is flickering… It can't be a pattern") the cloth's own weave is not
	// kept: only its broad shading (c here is the softened sample), within a narrow range
	float lum = dot(c, vec3(0.3, 0.59, 0.11));
	return col * clamp(lum / ref, 0.7, 1.2);
}

void fragment() {
	vec4 c = texture(albedo_tex, UV);
	ALBEDO = c.rgb;
	if (swaps > 0 && on_face < 0.5) {
		// (round 41: tested and painted on a softened sample — a coarser mip — so a patterned cloth's threads don't fall in
		// and out of the band one by one and shimmer as she moves)
		vec4 cs = texture(albedo_tex, UV, 2.5);
		vec3 q = hsv(cs.rgb);
		if (in_band(q, swap0_band, swap0_limits, height)) { ALBEDO = repaint(cs.rgb, swap0_col, swap0_ref); }
		else if (swaps > 1 && in_band(q, swap1_band, swap1_limits, height)) { ALBEDO = repaint(cs.rgb, swap1_col, swap1_ref); }
		else if (swaps > 2 && in_band(q, swap2_band, swap2_limits, height)) { ALBEDO = repaint(cs.rgb, swap2_col, swap2_ref); }
	}
	if (apron_on && height > apron_zone.x && height < apron_zone.y && front > 0.2 && side < apron_w) {
		float edge = smoothstep(apron_w, apron_w * 0.85, side);      // a soft hem at the sides
		ALBEDO = mix(ALBEDO, apron_col * (0.85 + 0.15 * front), edge);
	}
	if (top_shift != 0.0 && height > top_zone.x && height < top_zone.y) {
		vec3 q = hsv(ALBEDO);
		if (q.x > 60.0 && q.x < 200.0 && q.z > 0.12) {     // the greens of her top and its pattern
			q.x += top_shift;
			q.y = max(q.y, 0.4);              // even a pale top takes on a colour
			q.z *= 0.92;
			ALBEDO = rgb_of(q);
		}
	}
	if (has_orm) {
		vec3 orm = texture(orm_tex, UV).rgb;
		ROUGHNESS = orm.g;
		METALLIC = orm.b;
	} else {
		ROUGHNESS = 0.7;
	}
	if (has_normal) {
		NORMAL_MAP = texture(normal_tex, UV).rgb;
	}
}
