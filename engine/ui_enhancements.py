#!/usr/bin/env python3
"""
UI enhancement utilities for Patchwork Isles.
Provides rich terminal UI elements, animations, and improved formatting.
"""

import sys
import time
import textwrap
from typing import List, Optional, Dict, Any

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback for systems without colorama
    COLORAMA_AVAILABLE = False
    class MockColor:
        def __getattr__(self, name): return ""
    Fore = Back = Style = MockColor()

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import track
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def clear_screen():
    """Clear the terminal screen."""
    if sys.platform.startswith('win'):
        import os
        os.system('cls')
    else:
        import os
        os.system('clear')


def print_banner(title: str, subtitle: str = "", width: int = 80):
    """Print a stylized banner."""
    if RICH_AVAILABLE:
        panel = Panel(
            f"[bold cyan]{title}[/bold cyan]\\n[dim]{subtitle}[/dim]",
            width=width,
            padding=(1, 2),
            style="bold blue"
        )
        console.print(panel)
    else:
        # Fallback ASCII banner
        border = "═" * width
        print(f"{Fore.CYAN}{border}{Style.RESET_ALL}")
        centered_title = title.center(width)
        print(f"{Fore.CYAN}{Style.BRIGHT}{centered_title}{Style.RESET_ALL}")
        if subtitle:
            centered_subtitle = subtitle.center(width)
            print(f"{Fore.WHITE}{Style.DIM}{centered_subtitle}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{border}{Style.RESET_ALL}")


def print_section_header(title: str, icon: str = "📋"):
    """Print a section header with icon."""
    if RICH_AVAILABLE:
        text = Text(f"{icon} {title}")
        text.stylize("bold cyan")
        console.print(text)
    else:
        print(f"\\n{Fore.CYAN}{Style.BRIGHT}{icon} {title}{Style.RESET_ALL}")


def print_choice_menu(choices: List[str], title: str = "Choose an option:", 
                     selected_index: Optional[int] = None):
    """Print a styled choice menu."""
    if RICH_AVAILABLE:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Index", style="dim cyan")
        table.add_column("Choice")
        
        for i, choice in enumerate(choices, 1):
            style = "bold green" if selected_index == i else "white"
            marker = "▶" if selected_index == i else " "
            table.add_row(f"{marker} {i}.", choice, style=style)
        
        console.print(f"\\n[bold]{title}[/bold]")
        console.print(table)
    else:
        print(f"\\n{Fore.YELLOW}{Style.BRIGHT}{title}{Style.RESET_ALL}")
        for i, choice in enumerate(choices, 1):
            color = Fore.GREEN if selected_index == i else Fore.WHITE
            marker = "▶" if selected_index == i else " "
            print(f"{color}{marker} {i}. {choice}{Style.RESET_ALL}")


def print_character_stats(player: Dict[str, Any], compact: bool = False):
    """Print character statistics in a formatted layout."""
    if RICH_AVAILABLE and not compact:
        # Rich formatted character sheet
        table = Table(title="Character Information", box=None)
        table.add_column("Category", style="bold cyan")
        table.add_column("Details")
        
        # Basic info
        name = player.get('name', 'Unknown')
        hp = player.get('hp', 10)
        table.add_row("Name", f"[bold]{name}[/bold]")
        table.add_row("Health", f"{hp} HP")
        
        # Tags
        if player.get("tags"):
            tags_text = ", ".join(player["tags"])
            table.add_row("Skills & Roles", tags_text)
        
        # Traits
        if player.get("traits"):
            traits_text = ", ".join(player["traits"])
            table.add_row("Abilities", traits_text)
        
        # Inventory
        if player.get("inventory"):
            inventory_text = ", ".join(player["inventory"])
            table.add_row("Inventory", inventory_text)
        
        console.print(table)
    else:
        # Compact fallback
        name = player.get('name', 'Unknown')
        hp = player.get('hp', 10)
        print(f"{Fore.CYAN}📊 {name} ({hp} HP){Style.RESET_ALL}")
        
        if player.get("tags"):
            print(f"  🏷️  {', '.join(player['tags'])}")
        if player.get("traits"):
            print(f"  ✨ {', '.join(player['traits'])}")
        if player.get("inventory"):
            print(f"  🎒 {', '.join(player['inventory'])}")


def print_progress_bar(current: int, total: int, description: str = "Progress"):
    """Print a progress bar."""
    if RICH_AVAILABLE:
        # Rich will handle progress bars automatically if we use track()
        percentage = (current / total) * 100
        console.print(f"{description}: {current}/{total} ({percentage:.1f}%)")
    else:
        # Simple ASCII progress bar
        width = 30
        filled = int(width * current / total)
        bar = "█" * filled + "░" * (width - filled)
        percentage = (current / total) * 100
        print(f"{description}: [{bar}] {percentage:.1f}% ({current}/{total})")


def typewriter_text(text: str, delay: float = 0.03, wrap_width: int = 80):
    """Display text with typewriter effect."""
    # Wrap long text
    wrapped_lines = textwrap.fill(text, width=wrap_width).split('\\n')
    
    for line in wrapped_lines:
        for char in line:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()  # New line after each wrapped line
    print()  # Extra line after the text


def get_input_with_prompt(prompt: str, default: str = "", validation_fn=None) -> str:
    """Enhanced input with rich prompting if available."""
    if RICH_AVAILABLE:
        if default:
            result = Prompt.ask(prompt, default=default)
        else:
            result = Prompt.ask(prompt)
        
        if validation_fn and not validation_fn(result):
            console.print("[red]Invalid input. Please try again.[/red]")
            return get_input_with_prompt(prompt, default, validation_fn)
        
        return result
    else:
        # Fallback
        display_prompt = f"{prompt}"
        if default:
            display_prompt += f" [{default}]"
        display_prompt += ": "
        
        result = input(f"{Fore.YELLOW}{display_prompt}{Style.RESET_ALL}").strip()
        if not result and default:
            result = default
        
        if validation_fn and not validation_fn(result):
            print(f"{Fore.RED}Invalid input. Please try again.{Style.RESET_ALL}")
            return get_input_with_prompt(prompt, default, validation_fn)
        
        return result


def print_warning(message: str):
    """Print a warning message."""
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")
    else:
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚠️  {message}{Style.RESET_ALL}")


def print_success(message: str):
    """Print a success message."""
    if RICH_AVAILABLE:
        console.print(f"[bold green]✅ {message}[/bold green]")
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print an error message."""
    if RICH_AVAILABLE:
        console.print(f"[bold red]❌ {message}[/bold red]")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}❌ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print an info message."""
    if RICH_AVAILABLE:
        console.print(f"[bold blue]ℹ️  {message}[/bold blue]")
    else:
        print(f"{Fore.BLUE}{Style.BRIGHT}ℹ️  {message}{Style.RESET_ALL}")


def create_fancy_box(content: str, title: str = "", width: int = 60):
    """Create a fancy text box around content."""
    if RICH_AVAILABLE:
        panel = Panel(
            content,
            title=title if title else None,
            width=width,
            padding=(1, 2),
            style="dim"
        )
        console.print(panel)
    else:
        # ASCII box fallback
        lines = content.split('\\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        box_width = min(max(max_line_length + 4, width), 80)
        
        # Top border
        if title:
            title_line = f"╭─ {title} " + "─" * (box_width - len(title) - 5) + "╮"
        else:
            title_line = "╭" + "─" * (box_width - 2) + "╮"
        print(title_line)
        
        # Content
        for line in lines:
            padded_line = f"│ {line:<{box_width - 4}} │"
            print(padded_line)
        
        # Bottom border
        print("╰" + "─" * (box_width - 2) + "╯")


def show_loading_animation(duration: float = 2.0, message: str = "Loading..."):
    """Show a loading animation."""
    if not RICH_AVAILABLE:
        # Simple dots animation
        animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            sys.stdout.write(f"\\r{animation[i % len(animation)]} {message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write(f"\\r✅ {message} Complete!\\n")
    else:
        # Rich handles this with status context or progress bars
        with console.status(message):
            time.sleep(duration)
        console.print(f"✅ {message} Complete!")


# Theme configurations
THEMES = {
    "default": {
        "primary": Fore.CYAN,
        "secondary": Fore.YELLOW, 
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "text": Fore.WHITE
    },
    "dark": {
        "primary": Fore.BLUE,
        "secondary": Fore.MAGENTA,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "text": Fore.WHITE
    }
}

current_theme = "default"

def set_theme(theme_name: str):
    """Set the UI theme."""
    global current_theme
    if theme_name in THEMES:
        current_theme = theme_name
    else:
        print_warning(f"Theme '{theme_name}' not found. Available themes: {', '.join(THEMES.keys())}")

def get_theme_color(color_name: str) -> str:
    """Get a color from the current theme."""
    return THEMES[current_theme].get(color_name, Fore.WHITE)