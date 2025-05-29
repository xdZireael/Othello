# Projet de Programmation

- `reports/preliminary`: Code LaTeX du rapport préliminaire.
- `reports/final`: Code LaTeX du rapport final.

# Othello Game

Python based implementation of the game of Othello (also known as Reversi)

## Prerequisites

### System Dependencies

Depending on your Linux distribution, install the required GTK4 / PyGObject dependencies:

**Debian/Ubuntu:**
```bash
apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

**Fedora:**
```bash
sudo dnf install python3-gobject gtk4
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk4
```

**openSUSE:**
```bash
sudo zypper install python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-4_0 libgtk-4-1
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/xdZireael/Othello
```

2. Navigate to the project directory:
```bash
cd othello-1
```

3. Create and activate a virtual environment:
```bash
python -m venv venv
. venv/bin/activate
```

4. Install the game:
```bash
python -m pip install ./othello
```

## Running the Game

Launch the game using either:
```bash
python -m othello
# or
othello
```
If you are using zsh/autocd etc. like me, prefer the `python -m othello` version.

## Troubleshooting

If you encounter issues on Wayland, set the XKB configuration path:
```bash
export XKB_CONFIG_ROOT=/usr/share/X11/xkb/rules/
```

For additional PyGObject setup information, visit: https://pygobject.gnome.org/getting_started.html


## Colaborators

[Matis Duval](https://github.com/xdZireael) - Performance optimisation and CLI
[Gabriel Tardiou](https://github.com/Louksi) - Report and code structure
[Remy Heuret](https://github.com/Gostrick) - AI
[Lucas Marques](https://github.com/IkeYeek) - GUI and bitboard structure implementation
