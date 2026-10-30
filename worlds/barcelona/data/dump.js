
// ---- appended by extract.sh: build the world as boot() does, then print everything as JSON ----
genTiles(); genObjects();
const gy_ = HSTREETS[2].y + 1; let gx_ = 1; for (let x = 0; x < CITY_X0; x++) if (tileAt(x, gy_) === G.BRIDGE) gx_ = x;
var GUARD = { x: gx_, y: gy_ };
const tileNames = {}; for (const k in G) tileNames[G[k]] = k;
const rows = []; for (let y = 0; y < MH; y++) { let r = []; for (let x = 0; x < MW; x++) r.push(tiles[idx(x, y)]); rows.push(r); }
print(JSON.stringify({
  MW, MH, BCOLS, BROWS, BLOCK, VSTREETS, HSTREETS, SEGMENT_NAMES, CITY: [CITY_X0, CITY_Y0, CITY_X1, CITY_Y1],
  RAMBLA_PROM, RAMBLA_EXT_END, PASSEIG_Y1, TIBIDABO, SPAWN, GUARD, tileNames, tiles: rows,
  objects: worldObjs, BUILDINGS, ITEMS, SHOPS, EAT_MSG, BIN_MSGS, ACHIEVEMENTS, IDLE_LINES, BOOKS, NOTES, EXAM,
  SANDRA_LOOK, NPCS, TRUFA, PFAND_TIP, OPEN_MISSIONS, MISSIONS, NOTE_GIVE, ORIOL_STATES, PHONE, INTRO_TEXT,
  INTERIORS, CONTAINERS, TIBIDABO_PLAQUE,
  coast: Array.from({ length: MW * 2 }, (_, i) => coastY(i / 2)), beach: Array.from({ length: MW * 2 }, (_, i) => beachY(i / 2)),
  mount: Array.from({ length: MW * 2 }, (_, i) => mountY(i / 2)), river: Array.from({ length: MH * 2 }, (_, i) => riverX(i / 2)),
  forest: Array.from({ length: MH * 2 }, (_, i) => forestX(i / 2)),
}, (k, v) => typeof v === 'function' ? undefined : v));
