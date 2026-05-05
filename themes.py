import math

def palette_neon(brightness: float, sc: float) -> int:
    r = int(sc * 5)
    g = int((1 - sc) * brightness * 5)
    b = int(brightness * 5)
    return 16 + 36 * r + 6 * g + b


def palette_amber(brightness: float, sc: float) -> int:
    if brightness < 0.3:
        r = int(brightness * 8)
        g = int(brightness * 4)
        b = 0
    elif brightness < 0.7:
        r = int(2 + brightness * 3)
        g = int(brightness * 2)
        b = 0
    else:
        r = 5
        g = int(2 + (brightness - 0.7) * 6)
        b = int((brightness - 0.7) * 5)
    return 16 + 36 * r + 6 * g + b


def palette_matrix(brightness: float, sc: float) -> int:
    g = int(brightness * 5)
    r = int((1 - brightness) * brightness * 3)
    b = 0
    if brightness > 0.8:
        return 16 + 36 * 5 + 6 * 5 + 5
    return 16 + 36 * r + 6 * g + b


def palette_ghost(brightness: float, sc: float) -> int:
    gray = int(brightness * 23) + 232
    return gray


def palette_thermal(brightness: float, sc: float) -> int:
    if brightness < 0.25:
        return 16 + 36 * 0 + 6 * 0 + 1
    elif brightness < 0.5:
        return 16 + 36 * 1 + 6 * 2 + 5
    elif brightness < 0.75:
        return 16 + 36 * 5 + 6 * 2 + 0
    else:
        return 16 + 36 * 5 + 6 * 5 + 5


def palette_vhs(brightness: float, sc: float, row: int = 0) -> int:
    band = int(math.sin(row * 0.3) * 2)
    b = max(0, int(brightness * 5) - band)
    r = max(0, int(brightness * 3) - band)
    g = max(0, int(brightness * 3) - band)
    gray = int(brightness * brightness * 20)
    return 16 + 36 * r + 6 * g + b


THEMES = {
    "neon": {
        "palette": palette_neon,
        "ramp": " ░▒▓█",
    },
    "amber": {
        "palette": palette_amber,
        "ramp": " .:-=+*#%@",
    },
    "matrix": {
        "palette": palette_matrix,
        "ramp": " ·:+=xX$&#@",
    },
    "ghost": {
        "palette": palette_ghost,
        "ramp": " .:-=+*#%@",
    },
    "thermal": {
        "palette": palette_thermal,
        "ramp": " ░▒▓█",
    },
    "vhs": {
        "palette": palette_vhs,
        "ramp": " ░▒▓█",
    },
}

THEME_KEYS = list(THEMES.keys())


def get_theme(name: str):
    return THEMES.get(name, THEMES["neon"])