Name:           xkaa
Version:        0.2
Release:        1%{?dist}
Summary:        Display fun character speech bubbles on your desktop

License:        Free
URL:            https://github.com/sbognann/xkaa
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3 >= 3.6
Requires:       python3-pillow >= 9.0.0
Requires:       python3-gobject >= 3.42.0
Requires:       python3-cairosvg >= 2.5.0
Requires:       gtk4
Requires:       cairo

%description
xKaa is a Python 3 rework of xcowsay. Display fun character speech bubbles
on your desktop with custom text, dynamic sizing, and organic SVG-rendered
speech bubble tails!

Features:
- Dynamic speech bubbles that automatically resize based on text length
- SVG-rendered tails with smooth, organic curved shapes
- Multiple balloon styles: say, shout, think, dream
- Flexible bubble placement: left, right, or random positioning
- Multiple characters: snake, donkey, chicken, bat, and more
- Customizable text colors: black, red, blue, green
- Interactive: drag to move, click to close

%prep
%setup -q -n xkaa

%build
# Nothing to build - pure Python

%install
rm -rf %{buildroot}

# Create necessary directories
install -d %{buildroot}%{_prefix}/local/bin
install -d %{buildroot}%{_datadir}/%{name}
install -d %{buildroot}%{_datadir}/%{name}/images
install -d %{buildroot}%{_datadir}/%{name}/fonts

# Install the Python module and main script
install -m 644 xkaa.py %{buildroot}%{_datadir}/%{name}/xkaa.py
install -m 755 xkaasay %{buildroot}%{_datadir}/%{name}/xkaasay

# Install images and fonts
cp -r images/* %{buildroot}%{_datadir}/%{name}/images/
cp -r fonts/* %{buildroot}%{_datadir}/%{name}/fonts/

# Create wrapper script in /usr/local/bin that runs from the correct directory
cat > %{buildroot}%{_prefix}/local/bin/xkaasay << 'EOF'
#!/bin/bash
# xKaa wrapper script - changes to data directory before execution
cd %{_datadir}/%{name}
exec python3 ./xkaasay "$@"
EOF
chmod 755 %{buildroot}%{_prefix}/local/bin/xkaasay

%files
%{_prefix}/local/bin/xkaasay
%{_datadir}/%{name}/xkaasay
%{_datadir}/%{name}/xkaa.py
%{_datadir}/%{name}/images/
%{_datadir}/%{name}/fonts/
%doc README.md

%changelog
* Thu Apr 23 2026 Salvatore Bognanni <salvo@unixyouth.com> - 0.2-1
- SVG-based speech bubbles with organic curved tails
- Dynamic balloon sizing based on text length
- Bubble placement option (left, right, random)
- Seamless tail connection to bubble
- Fixed character visibility and positioning
- Yellow text background for better readability
- Improved text wrapping algorithm

* Tue Apr 21 2026 Salvatore Bognanni <salvo@unixyouth.com> - 0.1-1
- Initial RPM release
- Python 3 rework of xcowsay
- GTK4 support
- Multiple characters and balloon styles
