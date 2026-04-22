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

		# Dynamic balloon sizing
		self.balloon_width = 260
		self.balloon_height = 200
		self.balloon_padding = 20

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

	def calculate_text_size(self):
		"""Calculate the required balloon size based on text content"""
		if self.verb == 'dream':
			return self.balloon_width, self.balloon_height

		# Create a temporary image to measure text
		temp_img = Image.new('RGBA', (1, 1))
		draw = ImageDraw.Draw(temp_img)
		font = ImageFont.truetype(self.fontfile, 15)

		# Try different wrapping widths to find optimal layout
		# Start with reasonable character count and adjust based on text length
		words = self.text.split()
		word_count = len(words)

		# Determine wrap width based on total text length
		if word_count <= 5:
			wrap_width = 30
		elif word_count <= 15:
			wrap_width = 35
		elif word_count <= 30:
			wrap_width = 40
		else:
			wrap_width = 45

		# Wrap text and calculate required dimensions
		lines = textwrap.wrap(self.text, width=wrap_width)
		total_height = 0
		max_width = 0

		for line in lines:
			bbox = draw.textbbox((0, 0), line, font=font)
			line_width = bbox[2] - bbox[0]
			line_height = bbox[3] - bbox[1]
			total_height += line_height
			max_width = max(max_width, line_width)

		# Add padding for text background
		text_padding = 15

		# Store wrapped lines for later use
		self.text_lines = lines
		self.text_area_width = max_width + 2 * text_padding
		self.text_area_height = total_height + 2 * text_padding

		# For a rectangle to be inscribed in an ellipse:
		# If the rectangle has dimensions w×h, the ellipse needs semi-axes a×b where:
		# a = w/√2 and b = h/√2 for maximum inscribed rectangle
		# So ellipse diameter = rectangle dimension × √2 ≈ 1.414
		# Add extra factor for comfortable margin: use 1.6 instead of 1.414
		import math
		inscription_factor = 1.6

		required_width = self.text_area_width * inscription_factor + 2 * self.balloon_padding
		required_height = self.text_area_height * inscription_factor + 2 * self.balloon_padding

		# Set minimum and maximum sizes - allow wider balloons
		self.balloon_width = max(260, min(700, required_width))
		self.balloon_height = max(200, min(500, required_height))

		return self.balloon_width, self.balloon_height

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

		# Calculate required size based on text
		if self.balloontype != 'dream':
			self.calculate_text_size()

		# Character dimensions
		character_width = 250
		character_height = 320  # Character + base height
		left_margin = 20

		# Layout: Character on LEFT, Balloon on RIGHT (side-by-side)
		# Canvas width = left margin + character + gap + balloon + right margin
		gap_between = 20
		right_margin = 20
		canvas_width = left_margin + character_width + gap_between + self.balloon_width + right_margin

		# Canvas height = max of character height or balloon height, plus margins
		top_margin = 20
		bottom_margin = 60  # Extra space so character's base is visible
		canvas_height = max(character_height, self.balloon_height) + top_margin + bottom_margin

		# Ensure minimum dimensions
		canvas_width = max(640, canvas_width)
		canvas_height = max(400, canvas_height)

		# Convert to integers (dimensions may be floats from calculations)
		canvas_width = int(canvas_width)
		canvas_height = int(canvas_height)

		# Update image dimensions
		self.imgW = canvas_width
		self.imgH = canvas_height

		# Calculate positions
		# Character on the left side
		self.character_x = left_margin

		# Character positioned with some bottom margin so we can see its base
		bottom_character_margin = 40  # Space below character so bottom is visible
		self.character_y = canvas_height - character_height - bottom_character_margin

		# Balloon to the right of character
		# Character image is character_width (250px) wide
		# Balloon should start after character ends
		balloon_start_x = self.character_x + character_width + gap_between

		# Create base with dynamic size
		base = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
		overlay = Image.new('RGBA', base.size, (255, 255, 255, 0))
		draw = ImageDraw.Draw(overlay)

		# Calculate balloon coordinates
		balloon_left = balloon_start_x
		# Align balloon vertically with character's head area
		# Character head is roughly at the top 1/4 of character height
		character_head_y = self.character_y + 60  # Approximate head position

		# Center balloon vertically around character's head
		balloon_top = character_head_y - self.balloon_height / 2
		# Ensure balloon doesn't go off top
		balloon_top = max(top_margin, balloon_top)

		balloon_right = balloon_left + self.balloon_width
		balloon_bottom = balloon_top + self.balloon_height

		# Store balloon position for text centering later
		self.balloon_left = balloon_left
		self.balloon_top = balloon_top

		if self.balloontype == 'say':
			# Draw unified balloon + tail as ONE continuous shape
			import math

			# Character's mouth position
			character_mouth_x = self.character_x + 200
			character_mouth_y = character_head_y + 60

			# Tail attachment area
			balloon_attachment_y = max(balloon_top + 40, min(balloon_bottom - 40, character_mouth_y))
			tail_spread = 30
			tail_top_y = balloon_attachment_y - tail_spread
			tail_bottom_y = balloon_attachment_y + tail_spread

			# Create unified shape by tracing the outline
			# Start from top of balloon, go around clockwise, include tail, complete circle

			center_x = (balloon_left + balloon_right) / 2
			center_y = (balloon_top + balloon_bottom) / 2
			radius_x = (balloon_right - balloon_left) / 2
			radius_y = (balloon_bottom - balloon_top) / 2

			outline_points = []

			# Calculate angles for tail attachment points
			# Angle from center to tail points
			tail_top_angle = math.atan2(tail_top_y - center_y, balloon_left - center_x)
			tail_bottom_angle = math.atan2(tail_bottom_y - center_y, balloon_left - center_x)

			# Draw ellipse outline going clockwise, skipping the tail section
			num_ellipse_points = 100
			for i in range(num_ellipse_points + 1):
				angle = (2 * math.pi * i) / num_ellipse_points - math.pi  # Start from left (-pi)

				# Skip the section where the tail connects
				if tail_bottom_angle <= angle <= tail_top_angle:
					if len(outline_points) == 0 or outline_points[-1] != (balloon_left, tail_top_y):
						# Add top tail attachment point
						outline_points.append((balloon_left, tail_top_y))
					continue

				x = center_x + radius_x * math.cos(angle)
				y = center_y + radius_y * math.sin(angle)
				outline_points.append((x, y))

			# Add curved tail
			# Top curve of tail
			num_tail_points = 12
			for i in range(num_tail_points + 1):
				t = i / num_tail_points
				ctrl_x = (balloon_left + character_mouth_x) / 2 - 15
				ctrl_y = (tail_top_y + character_mouth_y) / 2

				x = (1-t)**2 * balloon_left + 2*(1-t)*t * ctrl_x + t**2 * character_mouth_x
				y = (1-t)**2 * tail_top_y + 2*(1-t)*t * ctrl_y + t**2 * character_mouth_y
				outline_points.append((x, y))

			# Bottom curve of tail (reverse)
			for i in range(num_tail_points, -1, -1):
				t = i / num_tail_points
				ctrl_x = (balloon_left + character_mouth_x) / 2 - 15
				ctrl_y = (tail_bottom_y + character_mouth_y) / 2

				x = (1-t)**2 * character_mouth_x + 2*(1-t)*t * ctrl_x + t**2 * balloon_left
				y = (1-t)**2 * character_mouth_y + 2*(1-t)*t * ctrl_y + t**2 * tail_bottom_y
				outline_points.append((x, y))

			# Draw the complete unified shape
			draw.polygon(outline_points, fill='white', outline='black', width=2)

			# Mark that we drew the unified shape (no separate tail needed)
			self.tail_data = None
		elif (self.balloontype == 'dream') or (self.balloontype == 'think'):
			draw.ellipse((balloon_left, balloon_top, balloon_right, balloon_bottom), fill='white', outline='black')

			# Thought bubble circles - dynamically connect to character's head
			# Position on RIGHT side of character's head (facing balloon)
			character_head_right_x = self.character_x + 200
			character_head_right_y = character_head_y + 60

			# Position bubbles in a path from character to balloon
			# Calculate positions between character and balloon
			mid_x = (balloon_left + character_head_right_x) / 2
			mid_y = (balloon_top + self.balloon_height * 0.6 + character_head_right_y) / 2

			# Store bubble positions to draw AFTER character is composited
			self.thought_bubbles = [
				(mid_x - 20, mid_y - 10, mid_x + 20, mid_y + 30),  # Larger bubble midway
				(character_head_right_x + 5, character_head_right_y - 10, character_head_right_x + 20, character_head_right_y + 5)  # Smaller bubble near character
			]
		elif self.balloontype == 'shout':
			# Scale shout polygon based on balloon size
			scale_x = self.balloon_width / 260
			scale_y = self.balloon_height / 200
			shout_points = [
				(3, 237), (29, 183), (46, 206), (56, 156),
				(12, 170), (36, 131), (3, 111), (38, 96),
				(8, 70), (51, 62), (25, 22), (85, 38), (120, 9),
				(147, 42), (191, 19), (201, 57), (252, 47), (249, 88),
				(282, 120), (235, 137), (260, 172), (210, 178),
				(233, 218), (170, 174), (148, 211), (130, 185),
				(104, 240), (94, 200), (47, 229), (29, 200)
			]
			scaled_points = [(int(x * scale_x + balloon_left), int(y * scale_y + balloon_top)) for x, y in shout_points]
			draw.polygon(scaled_points, fill='white', outline='black')
		else:
			draw.ellipse((balloon_left, balloon_top, balloon_right, balloon_bottom), fill='white')
		out = Image.alpha_composite(base, overlay)
		out.save(self.balloonbase)
		return self.balloonbase

	def draw_base(self):
		# Use character position calculated in draw_balloons
		# Character is positioned on the left side
		if hasattr(self, 'character_x') and hasattr(self, 'character_y'):
			self.character_posx = self.character_x
			self.character_posy = self.character_y
		else:
			# Fallback for dream mode
			self.character_posx = 80
			self.character_posy = self.imgH - 320
		myimage = combine_sources(self.character_posx, self.character_posy, self.bigbase, self.characterpic, self.imagefile)

	def build_popup(self):

		# Draw the balloon (which calculates layout and creates full canvas with balloon)
		self.baloon = self.draw_balloons(balloontype=self.verb)

		# For dream mode, use old positioning
		if self.verb == 'dream':
			self.baloon = self.make_dream()
			self.origx = 220
			self.origy = 0
			balloon_offset_x = 220
		else:
			# The balloon is already drawn on the full canvas at the correct position
			# We just need to overlay the character
			# Position for overlaying is (0, 0) since balloon canvas is already full size
			self.origx = 0
			self.origy = 0

		# Calculate centered position for text box within balloon
		if hasattr(self, 'text_area_width') and hasattr(self, 'text_area_height') and hasattr(self, 'balloon_left'):
			# Calculate the center of the elliptical balloon
			balloon_center_x = self.balloon_left + self.balloon_width / 2
			balloon_center_y = self.balloon_top + self.balloon_height / 2

			# Position text box so its center aligns with balloon center
			# The text box starts at center minus half its width/height
			self.textX = balloon_center_x - self.text_area_width / 2
			self.textY = balloon_center_y - self.text_area_height / 2
		else:
			# Fallback for dream mode
			self.textX = 40
			self.textY = 35

		# Create base image for character
		self.combo = "images/output.png"

		# First copy the balloon canvas as base
		import shutil
		shutil.copy(self.baloon, self.combo)

		# Draw character on separate image
		self.draw_base()

		# Overlay character onto the balloon canvas
		if self.verb != 'dream':
			myimage = combine_sources(self.character_posx, self.character_posy, self.combo, self.imagefile, self.combo)
		else:
			myimage = combine_sources(self.origx, self.origy, self.imagefile, self.baloon, self.combo)

		# draw text
		img = Image.open(self.combo)
		draw = ImageDraw.Draw(img)
		font = ImageFont.truetype(self.fontfile, 15)

		# Draw curved tail on top of character (for 'say' mode)
		if hasattr(self, 'tail_data') and self.tail_data:
			import math
			tail = self.tail_data

			tip = tail['tip']
			top_attach = tail['top_attach']
			bottom_attach = tail['bottom_attach']

			# Create smooth curved tail
			curved_points = []

			# Top curve: from top attachment point to tip
			num_points = 12
			for i in range(num_points + 1):
				t = i / num_points
				# Quadratic bezier with control point offset to create curve
				ctrl_x = (top_attach[0] + tip[0]) / 2 - 15
				ctrl_y = (top_attach[1] + tip[1]) / 2

				x = (1-t)**2 * top_attach[0] + 2*(1-t)*t * ctrl_x + t**2 * tip[0]
				y = (1-t)**2 * top_attach[1] + 2*(1-t)*t * ctrl_y + t**2 * tip[1]
				curved_points.append((x, y))

			# Bottom curve: from tip back to bottom attachment point
			for i in range(num_points, -1, -1):
				t = i / num_points
				ctrl_x = (bottom_attach[0] + tip[0]) / 2 - 15
				ctrl_y = (bottom_attach[1] + tip[1]) / 2

				x = (1-t)**2 * tip[0] + 2*(1-t)*t * ctrl_x + t**2 * bottom_attach[0]
				y = (1-t)**2 * tip[1] + 2*(1-t)*t * ctrl_y + t**2 * bottom_attach[1]
				curved_points.append((x, y))

			# Draw the curved tail
			draw.polygon(curved_points, fill='white', outline='black', width=2)
			draw.polygon(curved_points, fill='white')

		# Draw thought bubbles on top of character (for 'think' mode)
		if hasattr(self, 'thought_bubbles') and self.thought_bubbles:
			for bubble_coords in self.thought_bubbles:
				draw.ellipse(bubble_coords, fill='white', outline='black')

		if self.baloon != self.dreamballoon:
			# Use pre-calculated text lines from calculate_text_size
			if hasattr(self, 'text_lines'):
				lines = self.text_lines
			else:
				# Fallback if text_lines wasn't calculated
				lines = textwrap.wrap(self.text, width=35)

			# Calculate text area position
			text_padding = 15
			y_text_start = self.origy + self.textY
			x_text_start = self.origx + self.textX

			# Draw light yellow rectangular background for text area
			text_bg_x1 = x_text_start - text_padding
			text_bg_y1 = y_text_start - text_padding
			text_bg_x2 = text_bg_x1 + self.text_area_width
			text_bg_y2 = text_bg_y1 + self.text_area_height

			# Light yellow color for note/page effect
			yellow_bg = (255, 255, 224, 230)  # Light yellow with slight transparency
			draw.rectangle(
				[text_bg_x1, text_bg_y1, text_bg_x2, text_bg_y2],
				fill=yellow_bg,
				outline=(200, 200, 150),  # Subtle border
				width=1
			)

			# Draw text on top of yellow background
			y_text = y_text_start
			x_text = x_text_start
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
