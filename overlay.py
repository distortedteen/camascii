import curses


def draw_title(stdscr, title: str, subtitle: str, h: int, w: int):
    if not title:
        return
    box_w = max(len(title) + 4, len(subtitle) + 4, 20)
    box_h = 3
    box_y = h - box_h - 3
    box_x = 2

    try:
        stdscr.addstr(box_y, box_x, "╔" + "═" * (box_w - 2) + "╗", curses.A_BOLD)
        stdscr.addstr(box_y + 1, box_x, "║ " + title[:box_w - 4] + " ║", curses.A_BOLD)
        if subtitle:
            stdscr.addstr(box_y + 1, box_x + box_w - len(subtitle) - 3, subtitle[:box_w - 4], curses.A_BOLD)
        stdscr.addstr(box_y + 2, box_x, "╚" + "═" * (box_w - 2) + "╝", curses.A_BOLD)
    except curses.error:
        pass


def draw_vu_meter(stdscr, amplitude: float, w: int, row: int):
    bar_width = min(w - 10, 40)
    filled = int(amplitude * bar_width)
    pct = int(amplitude * 100)

    bar = "▐"
    for i in range(bar_width):
        if i < filled:
            bar += "█"
        elif i == filled:
            bar += "▓"
        else:
            bar += "░"
    bar += "▌"

    color = 2
    if amplitude > 0.7:
        color = 1
    elif amplitude > 0.4:
        color = 3

    try:
        stdscr.addstr(row, 2, "VU ", curses.A_BOLD)
        stdscr.addstr(row, 5, bar, curses.color_pair(color) if color else 0)
        stdscr.addstr(row, 5 + bar_width + 1, f" {pct:2d}%", curses.A_BOLD)
    except curses.error:
        pass


def draw_border(stdscr, h: int, w: int, style: str):
    if style == "none":
        return

    styles = {
        "single": ("─", "│", "┌", "┐", "└", "┘"),
        "double": ("═", "║", "╔", "╗", "╚", "╝"),
        "bold": ("━", "┃", "┏", "┓", "┗", "┛"),
    }
    if style not in styles:
        style = "single"
    hz, vt, tl, tr, bl, br = styles[style]

    try:
        stdscr.addstr(1, 0, tl + hz * (w - 2) + tr)
        for y in range(2, h - 3):
            stdscr.addstr(y, 0, vt)
            stdscr.addstr(y, w - 1, vt)
        stdscr.addstr(h - 3, 0, bl + hz * (w - 2) + br)
    except curses.error:
        pass


def draw_rec_indicator(stdscr, w: int, row: int, visible: bool):
    if not visible:
        return
    try:
        stdscr.addstr(row, w - 12, "● REC  ", curses.color_pair(1) | curses.A_BOLD)
    except curses.error:
        pass


OVERLAY_PRESETS = [
    "none",
    "minimal",
    "concert",
    "art",
]
PRESET_KEYS = list(OVERLAY_PRESETS)


BORDER_STYLES = [
    "none",
    "single",
    "double",
    "bold",
]
BORDER_KEYS = list(BORDER_STYLES)