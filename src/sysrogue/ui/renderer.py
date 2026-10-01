"""Composite terminal renderer for SYS//ROGUE."""

from sysrogue.core.state import GameState
from sysrogue.ui.panels import PanelRenderer
from sysrogue.ui.themes import AnsiTheme

class TerminalRenderer:
    """Manages full screen presentation and prompts."""

    def __init__(self, no_color: bool = False) -> None:
        self.no_color = no_color

    def render_screen(self, state: GameState) -> str:
        parts = [
            PanelRenderer.render_header(state, self.no_color),
            PanelRenderer.render_dashboard(state, self.no_color),
            PanelRenderer.render_logs(state, count=5, no_color=self.no_color),
        ]
        return "\n".join(parts)

    def format_prompt(self, state: GameState) -> str:
        prompt_txt = f"{state.current_node_id}:{state.player.name}> "
        return AnsiTheme.color(prompt_txt, AnsiTheme.GREEN + AnsiTheme.BOLD, self.no_color)
