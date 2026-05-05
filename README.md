# camascii

> live webcam → ASCII art in your terminal

your face, rendered in `░▒▓█` — real-time, zero dependencies beyond Python and OpenCV.

```
████▓▓▒▒░░  ░░▒▒▓▓██▓▓▒░  ░▒▓
▓▓██▓▒░  ░▒▓███████▓▒░  ░▒▓
▒▒▓██▓░  ░▓███░░███▓▒  ░░▒▓
░░▒▓███  ▓████  ████▒░  ░▒▓
```

## features

- **4 character sets** — minimal, detailed, blocks (default), matrix
- **edge-detect mode** — Canny filter, looks like a pencil sketch
- **256-color mode** — maps real pixel RGB to nearest xterm-256 color
- **adjustable thresholds** — tune Canny edge sensitivity live
- **freeze + save** — freeze any frame, export as `.txt` art file
- **invert & mirror** controls
- **audio-reactive mode** — mic input modulates render (guitar edition)
- **color themes** — neon, amber, matrix, ghost, thermal, vhs
- **glitch effects** — CRT interference on strums/transients
- **frame recorder** — record frames, export as .zip or video
- **overlays** — VU meter, title card, border, REC indicator
- zero GPU needed, runs on any Linux terminal that supports 256 colors

## guitar edition

Optimized for guitar recording, supports audio response, theme colors, and border decorations.

### audio-reactive features

- **amplitude modulation** — render zooms subtly on loud strums
- **glyph density mapping** — silence = sparse chars, loud = dense
- **glitch bursts** — CRT corruption on transient attacks
- **spectral centroid tinting** — color shifts with frequency

### themes

| theme | description |
|-------|-------------|
| neon | cyan → magenta gradient by frequency |
| amber | warm gold tones, acoustic feel |
| matrix | green-on-black, classic terminal |
| ghost | white/grey only, high contrast |
| thermal | black → purple → orange → white |
| vhs | desaturated with tracking bands |

## install

```bash
git clone https://github.com/yourname/camascii
cd camascii
pip install -r requirements.txt
```

> on Fedora/CachyOS you may need `--break-system-packages` if outside a venv

## run

```bash
python camascii.py
```

make your terminal fullscreen first — more pixels = more detail.

## run with overlays

```bash
python camascii.py --title "raag bhairavi" --subtitle "live session"
```

## controls

| key | action |
|-----|--------|
| `q` / `ESC` | quit |
| `e` | toggle edge-detect (Canny) |
| `c` | toggle 256-color mode |
| `d` | cycle character set |
| `t` | cycle color theme |
| `i` | invert brightness |
| `f` | freeze / unfreeze frame |
| `m` | mirror flip |
| `a` | toggle audio-reactive mode |
| `r` | start / stop recording |
| `o` | cycle overlay preset |
| `b` | cycle border style |
| `s` | save current frame as `.txt` |
| `[` / `]` | lower / raise Canny threshold |
| `h` | hide / restore HUD |

## guitar recording workflow

```
1. open a terminal, make it fullscreen
2. python camascii.py --title "song name" --subtitle "take 1"
3. press `a` to enable audio reactive mode
4. press `t` to pick a theme (amber or neon recommended for guitar)
5. press `o` to set overlay preset (concert or minimal)
6. press `r` to start recording
7. play — watch the ASCII glitch on every strum
8. press `r` again to stop — get a .zip of all frames
```

## recommended terminal setup (for Hyprland)

```ini
# kitty.conf
font_family      JetBrains Mono Nerd Font
font_size        7.0
background       #000000
foreground       #e0e0e0
cursor_blink_interval 0
sync_to_monitor  yes
```

smaller font = more ASCII pixels. 7pt in fullscreen ≈ 300×100 chars.

## tips

- **blocks + color** = the neo-tokyo aesthetic
- **edge mode + invert** = white lines on black, very clean
- **detailed charset + no color** = classic hacker terminal look
- for best color results, use a terminal with `TERM=xterm-256color`
- saved `.txt` files look great in a monospace font, paste them anywhere
- **amber theme + audio** = warm acoustic aesthetic
- **neon theme + audio** = vibrant electric sound

## how it works

1. OpenCV captures frames from `/dev/video0`
2. frame is resized to your exact terminal dimensions (width × render_height)
3. each pixel's brightness maps to a character in the selected ramp
4. in color mode, RGB → theme palette → xterm-256 color
5. in edge mode, Gaussian blur → Canny → binary edge map rendered as `█▓` chars
6. audio input analyzed for amplitude, transients, spectral centroid
7. glitches triggered on transient detection
8. curses handles rendering at ~50fps poll rate

## project structure

```
camascii/
├── camascii.py          ← main entry
├── audio.py           ← mic capture + analysis
├── recorder.py        ← frame recording + export
├── themes.py         ← color palettes
├── overlay.py        ← text overlays
├── requirements.txt
└── README.md
```

---

*part of a larger collection of terminal art experiments*