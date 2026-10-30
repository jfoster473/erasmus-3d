// A soft warm glow round a door that can be walked through: brightest at the edge of the opening,
// fading out over the wall around it, with a faint wash over the door itself.
// Kept steady: it is mixed over the wall rather than added to it (added light pushed bright walls over
// the bloom threshold, which shimmered as the camera moved), every edge is soft, and it fades to nothing
// before the card's own edges.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, shadows_disabled, fog_disabled;

uniform vec2 opening = vec2(1.24, 2.24);   // the door, metres
uniform vec2 card = vec2(2.6, 3.6);        // the card the glow is drawn on, centred on the door
uniform vec3 colour : source_color = vec3(1.0, 0.8, 0.52);
uniform float strength = 0.5;
uniform float reach = 0.3;                // how far it spreads over the wall, metres
uniform float arch = 0.0;                 // (round 33) the door's curved top, metres: 0 square, w/2 round, its height parabolic

float box_d(vec2 p, vec2 half_size, float r) {
	vec2 q = abs(p) - half_size + r;
	return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	vec2 p = (UV - 0.5) * card;
	p.y = -p.y;                                                         // (up)
	float d;
	if (arch <= 0.01) {
		d = box_d(p, opening * 0.5, 0.12);                               // distance from the rounded edge
	} else {
		// (round 33, the user: "it is a glowing door… put the shaped frame in there") the door's own shape: its
		// straight part and the curve over it, as one outline
		float a = min(arch, opening.y);
		float hs = (opening.y - a) * 0.5;
		float db = hs > 0.01 ? box_d(p - vec2(0.0, -a * 0.5), vec2(opening.x * 0.5, hs + 0.001), 0.05) : 1e3;
		vec2 c = p - vec2(0.0, opening.y * 0.5 - a);
		vec2 r = vec2(opening.x * 0.5, a);
		float de = (length(c / r) - 1.0) * min(r.x, r.y);
		de = c.y < 0.0 ? max(de, -c.y - 0.001) : de;                  // (only the curve counts above its foot)
		d = min(db, de);
	}
	float g = d > 0.0 ? exp(-d / reach) : 0.1 + 0.9 * exp(d / 0.22);
	vec2 e = (card * 0.5 - abs(p)) / 0.35;                              // fade out before the card's edges
	g *= clamp(min(e.x, e.y), 0.0, 1.0);
	ALBEDO = colour;
	ALPHA = clamp(g * strength, 0.0, 0.85);
}
