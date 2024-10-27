#!/usr/bin/python3
'''	There was an Old Man in a boat,
	Who said, 'I'm afloat! I'm afloat!'
		When they said 'No you ain't!'
		He was ready to faint,
	That unhappy Old Man in a boat.
				(E. Lear)


	A python rework of xcowsay ( http://www.doof.me.uk/xcowsay ) , this python script will display
	a character with different balloon styles. He will display custom text,
	or pictures (if in dream mode). Here's a sample on how to run it:

	characters are the pics in the images directory (bat,donkey,snake,chicken etc.)

	character icons are taken from the freeware Animal Icons collection by Martin Berube
	http://www.softicons.com/animal-icons/animal-icons-by-martin-berube

	instances are created like this :

	Puppet(character='snake',verb="say",text="your Text",font="BonvenoCF-Light.otf",fontcolor=(255,0,0))

	verb can be : say, think, shout or dream

	if dream, you can pass an image as the dream topic :

	Puppet(character='donkey',verb="dream",dreamed=path_to_your_pic) 
	
	You can drag the puppet around the screen by keeping the META/Windows KEY pressed
	and dragging the image with your mouse.
	
	Clicking on the image will close it. It will also close if you press any KEY, other
	than META/Windows'''

__version__ = "0.3"
__author__ = "Salvatore Bognanni <salvogendut AT gmail DOT CoM>"

import os
import sys
from PIL import Image, ImageFont, ImageDraw
import tkinter as tk
import textwrap
from typing import Optional, Tuple

imgdir = "images"
fontdir = "fonts"

def combine_sources(posx: int, posy: int, img1: str, img2: str, final: str) -> str:
    """Combine two images using PIL"""
    base = Image.open(img1)
    overlay = Image.open(img2)
    
    # Ensure images are in RGBA mode
    if base.mode != 'RGBA':
        base = base.convert('RGBA')
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')
        
    result = Image.new('RGBA', base.size, (0, 0, 0, 0))
    result.paste(base, (0, 0), base)
    result.paste(overlay, (posx, posy), overlay)
    result.save(final, 'PNG')
    return final

class Puppet(tk.Tk):
    def __init__(self, character: str = None, verb: str = None, text: str = None,
                 dreamed: str = None, font: str = None, fontcolor: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__()
        
        self.imgW = 640
        self.imgH = 520
        self.character = character
        self.font = font
        self.imgdir = imgdir
        self.imagefile = os.path.join(self.imgdir, 'ab' + self.character + ".png")
        self.characterpic = os.path.join(self.imgdir, self.character + ".png")
        self.dreamballoon = os.path.join(self.imgdir, "dream.png")
        self.dreambase = os.path.join(self.imgdir, "dreambase.png")
        self.bigbase = os.path.join(self.imgdir, "bigbase.png")
        self.minidream = os.path.join(self.imgdir, "minidream.png")
        self.empty = os.path.join(self.imgdir, "empty.png")
        self.balloonbase = os.path.join(self.imgdir, "balloonbase.png")
        self.combo = os.path.join(self.imgdir, "output.png")
        self.fontdir = fontdir
        self.fontfile = os.path.join(self.fontdir, self.font)
        self.window_title = "xKaa"
        self.dreamed = dreamed
        self.fontcolor = fontcolor
        self.verb = verb
        self.text = text
        self._dragging = False
        
        # Configure window
        self.overrideredirect(True)
        self.wm_title(self.window_title)
        self.attributes('-alpha', 0.999)
        
        # Using system default background color
        bg_color = self.cget('bg')
        
        # Create canvas with matching background
        self.canvas = tk.Canvas(
            self,
            width=self.imgW,
            height=self.imgH,
            bg=bg_color,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack()
        
        # Build and display the image
        self.popup = self.build_popup()
        self.image = tk.PhotoImage(file=self.popup)
        
        # Add image to canvas
        self.canvas_image = self.canvas.create_image(
            0, 0,
            image=self.image,
            anchor='nw'
        )
        
        # Bind events to canvas
        self.bind('<Key>', self.close_application)
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.close_if_not_dragged)
        
        # Make canvas focusable
        self.canvas.focus_set()
        
        # Center window at mouse position and set size
        self.center_window()
        
        # Adjust window size
        self.after(100, self.adjust_window_size)

    def adjust_window_size(self):
        """Adjust window size to match content"""
        # Get image dimensions
        width = self.image.width()
        height = self.image.height()
        
        # Configure canvas size
        self.canvas.configure(width=width, height=height)
        
        # Configure window size
        self.geometry(f"{width}x{height}")

    def make_dream(self) -> str:
        """Handle dream image"""
        dream_img = Image.open(self.dreamed)
        width = 128
        dream_img = dream_img.resize((width, width))
        dream_img.save(self.minidream)
        return combine_sources(80, 65, self.balloonbase, self.minidream, self.dreamballoon)

    def draw_balloons(self, balloontype: Optional[str] = None) -> str:
        """Create balloon using PIL"""
        self.balloontype = balloontype
        base = Image.new('RGBA', (640, 520), (0, 0, 0, 0))
        draw = ImageDraw.Draw(base)
        
        if self.balloontype == 'say':
            draw.polygon([(20, 230), (94, 195), (54, 172)], fill='white', outline='black')
            draw.ellipse((20, 20, 280, 220), fill='white', outline='black')
            draw.polygon([(20, 230), (94, 195), (54, 172)], fill='white')
        elif self.balloontype in ('dream', 'think'):
            draw.ellipse((20, 20, 280, 220), fill='white', outline='black')
            draw.ellipse((20, 180, 100, 240), fill='white', outline='black')
            draw.ellipse((0, 220, 20, 240), fill='white', outline='black')
        elif self.balloontype == 'shout':
            points = [(3, 237), (29, 183), (46, 206), (56, 156),
                     (12, 170), (36, 131), (3, 111), (38, 96),
                     (8, 70), (51, 62), (25, 22), (85, 38), (120, 9),
                     (147, 42), (191, 19), (201, 57), (252, 47), (249, 88),
                     (282, 120), (235, 137), (260, 172), (210, 178),
                     (233, 218), (170, 174), (148, 211), (130, 185),
                     (104, 240), (94, 200), (47, 229), (29, 200)]
            draw.polygon(points, fill='white', outline='black')
        else:
            draw.ellipse((20, 20, 280, 220), fill='white')
            
        base.save(self.balloonbase, 'PNG')
        return self.balloonbase

    def draw_base(self):
        """Create base image using PIL"""
        base = Image.new('RGBA', (640, 520), (0, 0, 0, 0))
        char_img = Image.open(self.characterpic)
        if char_img.mode != 'RGBA':
            char_img = char_img.convert('RGBA')
        base.paste(char_img, (80, 200), char_img)
        base.save(self.imagefile)
        return self.imagefile

    def build_popup(self) -> str:
        # Position balloons
        self.baloon = self.draw_balloons(balloontype=self.verb)

        if self.verb == 'say':
            self.origx, self.origy = 230, 10
            self.textX, self.textY = 290, 65
        elif self.verb == 'think':
            self.origx, self.origy = 230, 10
            self.textX, self.textY = 290, 65
        elif self.verb == 'dream':
            self.baloon = self.make_dream()
            self.origx, self.origy = 220, 0
        elif self.verb == 'shout':
            self.origx, self.origy = 210, 10
            self.textX, self.textY = 270, 70
        else:
            self.origx, self.origy = 190, 10
            self.textX, self.textY = 260, 55

        # Create transparent base
        result = Image.new('RGBA', (640, 520), (0, 0, 0, 0))
        
        # Build and combine images
        self.draw_base()
        char_img = Image.open(self.imagefile)
        balloon_img = Image.open(self.baloon)
        
        # Paste images with their alpha channels
        result.paste(char_img, (0, 0), char_img)
        result.paste(balloon_img, (self.origx, self.origy), balloon_img)

        # Add text if needed
        if self.baloon != self.dreamballoon:
            draw = ImageDraw.Draw(result)
            font = ImageFont.truetype(self.fontfile, 15)
            lines = textwrap.wrap(self.text, width=20)
            y_text = self.textY
            for line in lines:
                bbox = font.getbbox(line)
                text_height = bbox[3] - bbox[1]
                draw.text((self.textX, y_text), line, self.fontcolor, font=font)
                y_text += text_height

        # Crop to content
        bbox = result.getbbox()
        if bbox:
            padding = 10
            bbox = (
                max(0, bbox[0] - padding),
                max(0, bbox[1] - padding),
                min(result.width, bbox[2] + padding),
                min(result.height, bbox[3] + padding)
            )
            result = result.crop(bbox)

        result.save(self.combo, 'PNG')
        return self.combo

    def start_drag(self, event):
        """Start drag operation"""
        self._drag_start_x = event.x_root - self.winfo_x()
        self._drag_start_y = event.y_root - self.winfo_y()
        self._dragging = False
    
    def on_drag(self, event):
        """Handle window dragging"""
        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y
        self.geometry(f'+{x}+{y}')
        self._dragging = True
    
    def close_if_not_dragged(self, event):
        """Close window only if it wasn't being dragged"""
        if not self._dragging:
            self.close_application(event)

    def center_window(self):
        """Center window at mouse cursor"""
        x = self.winfo_pointerx() - self.winfo_width() // 2
        y = self.winfo_pointery() - self.winfo_height() // 2
        self.geometry(f'+{x}+{y}')

    def close_application(self, event):
        """Clean up and close"""
        for file in [self.combo, self.imagefile, self.balloonbase]:
            try:
                os.unlink(file)
            except:
                pass
        try:
            os.unlink(self.minidream)
            os.unlink(self.dreamballoon)
        except:
            pass
        self.quit()

if __name__ == "__main__":
    app = Puppet(
        character='snake',
        verb="say",
        text="Hello World!",
        font="BonvenoCF-Light.otf",
        fontcolor=(255, 0, 0)
    )
    app.mainloop()
