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
| `edit8` | `title titleCol right wide rows active hot` | the dense sound editor: up to 8 parameters as two rows of four cells (KNOB 1–4 each), an optional full-width graphic (`wide`: an AHDSR envelope, a filter response or a wave) above them; the `active` row (the one on the knobs) in the knob colours with a bar under each cell, the other row grey. See **Sound editor panels** |
| `stack` | `title titleCol right cols rows active hot` | N = 1–8 equal rows of four cells under column headings (oscillators, LFOs, the 8-slot mod matrix), a row label at the left; the `active` row in the knob colours, the others grey. See **Sound editor panels** |

### Sound editor panels (`edit8`, `stack`)

Both are drawn for the full 240 × 240 screen: give them `header: null`, `cards: null`, `footer: null`
(if the state sets a header, cards or a footer they are drawn as usual and the layout below is squeezed
vertically into the remaining panel).

**Shared.** The top line (y 0–24): `title` left in 13 px bold (`titleCol`, default white; a trailing
`*` means "edited"), `right` right-aligned in 11 px grey. A **cell** is `null` (empty) or
`{ label, value, col, glyph, pct, bipolar, env, cycles, n, wave, shape }`:

- `col` its knob colour; without it the colour is taken by column index: **blue, orange, white, green**
  (KNOB 1–4; palettes without those names fall back to theme / accent / text / mint).
- `glyph` one of the `params` glyphs `knob bar env wave saw square filter steps dots` (same fields:
  `pct`, `env`, `cycles`, `n`), drawn small; omitted or `"none"` = a text cell.
- `pct` 0–1: drives the glyph; a text cell (no glyph) draws it as a small horizontal bar.
- `bipolar: true`: the bar is centre-zero, **`pct` 0.5 = zero** (0 = full negative, 1 = full positive);
  with `glyph: "bar"` the vertical bar grows up / down from the middle.
- `wave` (optional, `SAW SQR TRI SIN PWM NOIS`, with `shape` 0–1 = PWM duty / TRI peak and `cycles`,
  default 1): draws that oscillator shape instead of a `glyph`.
- **`active`** (row index) is the row that is on KNOB 1–4: its labels, glyphs and values are in the knob
  colours and a 2 px bar in that colour sits under each cell. Every other row is drawn in the palette's
  `dim` grey with no bar. **`hot`** `[row, col]` (or `null`) is the parameter just turned: a filled block
  in the cell's colour behind its value (the value in the background colour).

**`edit8`**: `rows` = 1 or 2 arrays of 4 cells; `active` 0 | 1; `wide` = one of

- `{ "type": "env", "a", "h", "d", "s", "r", "seg", "col" }` (all 0–1): one wide AHDSR line (3 px, white)
  over a faint baseline, the sustain a flat run; segment `seg` (0 A, 1 H, 2 D, 3 S, 4 R; `null` = none)
  thicker in `col` (default: the colour of the `hot` cell, else the knob colour of column `seg % 4`),
  segment letters A H D S R under the baseline.
- `{ "type": "filter", "cut", "res", "ftype": "LP"|"BP"|"HP"|"NOTCH", "drive", "col" }` (`cut res drive`
  0–1, cutoff on a 9-octave log axis): the response curve (3 px, orange = KNOB 2) with its resonance
  peak over a dashed 0 dB pass level; `ftype` top left, `DRIVE n` top right when `drive` > 0.
- `{ "type": "wave", "wave": "SAW"|"SQR"|"TRI"|"SIN"|"PWM"|"NOIS", "shape", "cycles", "col" }`: two
  cycles (default) across the screen (3 px, blue = KNOB 1).
- `null` / omitted: no band, the rows get the room and larger glyphs.

Layout (cells 60 px wide at x = 60·c): with `wide` — title 0–24, wide band 24–120, row A 124–180,
row B 184–240 (label 10 px, glyph 22 px, value 13 px bold); without — row A 30–130, row B 134–234
(label 12 px, glyph 34 px, value 17 px bold).

```json
"screen": { "header": null, "cards": null, "footer": null, "panel": {
  "kind": "edit8", "title": "WARM PAD*", "right": "AMP ENV · 1/2",
  "wide": { "type": "env", "a": 0.2, "h": 0.0, "d": 0.3, "s": 0.7, "r": 0.4, "seg": 2 },
  "rows": [
    [ { "label": "Attack", "value": "0.20", "glyph": "knob", "pct": 0.2 },
      { "label": "Hold", "value": "0.00", "glyph": "knob", "pct": 0.0 },
      { "label": "Decay", "value": "0.30", "glyph": "knob", "pct": 0.3 },
      { "label": "Sustain", "value": "70", "glyph": "bar", "pct": 0.7 } ],
    [ { "label": "Release", "value": "0.40", "glyph": "knob", "pct": 0.4 },
      { "label": "Env amt", "value": "+32", "glyph": "bar", "pct": 0.756, "bipolar": true },
      { "label": "Vel", "value": "50", "pct": 0.5 },
      null ] ],
  "active": 0, "hot": [0, 2] } }
```

**`stack`**: `cols` = up to 4 column headings (10 px grey; `""` = none); `rows` = 1–8
`{ "label": "OSC 1", "cells": [cell × 4] }`; `active` the row on the knobs. The rows share y 41–239
equally under the headings (y ≈ 36); a row label column (11 px bold, white when active, else grey) is
as wide as the longest `label` (max 44 px) and the four cells share the rest. A cell's own `label` is not
drawn (the column heading names it). With rows ≥ 30 px (N ≤ 6): a glyph cell (`saw square wave dots
steps knob env filter`, or `wave`) draws the glyph with its `value` under it; a text cell (no glyph, or
`glyph: "bar"`) draws its `value` (15 px bold, 13 px under 45 px rows) with a 3 px `pct` bar under it.
With rows < 30 px (N = 7–8, ~24.75 px: the mod matrix) every cell is text only: the `value` in 12 px
bold and a 2 px `pct` bar (centre-zero with `bipolar`). The active-row knob bar is 2 px at the bottom of
each cell; rows are separated by a 1 px line.

```json
"screen": { "header": null, "cards": null, "footer": null, "panel": {
  "kind": "stack", "title": "WARM PAD*", "right": "OSC · 1/1", "titleCol": "white",
  "cols": ["Wave", "Level", "Coarse", "Fine"],
  "rows": [
    { "label": "1", "cells": [ { "value": "SAW", "glyph": "saw" }, { "value": "90%", "glyph": "bar", "pct": 0.9 }, { "value": "0" }, { "value": "+3" } ] },
    { "label": "2", "cells": [ { "value": "PWM", "glyph": "square", "pct": 0.55 }, { "value": "70%", "glyph": "bar", "pct": 0.7 }, { "value": "+12" }, { "value": "-5" } ] },
    { "label": "3", "cells": [ { "value": "SIN", "glyph": "wave" }, { "value": "40%", "glyph": "bar", "pct": 0.4 }, { "value": "-12" }, { "value": "0" } ] },
    { "label": "4", "cells": [ { "value": "NOIS", "glyph": "dots", "pct": 0.5 }, { "value": "0%", "glyph": "bar", "pct": 0 }, { "value": "0" }, { "value": "0" } ] } ],
  "active": 1, "hot": [1, 2] } }
```

The mod matrix (8 rows, text only, a bipolar amount):

```json
"panel": { "kind": "stack", "title": "WARM PAD*", "right": "MOD 1", "cols": ["Source", "Dest", "Amount", ""],
  "rows": [ { "label": "1", "cells": [ { "value": "LFO1" }, { "value": "CUT" }, { "value": "+24", "pct": 0.62, "bipolar": true }, null ] },
            { "label": "2", "cells": [ { "value": "–" }, { "value": "–" }, { "value": "–" }, null ] },
            "… 8 rows …" ],
  "active": 0, "hot": null }
```

[examples/edit8-smoke.json](examples/edit8-smoke.json) has one of each (env, filter and wave bands, no
band, a stack of 4, the 8-row mod matrix);
[examples/choralroot-fm1-sound-editor-mockups.json](examples/choralroot-fm1-sound-editor-mockups.json)
is the ChoralRoot sound editor built from them.

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
