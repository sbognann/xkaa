xkaa
====

A Python 3 rework of xcowsay (http://www.doof.me.uk/xcowsay/). The name is inspired by Kaa, the python from 'The Jungle Book'. The x is for X-window, but it also works in Wayland. It also should sound close to 'xcow'.

## Requirements
- Python 3
- GTK4
- Pillow

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
./xkaasay -c snake -a say -t "Hello World!" -i blue
```

### Options
- `-c, --character` : Character name (snake, bat, donkey, etc.)
- `-a, --action` : Action type (say, shout, think, dream)
- `-t, --text` : Text to display
- `-i, --ink` : Ink color (black, red, blue, green)
- `-d, --dream` : Path to dream image (for dream action)

### Controls
- Left click and drag to move the window
- Right click or ESC to close
