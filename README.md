# camascii

> live webcam → ASCII art in your terminal

Licensed under [MIT](LICENSE) — free for personal and commercial use.

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
git clone https://github.com/distortedteen/camascii
cd camascii
pip install -r requirements.txt
```

### requirements

- **Python** 3.10+
- **opencv-python** >=4.8.0
- **numpy** >=1.24.0
- **sounddevice** >=0.4.6 (for audio mode)
- **scipy** >=1.11.0

> on Fedora/CachyOS you may need `--break-system-packages` if outside a venv

## run

```bash
python camascii.py
```

make your terminal fullscreen first — more pixels = more detail.

## quick start (basic mode)

```bash
# 1. make terminal fullscreen
# 2. run the default basic mode
python camascii.py
# 3. press q to quit
```

## run with overlays

```bash
python camascii.py --title "raag bhairavi" --subtitle "live session"
```

## CLI arguments

| argument | description | default |
|----------|-------------|---------|
| `--title` | Title text for overlay | (none) |
| `--subtitle` | Subtitle text for overlay | (none) |

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

## troubleshooting

### webcam not detected

- Check that `/dev/video0` exists: `ls /dev/video*`
- Try a different device index: modify line 190 in `camascii.py` (`VideoCapture(0)` → `VideoCapture(1)`)
- On Wayland, ensure webcam access is granted in settings

### colors look wrong or monochrome

- Ensure your terminal sets `TERM=xterm-256color`
- Check: `echo $TERM`
- If wrong, add to your shell config: `export TERM=xterm-256color`
- Or press `c` to toggle 256-color mode

### performance is slow / choppy

- Reduce terminal window size (fewer pixels to render)
- Press `h` to hide HUD overlay
- Disable color mode (press `c` to toggle off)
- Close other applications using the webcam

### audio mode not working

- Install PortAudio: `sudo dnf install portaudio-devel` (Fedora) / `sudo apt install libportaudio2` (Debian)
- Check microphone permissions in system settings
- Verify with: `python -c "import sounddevice as sd; print(sd.query_devices())"`

### saved .txt files look malformed

- Use a monospace font to view (JetBrains Mono, Fira Code, etc.)
- Ensure no line wrapping in your editor

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

## contributing

Contributions welcome. Please follow these guidelines:

1. **Fork** the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Test your changes locally
4. Commit with clear messages: `git commit -m "add: feature description"`
5. Push to your fork and open a pull request

### code style

- Use **Python 3.10+** syntax
- Follow [PEP 8](https://peps.python.org/pep-0008/) formatting
- Use `curses` for terminal rendering (no external TUI libraries)

### changelog

See [CHANGELOG.md](CHANGELOG.md) for a full version history.

### development setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## contact

- **Issues**: https://github.com/distortedteen/camascii/issues
- **Repo**: https://github.com/distortedteen/camascii

---

*part of a larger collection of terminal art experiments*