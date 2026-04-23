![Example Image](xkaasay.png)

xkaa
====

A Python 3 rework of xcowsay (http://www.doof.me.uk/xcowsay/). The name is inspired by Kaa, the python from 'The Jungle Book'. The x is for X-window, but it also works in Wayland. It also should sound close to 'xcow'.

Display fun character speech bubbles on your desktop with custom text, dynamic sizing, and organic SVG-rendered speech bubble tails!

## Features

- **Dynamic speech bubbles** that automatically resize based on text length
- **SVG-rendered tails** with smooth, organic curved shapes
- **Multiple balloon styles**: say, shout, think, dream
- **Flexible bubble placement**: left, right, or random positioning
- **Multiple characters**: snake, donkey, chicken, bat, and more
- **Customizable text colors**: black, red, blue, green
- **Interactive**: drag to move, click to close

## Requirements

- Python 3
- GTK 4.0
- Pillow (PIL)
- PyGObject
- cairosvg

## Installation

### From source
```bash
pip install -r requirements.txt
```

### On Fedora (RPM)

#### Install pre-built package
```bash
sudo dnf install xkaa
```

#### Build from source
```bash
# Install build dependencies
sudo dnf install rpm-build rpmdevtools

# Set up RPM build environment
rpmdev-setuptree

# Create source tarball
tar --exclude='.git' -czf xkaa-0.2.tar.gz xkaa/
mv xkaa-0.2.tar.gz ~/rpmbuild/SOURCES/

# Copy spec file and build
cp xkaa/xkaa.spec ~/rpmbuild/SPECS/
cd ~/rpmbuild/SPECS
rpmbuild -ba xkaa.spec

# Install the built RPM
sudo dnf install ~/rpmbuild/RPMS/noarch/xkaa-0.2-1.fc*.noarch.rpm
```

See [BUILD_RPM.md](BUILD_RPM.md) for detailed instructions.

## Usage

```bash
xkaasay -c snake -a say -t "Hello World!" -i blue -p right
```

### Command Line Options

- `-t, --text TEXT` : Text to display (default: "Hello World! Use -h for help")
- `-a, --action ACTION` : Balloon type - say, shout, think, or dream (default: say)
- `-c, --character CHARACTER` : Character name - snake, donkey, chicken, bat, etc. (default: snake)
- `-i, --ink COLOR` : Text ink color - black, red, blue, green (default: black)
- `-p, --placement POSITION` : Bubble placement - left, right, or random (default: random)
- `-d, --dream IMAGE` : Path to dream image for dream action (default: images/sheep.png)
- `-h, --help` : Show help message

### Examples

Simple greeting:
```bash
xkaasay -c snake -t "Hello!"
```

Bubble on the right with blue text:
```bash
xkaasay -c donkey -t "Welcome to xKaa!" -i blue -p right
```

Thought bubble:
```bash
xkaasay -c chicken -a think -t "What should I code today?"
```

Dream bubble:
```bash
xkaasay -c bat -a dream -d /path/to/image.png
```

### Interactive Controls

- **Left click and drag**: Move the window around the screen
- **Right click or ESC**: Close the window

## Available Characters

The `images/` directory contains various characters. Common ones include:
- snake
- donkey  
- chicken
- bat
- And more!

## How It Works

xKaa creates beautiful speech bubbles using SVG path rendering with quadratic Bezier curves for smooth, organic tail shapes. The bubbles dynamically size based on text content, with intelligent text wrapping and proper elliptical inscription. The tail seamlessly connects to the bubble and points toward the character's mouth.

## License

Free software - character icons from Animal Icons collection by Martin Berube
http://www.softicons.com/animal-icons/animal-icons-by-martin-berube

## Credits

Inspired by xcowsay (http://www.doof.me.uk/xcowsay/)
Python rework by Salvatore Bognanni
