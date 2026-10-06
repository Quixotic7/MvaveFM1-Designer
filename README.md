# ChoralRoot FM-1 designer

A visual editor for designing M-VAVE FM-1 panel states — the LEDs under the 27 keys and 14 buttons,
what the 8 knobs do, and a faithful mock-up of the 240×240 screen — plus a JSON interchange format
for sharing them with humans and LLMs. A sibling of the
[OMX-27 LED designer](https://github.com/quixotic7/OMX-LED-Designer) and the
[grid LED designer](https://github.com/quixotic7/grid-led-designer), adapted to the FM-1's mono LEDs,
its encoders and its colour screen. Built to design the ChoralRoot FM-1 firmware (an Orchid-style
chord instrument on Felucca's engines), useful for any FM-1 firmware.

No build, no dependencies — `index.html` is the whole app. Open it in a browser.

![example export: the ChoralRoot screens](docs/choralroot-fm1-screens.png)

## the hardware

The tool models the FM-1 as its open firmwares see it (Felucca's `fm1_input.h` / `panel.c` / `seq.c`):

- **27 keys F3–G5** (key index 0–26, MIDI note 53 + index), in their real capsule layout measured from
  the FM-1's own panel drawing, each with one **white LED**
- **12 function buttons** (`FX SEL ENV LFO EDIT GLO` / `HOME SAVE ARP SEQ PLAY REC`) and **OCT−/OCT+**,
  each with an LED — REC red, PLAY orange plus a separate green transport LED
- **7 endless encoders** (`SELECT PRESETS ALGORITHM KNOB1–4`, no push switches) and the **MASTER** pot
- the **1.54" 240×240 TFT**

## features

- **paint LED levels** — off / dim (the idle glow) / lit / blink — onto keys and buttons; drag to paint
  a run, right-drag turns them off; PLAY's green LED is a clickable dot
- **relabel the controls**: a design-wide "sticker" (what the firmware makes of each printed button and
  knob) and per-state labels for layers where keys and knobs change job
- **annotate** keys, buttons, knobs and the screen; notes show as numbered badges with a legend
- **screen mock-ups** composed from a structured description — an optional header, four knob cards and
  footer in Felucca's layout, and a panel — with templates for a chord name filling the screen in the
  Orchid notation, Orchid-style dial screens (a huge value with an inverted level fill), tall inverted
  lists, a keyboard strip, a Geek Out view, layer tiles, a circular loop ring, an oscilloscope,
  dense sound-editor pages (`edit8`: 8 parameters under a wide envelope / filter / wave graphic;
  `stack`: up to 8 rows of four, e.g. oscillators or the mod matrix) and free text, in Felucca's eight palettes; edit the JSON in place with a live preview
- **multiple states** (up to 24): pages, layers, moments; each renamable with its own notes and a
  per-state png checkbox
- **png export** of the faceplates at true proportions with legends, or of just the screens as a sheet
- **JSON save/load** in an LLM-friendly format (see below), drag-and-drop loading, copy-to-clipboard
- undo (⌘Z), P / L tools, 0–3 pick the LED level

## scripted exports

`tools/serve.py` serves the folder and accepts `POST /save`, so a design can be rendered without a
download dialog (the browser needs http for `?design=`):

```bash
python3 tools/serve.py --port 8765
```

```
http://localhost:8765/?design=examples/choralroot-fm1-mockups.json&export=screens&post=/save
http://localhost:8765/?design=examples/choralroot-fm1-mockups.json&export=plate&post=/save
```

writes `docs/<design>-screens.png` and `docs/<design>.png` (`name=` overrides).

## the JSON format

Designs save as `fm1-panel-design` JSON, specified in [FORMAT.md](FORMAT.md): per state, 27 key
levels, 14 button levels, the knob notes and a structured `screen` object. The format is built for
LLM round-tripping: paste a design's JSON (plus `FORMAT.md`) to your assistant and ask for changes,
then load its reply back into the editor — or ask it to generate a design from scratch and inspect the
result visually. See [examples/choralroot-fm1-mockups.json](examples/choralroot-fm1-mockups.json), the
ChoralRoot FM-1 interface in twenty-four states.

## related

- [ChoralRoot FM-1](https://github.com/Quixotic7/ChoralRootFM1) — the firmware this was built for
- [Felucca](https://github.com/hugelton/Felucca) — the open FM-1 firmware whose UI grammar the screen
  mock-ups follow
- [OMX-27 LED designer](https://github.com/quixotic7/OMX-LED-Designer), [grid LED designer](https://github.com/quixotic7/grid-led-designer)

## license

[MIT](LICENSE)
