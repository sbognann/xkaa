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

	You can drag the puppet around the screen by holding the left mouse button
	and dragging the image with your mouse.

	Clicking the right mouse button or pressing ESC will close the window.'''


__version__ = "0.2"
__author__ = "Salvatore Bognanni <salvo AT unixyouth DOT COM>"


import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import sys
import os
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
import textwrap

imgdir = "images"
fontdir = "fonts"


def combine_sources(posx, posy, img1, img2, final):
	"""Combine two PNG images using PIL/Pillow instead of Cairo"""
	output = final

	# Open both images
	base = Image.open(img1).convert('RGBA')
	overlay = Image.open(img2).convert('RGBA')

	# Paste overlay onto base at the specified position
	base.paste(overlay, (posx, posy), overlay)

	# Save the result
	base.save(final, 'PNG')
	return output


class Puppet():

	def __init__(self, character=None, verb=None, text=None, dreamed=None, font=None, fontcolor=(0, 0, 0)):

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
		self.fontdir = fontdir
		self.fontfile = os.path.join(self.fontdir, self.font)
		self.title = "xKaa"
		self.dreamed = dreamed
		self.fontcolor = fontcolor

		self.verb = verb
		self.text = text

		self.popup = self.build_popup()

		# For dragging
		self.dragging = False
		self.drag_started = False
		self.drag_start_x = 0
		self.drag_start_y = 0

		# Create GTK application
		self.app = Gtk.Application(application_id='com.xkaa.puppet')
		self.app.connect('activate', self.on_activate)
		self.app.run(None)

	def make_dream(self):
		# combine images together
		scalefactor = 1
		posx = 80
		posy = 65
		width = 128

		# Load and resize the dreamed image
		pixbuf = Image.open(self.dreamed)
		pixbuf.thumbnail((width // scalefactor, width // scalefactor), Image.LANCZOS)
		pixbuf.save(self.minidream, 'PNG')

		myimage = combine_sources(posx, posy, self.balloonbase, self.minidream, self.dreamballoon)
		return self.dreamballoon

	def draw_balloons(self, balloontype=None):
		self.balloontype = balloontype
		''' this will create a balloon instead of using a premade one '''
		base = Image.open(self.empty).convert('RGBA')
		overlay = Image.new('RGBA', base.size, (255, 255, 255, 0))
		draw = ImageDraw.Draw(overlay)
		if self.balloontype == 'say':
			draw.polygon([(20, 230), (94, 195), (54, 172)], fill='white', outline='black')
			draw.ellipse((20, 20, 280, 220), fill='white', outline='black')
			draw.polygon([(20, 230), (94, 195), (54, 172)], fill='white')
		elif (self.balloontype == 'dream') or (self.balloontype == 'think'):
			draw.ellipse((20, 20, 280, 220), fill='white', outline='black')
			draw.ellipse((20, 180, 100, 240), fill='white', outline='black')
			draw.ellipse((0, 220, 20, 240), fill='white', outline='black')
		elif self.balloontype == 'shout':
			draw.polygon([(3, 237), (29, 183), (46, 206), (56, 156),
					(12, 170), (36, 131), (3, 111), (38, 96),
					(8, 70), (51, 62), (25, 22), (85, 38), (120, 9),
					(147, 42), (191, 19), (201, 57), (252, 47), (249, 88),
					(282, 120), (235, 137), (260, 172), (210, 178),
					(233, 218), (170, 174), (148, 211), (130, 185),
					(104, 240), (94, 200), (47, 229), (29, 200)], fill='white', outline='black')
		else:
			draw.ellipse((20, 20, 280, 220), fill='white')
		out = Image.alpha_composite(base, overlay)
		out.save(self.balloonbase)
		return self.balloonbase

	def draw_base(self):
		posx = 80
		posy = 200
		myimage = combine_sources(posx, posy, self.bigbase, self.characterpic, self.imagefile)

	def build_popup(self):

		# some positioning of balloons here
		self.baloon = self.draw_balloons(balloontype=self.verb)

		if self.verb == 'say':
			self.origx = 230
			self.origy = 10
			self.textX = 290
			self.textY = 65
		elif self.verb == 'think':
			self.origx = 230
			self.origy = 10
			self.textX = 290
			self.textY = 65
		elif self.verb == 'dream':
			self.baloon = self.make_dream()
			self.origx = 220
			self.origy = 0
		elif self.verb == 'shout':
			self.origx = 210
			self.origy = 10
			self.textX = 270
			self.textY = 70
		else:
			self.origx = 190
			self.origy = 10
			self.textX = 260
			self.textY = 55

		# combine images together - Main
		self.combo = "images/output.png"
		self.draw_balloons(balloontype=self.verb)
		self.draw_base()
		myimage = combine_sources(self.origx, self.origy, self.imagefile, self.baloon, self.combo)

		# draw text
		img = Image.open(self.combo)
		draw = ImageDraw.Draw(img)
		font = ImageFont.truetype(self.fontfile, 15)

		if self.baloon != self.dreamballoon:
			# handling the wrap around of text is done via textwrap module
			lines = textwrap.wrap(self.text, width=20)
			y_text = self.textY
			x_text = self.textX
			for line in lines:
				bbox = draw.textbbox((x_text, y_text), line, font=font)
				width = bbox[2] - bbox[0]
				height = bbox[3] - bbox[1]
				draw.text((x_text, y_text), line, self.fontcolor, font=font)
				y_text += height

		# save image
		img.save(self.combo)
		return self.combo

	def on_activate(self, app):
		"""Create and show the GTK window"""
		# Create window
		self.window = Gtk.ApplicationWindow(application=app)
		self.window.set_title(self.title)
		self.window.set_default_size(self.imgW, self.imgH)
		self.window.set_decorated(False)  # No window frame

		# Load the image
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.popup)

		# Create picture widget to display the image
		self.picture = Gtk.Picture.new_for_pixbuf(pixbuf)

		# Add CSS to make the window background transparent
		css_provider = Gtk.CssProvider()
		css_provider.load_from_data(b"""
			window {
				background-color: transparent;
			}
		""")
		Gtk.StyleContext.add_provider_for_display(
			self.window.get_display(),
			css_provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)

		self.window.set_child(self.picture)

		# Set up mouse event controllers
		# Left click drag controller
		self.drag_controller = Gtk.GestureDrag.new()
		self.drag_controller.connect('drag-begin', self.on_drag_begin)
		self.drag_controller.connect('drag-update', self.on_drag_update)
		self.drag_controller.connect('drag-end', self.on_drag_end)
		self.window.add_controller(self.drag_controller)

		# Right click controller
		self.click_controller = Gtk.GestureClick.new()
		self.click_controller.set_button(3)  # Right mouse button
		self.click_controller.connect('pressed', self.on_right_click)
		self.window.add_controller(self.click_controller)

		# ESC key controller
		self.key_controller = Gtk.EventControllerKey.new()
		self.key_controller.connect('key-pressed', self.on_key_pressed)
		self.window.add_controller(self.key_controller)

		# Connect window close event
		self.window.connect('close-request', self.on_window_close)

		# Show the window
		self.window.present()

	def on_drag_begin(self, gesture, x, y):
		"""Start dragging the window"""
		self.drag_started = False
		# Start window drag using native window manager
		device = gesture.get_device()
		surface = self.window.get_surface()
		if surface and hasattr(surface, 'begin_move'):
			surface.begin_move(device, 1, x, y, gesture.get_current_event_time())

	def on_drag_update(self, gesture, offset_x, offset_y):
		"""Update drag state"""
		# Mark that we've actually dragged (not just clicked)
		if abs(offset_x) > 3 or abs(offset_y) > 3:
			self.drag_started = True

	def on_drag_end(self, gesture, offset_x, offset_y):
		"""Handle drag end - close if it was just a click"""
		if not self.drag_started:
			# It was just a click, not a drag - close the window
			self.window.close()
		self.drag_started = False

	def on_right_click(self, gesture, n_press, x, y):
		"""Close window on right click"""
		self.window.close()

	def on_key_pressed(self, controller, keyval, keycode, state):
		"""Handle keyboard events"""
		if keyval == Gdk.KEY_Escape:
			self.window.close()
			return True
		return False

	def on_window_close(self, window):
		"""Clean up when window is closed"""
		self.close_application()
		return False

	def close_application(self):
		"""Clean up and quit"""
		# Clean up temporary files
		try:
			os.unlink(self.combo)
		except:
			pass
		try:
			os.unlink(self.imagefile)
		except:
			pass
		try:
			os.unlink(self.balloonbase)
		except:
			pass
		try:
			os.unlink(self.minidream)
		except:
			pass
		try:
			os.unlink(self.dreamballoon)
		except:
			pass
