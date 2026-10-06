# fm1-panel-design JSON format

Interchange format for M-VAVE FM-1 panel and screen designs, produced and consumed by
[index.html](index.html) (the ChoralRoot FM-1 designer). Hand this file (or just the JSON) to Claude
when asking it to read or generate a design. [examples/choralroot-fm1-mockups.json](examples/choralroot-fm1-mockups.json)
is a complete, 16-state example (the ChoralRoot firmware's interface sketch).

## Hardware conventions

The [M-VAVE FM-1](../MWaveFM1Reference/FM-1-manual.pdf) is a 27-key silicone-keybed synth with a 2×6
block of function buttons, OCT−/OCT+, seven endless encoders, a volume pot and a 1.54" 240×240 TFT.
Everything below matches the open firmwares for it ([Felucca](https://github.com/hugelton/Felucca),
`firmware/hal/fm1_input.h`, `src/panel.c`, `src/seq.c`).

- **27 keys, key index 0–26 = F3 … G5**, MIDI note `53 + index` (the firmware's `fm1_in.notes` bit n).
  Black keys are indices 1 3 5 8 10 13 15 17 20 22 25 (`key_black(k) = (0x54A >> ((k+5)%12)) & 1`).
  The black keys carry the stock prints OP1–OP6, PIT, GLO, MONO, POLY.
  **Every key has one white LED.**
- **14 buttons by id**: top row `FX SEL ENV LFO EDIT GLO`, bottom row `HOME SAVE ARP SEQ PLAY REC`,
  and `OCT-` `OCT+`. Each has an LED: white, except **REC red** and **PLAY orange**; PLAY also has a
  **second, green LED** (`playGreen`, the transport light).
- **LED levels** are integers: `0` off, `1` dim (Felucca's idle glow, `fm1_led_dim`), `2` lit
  (`fm1_led`), `3` blinking (lit / dark at ~2 Hz). The names `"off" "dim" "lit" "blink"` load too.
- **8 rotary controls by id**: `MASTER` (a potentiometer: the volume), `SELECT`, `PRESETS`,
  `ALGORITHM`, `KNOB1`–`KNOB4` (endless encoders, **no push switches**). They carry text only: what
  turning does, and an optional value shown under the knob.
- **The screen** is a structured 240×240 mock-up in one of Felucca's eight palettes, laid out as the
  Felucca UI (`src/ui.c`): header rows 0–24, four knob cards 28–72 (57×44 at x = 3 + 59·c), the
  panel 76–198, the footer 202–240. See **Screen** below.

## Schema (version 1)

A design holds **one or more states** (up to 24) — alternative pages, layers or moments of the same
hardware (idle, a chord held, a layer button held, the loop recording…). Every state describes all
27 key LEDs, all 14 button LEDs, the knobs and the screen.

```json
{
  "format": "fm1-panel-design",
  "version": 1,
  "device": "M-VAVE FM-1",
  "name": "my design",
  "palette": "CHORAL",
  "convention": "(human-readable restatement of the conventions above)",
  "keyMap": [ { "key": 0, "role": "white", "note": 53, "name": "F3" }, { "key": 1, "role": "black", "note": 54, "name": "F#3", "stock": "OP1" } ],
  "labels": {
    "buttons":  { "EDIT": "KEY", "ARP": "PERF", "PLAY": "LOOP" },
    "encoders": { "KNOB1": "VOICING", "PRESETS": "SOUND" }
  },
  "notes": "global notes: overall intent, how the states relate",
  "states": [
    {
      "state": 1,
      "name": "MAJ held, C4 pressed",
      "export": true,
      "notes": "free-text notes about this state",
      "keys": [1, 1, 1, "... exactly 27 levels 0-3, one per key index ..."],
      "keyLabels": { "1": "DIM", "0": "6", "9": "D" },
      "keyNotes":  { "9": "the root pressed" },
      "buttons": { "FX": 1, "SEL": 1, "ENV": 2, "LFO": 1, "EDIT": 1, "GLO": 1, "HOME": 1, "SAVE": 1, "ARP": 1, "SEQ": 1, "PLAY": 1, "REC": 1, "OCT-": 1, "OCT+": 1 },
      "playGreen": 0,
      "buttonLabels": { "EDIT": "KEY" },
      "buttonNotes":  { "EDIT": "held: the key layer" },
      "encoders": { "KNOB1": { "note": "chord voicing", "value": "+2" }, "SELECT": { "note": "", "value": "" } },
      "screen": { "...": "see below" }
    }
  ]
}
```

- `palette` is the design-wide screen palette: `MONO GREEN AMBER ICE VIOLET ROSE PAPER HI-CON`
  (Felucca's `tools/gen_ui_palettes.py`), `CHORAL` (cream, orange, coral, magenta, blue, teal, mint,
  navy, grey on a warm near-black) or `MOD` (ChoralRoot's: white, red, blue, yellow, orange, green,
  grey on black; the CHORAL names map onto it). A state's screen may override it. Anywhere a colour is
  taken (`col`, `cols`, `selCol`, `vcol`, `midCol`, `rightCol`, `lineCol`, `ringCol`, `messageCol`, a
  bubble's `col`, a lit key's `col`) it is one of those names, a token (`theme accent text mid dim rec`)
  or a hex; palettes without named colours map the names onto their theme / accent.
- `labels` relabels the printed controls for the whole design — what the firmware makes of each
  button and knob (the "overlay sticker"). A state's `buttonLabels` / `encoders[id].note` override
  them for that state (a layer that turns the keys and knobs into something else).
- **`keys`** is an array of **exactly 27** levels; `keys[i]` is key `i`'s LED.
- **`keyLabels`** is text printed on a key in that state (its function: `"C"`, `"STRUM"`, `"1"`);
  **`keyNotes`** are legend annotations (numbered badges). Both are keyed by key index as a string.
- **`buttons`** has every button id → level; `playGreen` 0/1 is PLAY's green LED.
- **`encoders`** has every rotary id → `{ note, value }`; `note` is what turning does, `value` an
  optional short value drawn under the knob. A plain string is accepted as `value`.
- `export` marks whether the state is included in the png exports (editor setting).
- `keyMap` is a static reference the designer emits so a reader knows every key's note.
- The loader is forgiving: missing fields default sensibly, levels clamp to 0–3, `leds` is an alias
  for `keys`, `keyNotes` may be an array of `{ key, text }`, and a single-state file (top-level
  `keys`) loads as a one-state design.

## Screen

```json
"screen": {
  "palette": null,
  "header": { "icon": "stop", "bpm": "120", "mid": "KEY  C MAJ", "right": "", "batt": 3, "usb": true, "rec": false, "hot": false },
  "cards": [ { "label": "VOICING", "value": "+2", "hot": true }, { "label": "BASS", "value": "0" }, { "label": "PERF", "value": "OFF" }, { "label": "FX", "value": "REV 25" } ],
  "panel": { "kind": "chord", "root": "C", "quality": "", "sup": "M7", "notes": "G4 B4 C5 E5", "key": "", "hint": "" },
  "footer": { "left": "12 PLUCK", "right": "BASS OFF" },
  "ring": 0.35, "ringRec": true,
  "message": "PANIC · all notes off",
  "note": "legend text for this screen"
}
```

- `header`: `icon` = `stop | play | rec | loop | none`; with `none` and no `bpm` the line is Orchid's bare top line (`mid` at the left in M size, `right` at the right); `bpm` the tempo (rendered with its unit, `unit:
  false` hides it; `hot` draws it in the accent colour); `rec` adds a red dot; `mid` is the message /
  layer name / key; `right` a short status (octave, transpose); `batt` 0–4 (4 = charging), `usb` true/false.
  `null` removes the header.
- `cards`: up to four `{ label, value, hot, sub }` for KNOB 1–4 (a hot card is the knob just turned,
  drawn in the accent colour; `sub` replaces the gauge dash with a small line). `null` removes the
  cards and gives the panel rows 28–198.
- `footer`: `{ text }` one centred line, or `{ left, right }` texts, optional `steps: { n, on, filled }` (a beat / position strip),
  **or** `{ hints: [ { key: "KEYS", act: "TONIC" }, { key: "OCT-", act: "BACK", on: false } ] }`
  drawn as keycap chips (Felucca's footer). `null` removes the footer.
- `ring` 0–1 draws Orchid's ring progress indicator: a dotted circle round the screen edge with the
  progress solid (`ringRec` in red; `0` draws just the track).
- `message` draws an inverted message box over the panel (`messageCol`); `ringCol` colours the ring.
- `panel.kind` selects the template:

| kind | fields | what it draws |
| --- | --- | --- |
| `chord` | `root quality sup notes line lineCol bubbles bubbleStyle cols squeeze block key trans hint size` | the chord name in the Orchid Standard Framework: root big, quality (`m`, `dim`, `sus`, `+`) after it, extensions (`M7`, `7 9`, `JAZZ`) as a superscript, coloured by `cols: { root, quality, sup }`; the name is squeezed horizontally to fit (`squeeze` 0–1 forces a factor: an animation frame); `bubbles` = the voiced notes as a coloured text line `[{ t, col, mark }]` (`bubbleStyle: "disc"` draws discs instead); `block` fills the panel with a colour; `line` a one-line note; `hint` when empty |
| `picker` | `items sel label col value title orient size` | one choice at a time: the current item huge (squeezed to fit), its neighbours peeking small and faded above and below (`orient: "h"`: left and right), square position marks, the value under it; items are strings or `{ t, v }` |
| `meter` | `value sub label col pct segments thick title size` | a knob's value huge in its colour over a stripe meter of `segments` blocks filled to `pct` |
| `stripes` | `bands band gap phase skew title titleSize titleCol titleY y sub` | mod racing stripes: bold horizontal bands in the `bands` colours, the name above; `phase` 0–1 slides them (an animation frame) |
| `roundel` | `rings title titleSize titleCol bandCol sub r cx cy` | the mod target: concentric rings in the `rings` colours (outer first) with a text band across the middle |
| `splash` | `bands width phase title titleCol titleSize sub xm` | a 70s ribbon: nested stripes in the `bands` colours along a rounded zig-zag; `phase` 0–1 slides it (an animation frame); the title in a corner |
| `dial` | `value sub label col pct size r` | a knob's value huge in its colour inside a 270° gauge with ticks (`pct` fills the gauge) |
| `params` | `title page col cols foot` | a sound-edit page: four columns for KNOB 1–4 in the knob colours (blue, orange, cream, coral), each `{ label, value, col, glyph, pct, env, cycles, n }` with `glyph` = `knob bar env wave saw square filter steps dots` |
| `arp` | `root quality sup cols notes pos hopCol line lineCol size` | a performance in motion: the chord name, its notes as coloured discs on a line, the sounding one (`pos`) lifted with a dotted hop arc to the next |
| `keyboard` | `root quality sup cols lit labels notes key title titleSize col` | the chord name (or a `title` in `col`) over a 27-key strip; `lit` = key indices, note names or `{ k, col }`; `labels` = { index: text } |
| `notes` | `root quality sup notes line key` | the chord name with each note in its own box |
| `geek` | `root quality sup notes lit lines key trans` | Geek Out: chord, the notes listed, status `lines`, the key strip |
| `tiles` | `title subtitle cols rows cells` | a layer map of tiles; a cell is `{ t, sub, on, acc, dim, off, mark }` or a string, `null` for a gap |
| `list` | `title subtitle items sel rowH big col vcol selCol` | a menu / browser; an item is `{ t, v, dim, col, vcol }` or a string; `sel` the selected row (scrolls into view); `big: true` = Orchid-style tall rows; `selCol` the selection bar, `col` / `vcol` the text and value colours (inside a `ring` the big list is inset) |
| `big` | `value label sub pct block col title size` | one huge value with its name under it (Orchid's dial screens); `sub` a second line; `pct` 0–1 draws the level as an inverted fill rising from the bottom; `block` fills the panel with a colour and sets the type in the background colour |
| `scope` | `root quality sup amp freq` | an oscilloscope wave (React view) |
| `text` | `title lines` | free lines; a line is `{ t, px, col: theme\|accent\|dim, center, w }` or a string |
| `loop` | `value label pct rec layers status title right` | the loop page: a ring with the bar count inside, layer rings, a status line |

`surface: false` on a panel drops its SURF card background (`chord`, `big`, `scope`, `notes` and
`geek` draw on the background by default).

## Tips for generating designs (for Claude)

- Compute the 27-entry `keys` array programmatically (key index = MIDI note − 53; the example
  is generated by `design/make_mockups.py` in the ChoralRootFM1 repo) and always emit the whole array.
- Use `1` (dim) as the resting level of every key and button — that is how Felucca-based firmware
  idles — `2` for what is held, sounding or active, `3` for a held layer button or an armed transport.
- Give every state the same `labels` (the sticker) and change `buttonLabels` / `keyLabels` /
  `encoders` only inside layers, where the controls really change job.
- Orchid-style screens are the norm for ChoralRoot: `cards: null`, `footer: null` (or one `text`
  line in a layer), `header` with `icon: "none"` and `bpm: ""`, and one `chord` / `big` / big `list`
  panel. The knob cards exist for Felucca-style pages.
- Keep `header.mid` short (`Key: C`, `Rec`); it is the Orchid's top-left text.
- Use `notes`, `keyNotes`, `buttonNotes` and the screen `note` to say what a state means and how it
  is entered and left; one state is one static moment.
