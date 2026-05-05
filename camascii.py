#!/usr/bin/env python3
"""
camascii — live webcam to ASCII/block-char art renderer (guitar edition)

Controls:
  q / ESC   quit
  e         toggle edge-detect mode (Canny)
  c         toggle 256-color mode
  d         cycle character sets (minimal → detailed → blocks → matrix)
  t         cycle color themes (neon/amber/matrix/ghost/thermal/vhs)
  i         invert brightness
  f         freeze / unfreeze frame
  s         save current frame as .txt file
  [ / ]     lower / raise Canny threshold (in edge mode)
  m         mirror flip toggle
  a         toggle audio-reactive mode
  r         start / stop recording
  o         cycle overlay preset (none/minimal/concert/art)
  b         cycle border style (none/single/double/bold)
  h         toggle HUD visibility
"""

import argparse
import curses
import sys
import os
import time
import random
from datetime import datetime

try:
    import cv2
    import numpy as np
except ImportError:
    print("Missing deps. Run:  pip install opencv-python numpy")
    sys.exit(1)

from audio import AudioAnalyzer, HAS_SOUNDDEVICE
from themes import THEMES, THEME_KEYS, get_theme
from overlay import (
    draw_title, draw_vu_meter, draw_border, draw_rec_indicator,
    OVERLAY_PRESETS, PRESET_KEYS, BORDER_STYLES, BORDER_KEYS
)
from recorder import Recorder


RAMPS = {
    "minimal": " .:-=+*#%@",
    "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "blocks": " ░▒▓█",
    "matrix": " ·:+=xX$&#@",
}
RAMP_KEYS = list(RAMPS.keys())


GLITCH_CHARS = "▓▒█░│─┼╫╬╪▐▌▄▀■□▪▫"


def rgb_to_xterm256(r: int, g: int, b: int) -> int:
    r6 = round(r / 255 * 5)
    g6 = round(g / 255 * 5)
    b6 = round(b / 255 * 5)
    return 16 + 36 * r6 + 6 * g6 + b6


_pair_cache = {}
_next_pair = [1]


def get_color_pair(xterm_idx: int) -> int:
    if xterm_idx in _pair_cache:
        return _pair_cache[xterm_idx]
    pair_num = _next_pair[0]
    if pair_num >= curses.COLOR_PAIRS:
        pair_num = (pair_num % (curses.COLOR_PAIRS - 1)) + 1
    _next_pair[0] = pair_num + 1
    curses.init_pair(pair_num, xterm_idx, -1)
    _pair_cache[xterm_idx] = pair_num
    return pair_num


def brightness_to_char(val: int, ramp: str) -> str:
    idx = int(val / 255 * (len(ramp) - 1))
    return ramp[idx]


def frame_to_ascii(gray, w: int, h: int, ramp: str, invert: bool):
    small = cv2.resize(gray, (w, h), interpolation=cv2.INTER_AREA)
    if invert:
        small = 255 - small
    return ["".join(brightness_to_char(int(px), ramp) for px in row) for row in small]


def frame_to_edges(gray, w: int, h: int, lo: int, hi: int):
    small = cv2.resize(gray, (w, h), interpolation=cv2.INTER_AREA)
    blurred = cv2.GaussianBlur(small, (3, 3), 0)
    edges = cv2.Canny(blurred, lo, hi)
    rows = []
    for row in edges:
        rows.append("".join("█" if px > 200 else ("▓" if px > 100 else " ") for px in row))
    return rows


def frame_to_color(frame, w: int, h: int, ramp: str, theme_name: str, sc: float = 0.5):
    theme = get_theme(theme_name)
    palette = theme["palette"]
    custom_ramp = theme.get("ramp", ramp)

    small_bgr = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
    small_gray = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2GRAY)
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            b, g, r = int(small_bgr[y, x, 0]), int(small_bgr[y, x, 1]), int(small_bgr[y, x, 2])
            brightness = int(small_gray[y, x]) / 255.0

            if theme_name == "vhs":
                col = palette(brightness, sc, y)
            else:
                col = palette(brightness, sc)

            ch_idx = int(brightness * (len(custom_ramp) - 1))
            ch = custom_ramp[ch_idx]
            row.append((ch, col))
        result.append(row)
    return result


def save_frame(rows: list[str]) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"camascii_{ts}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    return fname


class GlitchState:
    def __init__(self):
        self.active = False
        self.rows = []
        self.ttl = 0

    def trigger(self, term_h, term_w):
        n_bands = random.randint(1, 4)
        self.rows = []
        for _ in range(n_bands):
            y = random.randint(0, term_h - 3)
            x_start = random.randint(0, term_w // 2)
            width = random.randint(term_w // 6, term_w // 2)
            chars = "".join(random.choice(GLITCH_CHARS) for _ in range(width))
            self.rows.append((y, x_start, chars))
        self.ttl = random.randint(1, 2)
        self.active = True

    def tick(self):
        if self.active:
            self.ttl -= 1
            if self.ttl <= 0:
                self.active = False

    def apply(self, stdscr):
        if not self.active:
            return
        for y, x, chars in self.rows:
            try:
                stdscr.addstr(y, x, chars, curses.A_BOLD)
            except curses.error:
                pass


def main(stdscr: curses.window) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, default="", help="Song title for overlay")
    parser.add_argument("--subtitle", type=str, default="", help="Subtitle for overlay")
    args, _ = parser.parse_known_args()

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(20)
    curses.start_color()
    curses.use_default_colors()

    has_256 = curses.COLORS >= 256
    if has_256:
        curses.init_pair(1, 196, -1)
        curses.init_pair(2, 46, -1)
        curses.init_pair(3, 226, -1)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        curses.endwin()
        print("Error: could not open webcam (device 0).")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    audio_analyzer = None
    if HAS_SOUNDDEVICE:
        try:
            audio_analyzer = AudioAnalyzer()
            audio_analyzer.start()
        except Exception:
            audio_analyzer = None

    ramp_idx = 2
    edge_mode = False
    color_mode = False
    frozen = False
    invert = False
    mirror = True
    show_hud = True
    edge_lo = 40
    edge_hi = 120

    theme_idx = 0

    audio_reactive = False

    overlay_idx = 0

    border_idx = 0

    recorder = Recorder()
    glitch = GlitchState()

    cached_frame = None
    cached_gray = None
    last_rows = []

    status_msg = ""
    status_until = 0.0

    def flash(msg: str) -> None:
        nonlocal status_msg, status_until
        status_msg = msg
        status_until = time.time() + 2.5

    flash("camascii ready  —  h for controls")

    while True:
        term_h, term_w = stdscr.getmaxyx()
        render_h = max(1, term_h - (2 if show_hud else 0))
        render_w = max(1, term_w)

        amplitude = 0.0
        is_transient = False
        spectral_centroid = 0.5
        if audio_reactive and audio_analyzer:
            amplitude, is_transient, spectral_centroid = audio_analyzer.get()

        if audio_reactive and amplitude > 0:
            render_w = int(term_w * (0.85 + amplitude * 0.15))
            ramp_idx = int(amplitude * (len(RAMP_KEYS) - 1))
            ramp_idx = max(0, min(ramp_idx, len(RAMP_KEYS) - 1))

        key = stdscr.getch()

        if key in (ord('q'), 27):
            break
        elif key == ord('e'):
            edge_mode = not edge_mode
            if edge_mode:
                color_mode = False
            flash(f"edge detect {'ON' if edge_mode else 'OFF'}")
        elif key == ord('c'):
            if not has_256:
                flash("256-color not supported by this terminal")
            else:
                color_mode = not color_mode
                if color_mode:
                    edge_mode = False
                flash(f"color {'ON' if color_mode else 'OFF'}")
        elif key == ord('d'):
            ramp_idx = (ramp_idx + 1) % len(RAMP_KEYS)
            flash(f"charset → {RAMP_KEYS[ramp_idx]}")
        elif key == ord('t'):
            theme_idx = (theme_idx + 1) % len(THEME_KEYS)
            flash(f"theme → {THEME_KEYS[theme_idx]}")
        elif key == ord('i'):
            invert = not invert
            flash(f"invert {'ON' if invert else 'OFF'}")
        elif key == ord('f'):
            frozen = not frozen
            flash("FROZEN" if frozen else "live")
        elif key == ord('m'):
            mirror = not mirror
            flash(f"mirror {'ON' if mirror else 'OFF'}")
        elif key == ord('a'):
            audio_reactive = not audio_reactive
            if audio_reactive and not audio_analyzer:
                flash("audio not available (install sounddevice)")
                audio_reactive = False
            else:
                flash(f"audio reactive {'ON' if audio_reactive else 'OFF'}")
        elif key == ord('r'):
            if recorder.recording:
                fname = recorder.stop()
                flash(f"saved → {fname}")
            else:
                recorder.start()
                flash("REC started  (press r to stop)")
        elif key == ord('h'):
            show_hud = not show_hud
            flash("hud hidden  (press h to restore)" if not show_hud else "")
        elif key == ord('s'):
            if last_rows:
                fname = save_frame(last_rows)
                flash(f"saved → {fname}")
        elif key == ord('o'):
            overlay_idx = (overlay_idx + 1) % len(PRESET_KEYS)
            flash(f"overlay → {PRESET_KEYS[overlay_idx]}")
        elif key == ord('b'):
            border_idx = (border_idx + 1) % len(BORDER_KEYS)
            flash(f"border → {BORDER_KEYS[border_idx]}")
        elif key in (ord(']'), ord('+')):
            edge_hi = min(254, edge_hi + 10)
            flash(f"edge threshold hi → {edge_hi}")
        elif key in (ord('['), ord('-')):
            edge_hi = max(edge_lo + 10, edge_hi - 10)
            flash(f"edge threshold hi → {edge_hi}")
        elif key == curses.KEY_RESIZE:
            stdscr.clear()

        if not frozen:
            ret, frame = cap.read()
            if ret:
                if mirror:
                    frame = cv2.flip(frame, 1)
                cached_frame = frame
                cached_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame = cached_frame
        gray = cached_gray
        if frame is None or gray is None:
            time.sleep(0.03)
            continue

        ramp = RAMPS[RAMP_KEYS[ramp_idx]]

        stdscr.erase()

        if is_transient and audio_reactive:
            glitch.trigger(term_h, term_w)

        if edge_mode:
            rows = frame_to_edges(gray, render_w, render_h, edge_lo, edge_hi)
            last_rows = rows
            for y, row in enumerate(rows[:render_h]):
                try:
                    stdscr.addstr(y, 0, row[:render_w])
                except curses.error:
                    pass

        elif color_mode and has_256:
            theme_name = THEME_KEYS[theme_idx]
            color_rows = frame_to_color(frame, render_w, render_h, ramp, theme_name, spectral_centroid)
            plain_rows = []
            for y, row in enumerate(color_rows[:render_h]):
                plain = ""
                for x, (ch, col_idx) in enumerate(row[:render_w - 1]):
                    plain += ch
                    pair = get_color_pair(col_idx)
                    attr = curses.color_pair(pair)
                    try:
                        stdscr.addch(y, x, ch, attr)
                    except curses.error:
                        pass
                plain_rows.append(plain)
            last_rows = plain_rows

        else:
            rows = frame_to_ascii(gray, render_w, render_h, ramp, invert)
            last_rows = rows
            for y, row in enumerate(rows[:render_h]):
                try:
                    stdscr.addstr(y, 0, row[:render_w])
                except curses.error:
                    pass

        glitch.tick()
        glitch.apply(stdscr)

        if recorder.recording:
            recorder.add_frame(last_rows)

        if show_hud:
            current_preset = PRESET_KEYS[overlay_idx]
            current_border = BORDER_KEYS[border_idx]

            if current_preset in ("minimal", "concert", "art"):
                draw_vu_meter(stdscr, amplitude, render_w, 1)

            if current_preset == "concert":
                draw_border(stdscr, term_h, term_w, current_border)
                draw_title(stdscr, args.title, args.subtitle, term_h, term_w)

            if current_preset == "art":
                draw_border(stdscr, term_h, term_w, current_border)

            if current_preset != "none":
                rec_blink = int(time.time() * 2) % 2 == 0
                draw_rec_indicator(stdscr, render_w, 1, recorder.recording and rec_blink)

            mode_tag = "EDGE" if edge_mode else ("COLOR" if color_mode else "ASCII")
            flags = "  ".join(f for f in [
                f"charset:{RAMP_KEYS[ramp_idx]}",
                "FROZEN" if frozen else None,
                "INVERTED" if invert else None,
                f"edge:{edge_lo}/{edge_hi}" if edge_mode else None,
                f"theme:{THEME_KEYS[theme_idx]}" if color_mode else None,
                "AUDIO" if audio_reactive else None,
                "REC" if recorder.recording else None,
            ] if f)
            hud_left = f"  camascii │ {mode_tag} │ {flags}  "
            hud_right = "  e·edge  c·color  d·charset  t·theme  i·invert  f·freeze  s·save  a·audio  r·rec  o·overlay  b·border  h·hud  q·quit  "
            hud_line = (hud_left + hud_right)[:render_w - 1].ljust(render_w - 1)

            now = time.time()
            status = f"  {status_msg}" if now < status_until else ""

            try:
                stdscr.addstr(term_h - 2, 0, "─" * min(render_w, term_w - 1))
                stdscr.addstr(term_h - 1, 0, hud_line, curses.A_REVERSE)
                if status:
                    sx = max(0, render_w - len(status) - 2)
                    stdscr.addstr(term_h - 1, sx, status[:render_w - sx - 1], curses.A_REVERSE | curses.A_BOLD)
            except curses.error:
                pass

        stdscr.refresh()

    cap.release()
    if audio_analyzer:
        audio_analyzer.stop()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass