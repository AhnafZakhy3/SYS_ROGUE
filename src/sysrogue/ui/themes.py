"""ANSI terminal color definitions and visual formatting helpers."""

class AnsiTheme:
    """Cyberpunk terminal ANSI palette."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_DARK = "\033[48;5;234m"

    @classmethod
    def color(cls, text: str, code: str, no_color: bool = False) -> str:
        if no_color:
            return text
        return f"{code}{text}{cls.RESET}"

def render_gauge(
    current: int,
    maximum: int,
    width: int = 12,
    char: str = "█",
    empty: str = "░",
    no_color: bool = False,
) -> str:
    """Renders a text-based status gauge bar."""
    if no_color:
        char, empty = "#", "."
    if maximum <= 0:
        maximum = 1
    current = max(0, min(current, maximum))
    fill_len = int((current / maximum) * width)
    empty_len = width - fill_len
    return f"[{char * fill_len}{empty * empty_len}]"
