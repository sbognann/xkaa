# Building xKaa RPM Package

This guide explains how to build an RPM package for xKaa on Fedora.

## Prerequisites

Install the required tools:
```bash
sudo dnf install rpm-build rpmdevtools
```

## Build Steps

1. **Set up RPM build environment:**
   ```bash
   rpmdev-setuptree
   ```

2. **Create source tarball:**
   ```bash
   cd /var/home/sbognann/Development
   tar --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
       -czf xkaa-0.2.tar.gz xkaa/
   ```

3. **Move tarball to RPM sources:**
   ```bash
   mv xkaa-0.2.tar.gz ~/rpmbuild/SOURCES/
   ```

4. **Copy spec file:**
   ```bash
   cp xkaa/xkaa.spec ~/rpmbuild/SPECS/
   ```

5. **Build the RPM:**
   ```bash
   cd ~/rpmbuild/SPECS
   rpmbuild -ba xkaa.spec
   ```

## Installation

After successful build, install the RPM:
```bash
sudo dnf install ~/rpmbuild/RPMS/noarch/xkaa-0.2-1.fc*.noarch.rpm
```

## Verification

Test the installation:
```bash
xkaasay -c snake -t "Hello from RPM!" -p right
```

## Dependencies

The RPM will automatically install these dependencies:
- python3 (>= 3.6)
- python3-pillow (>= 9.0.0)
- python3-gobject (>= 3.42.0)
- python3-cairosvg (>= 2.5.0)
- gtk4
- cairo

## Package Contents

The RPM installs files to:
- `/usr/local/bin/xkaasay` - Main executable wrapper
- `/usr/share/xkaa/` - Application data directory
  - `xkaa.py` - Python module
  - `xkaasay` - Main script
  - `images/` - Character images
  - `fonts/` - Font files
- `/usr/share/doc/xkaa/README.md` - Documentation

## Troubleshooting

### Missing dependencies
If you get dependency errors, install them manually:
```bash
sudo dnf install python3-pillow python3-gobject python3-cairosvg gtk4
```

### Permission errors
The executable needs to be in /usr/local/bin which requires sudo for installation.

### Build errors
Check the build log at:
```bash
less ~/rpmbuild/BUILD/xkaa-0.2/build.log
```
