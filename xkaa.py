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
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import sys
import os
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
import textwrap
import random
import io
import cairosvg

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

	def __init__(self, character=None, verb=None, text=None, dreamed=None, font=None, fontcolor=(0, 0, 0), placement='random', auto_close=None):

		self.imgW = 640
		self.imgH = 520
		self.character = character
		self.font = font
		self.imgdir = imgdir

		# Handle subdirectory in character name (e.g., "legacy/chicken")
		if '/' in self.character:
			char_dir, char_name = os.path.split(self.character)
			self.imagefile = os.path.join(self.imgdir, char_dir, 'ab' + char_name + ".png")
		else:
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
		self.placement = placement
		self.auto_close = auto_close

		# Check if character image exists
		if not os.path.exists(self.characterpic):
			print(f"Error: Character image '{self.characterpic}' not found.")
			print(f"Please check that the character '{character}' exists in the images directory.")
			sys.exit(1)

		# Check if dream image exists (when in dream mode)
		if verb == 'dream' and dreamed and not os.path.exists(dreamed):
			print(f"Error: Dream image '{dreamed}' not found.")
			print(f"Please provide a valid path to a dream image.")
			sys.exit(1)

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

		# Start with default font size
		font_size = 15

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

		# Wrap text and check line count
		lines = textwrap.wrap(self.text, width=wrap_width)
		line_count = len(lines)

		# Shrink font if more than 5 lines
		if line_count > 5:
			if line_count <= 8:
				font_size = 13
			elif line_count <= 12:
				font_size = 11
			else:
				font_size = 10

		# Store font size for later use
		self.font_size = font_size
		font = ImageFont.truetype(self.fontfile, font_size)

		# Calculate required dimensions with the chosen font size
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
		"""Add dream image to the balloon - now works with dynamic layout"""
		# Calculate image size based on balloon size
		# Dream image should fit nicely inside the balloon
		max_image_width = int(self.balloon_width * 0.5)
		max_image_height = int(self.balloon_height * 0.5)

		# Load and resize the dreamed image
		dream_img = Image.open(self.dreamed).convert('RGBA')
		dream_img.thumbnail((max_image_width, max_image_height), Image.LANCZOS)

		# Calculate position to center the dream image in the balloon
		balloon_center_x = self.balloon_left + self.balloon_width / 2
		balloon_center_y = self.balloon_top + self.balloon_height / 2

		image_x = int(balloon_center_x - dream_img.width / 2)
		image_y = int(balloon_center_y - dream_img.height / 2)

		# Store position for later compositing
		self.dream_image_x = image_x
		self.dream_image_y = image_y
		self.dream_image = dream_img

		return self.balloonbase

	def create_svg_speech_bubble(self, width, height, tail_x, tail_y, bubble_side='right', bubble_type='say'):
		"""Create SVG speech bubble (just the bubble) and return tail data separately"""
		import math

		# Bubble dimensions
		cx = width / 2
		cy = height / 2

		# Stroke widths following the blog post style
		outer_stroke = 6  # Thicker outer border

		if bubble_type == 'shout':
			# Create a comic book style shout bubble with uniform triangular spikes
			# Build an OVAL/ELLIPTICAL base with regular triangle spikes arranged in a circular pattern
			# One spike acts as a "tail" pointing towards the character's mouth

			svg_path = []

			# Spike parameters - proportional to bubble size (50% larger)
			spike_height = min(width, height) * 0.225  # Spike height is 22.5% of smaller dimension

			# Define the inner ellipse (where spike bases attach)
			# Leave room for spikes to extend outward
			padding = 10  # Minimal edge padding
			base_rx = width / 2 - padding - spike_height
			base_ry = height / 2 - padding - spike_height

			# Calculate the angle towards the tail (character's mouth)
			tail_angle = math.atan2(tail_y - cy, tail_x - cx)

			# Number of triangular spikes around the perimeter
			num_spikes = 16

			# Create triangular spikes arranged in a circular pattern around the ellipse
			for i in range(num_spikes):
				# Each spike is defined by three angles:
				# 1. Start angle (left edge of spike base)
				# 2. Peak angle (tip of spike pointing outward)
				# 3. End angle (right edge of spike base)

				angle_start = (i * 2 * math.pi) / num_spikes
				angle_peak = ((i + 0.5) * 2 * math.pi) / num_spikes
				angle_end = ((i + 1) * 2 * math.pi) / num_spikes

				# Check if this spike should be the "tail" (closest to tail_angle)
				angle_diff = abs(((angle_peak - tail_angle + math.pi) % (2 * math.pi)) - math.pi)
				is_tail_spike = angle_diff < (math.pi / num_spikes)

				# Start point on base ellipse
				x1 = cx + base_rx * math.cos(angle_start)
				y1 = cy + base_ry * math.sin(angle_start)

				# Peak point - for tail spike, point it towards the mouth (but limit extension)
				if is_tail_spike:
					# Point this spike towards the character's mouth
					# But extend it only spike_height distance, not all the way to the mouth
					tail_distance = math.sqrt((tail_x - cx)**2 + (tail_y - cy)**2)
					if tail_distance > 0:
						# Normalize the direction and extend by spike_height
						direction_x = (tail_x - cx) / tail_distance
						direction_y = (tail_y - cy) / tail_distance
						# Extend from the base ellipse edge
						base_edge_x = cx + base_rx * direction_x
						base_edge_y = cy + base_ry * direction_y
						x2_unclamped = base_edge_x + spike_height * 2.5 * direction_x  # Make tail 2.5x longer
						y2_unclamped = base_edge_y + spike_height * 2.5 * direction_y

						# Clamp the tail tip to stay within the SVG canvas bounds
						margin_from_edge = 5  # Keep a small margin from edge
						x2 = max(margin_from_edge, min(width - margin_from_edge, x2_unclamped))
						y2 = max(margin_from_edge, min(height - margin_from_edge, y2_unclamped))
					else:
						# Fallback
						peak_rx = base_rx + spike_height
						peak_ry = base_ry + spike_height
						x2 = cx + peak_rx * math.cos(angle_peak)
						y2 = cy + peak_ry * math.sin(angle_peak)
				else:
					# Regular spike extending outward radially
					peak_rx = base_rx + spike_height
					peak_ry = base_ry + spike_height
					x2 = cx + peak_rx * math.cos(angle_peak)
					y2 = cy + peak_ry * math.sin(angle_peak)

				# End point on base ellipse
				x3 = cx + base_rx * math.cos(angle_end)
				y3 = cy + base_ry * math.sin(angle_end)

				if i == 0:
					svg_path.append(f"M {x1:.1f},{y1:.1f}")

				svg_path.append(f"L {x2:.1f},{y2:.1f}")
				svg_path.append(f"L {x3:.1f},{y3:.1f}")

			svg_path.append("Z")
			path_data = " ".join(svg_path)

			# Set rx/ry for tail calculation
			rx = base_rx
			ry = base_ry

			# Create SVG with jagged shout bubble
			svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
			  <!-- White fill -->
			  <path d="{path_data}" fill="#fff" stroke="none"/>

			  <!-- Black border -->
			  <path d="{path_data}" fill="none" stroke="#000" stroke-width="{outer_stroke}"/>
			</svg>'''
		else:
			# For say mode - smooth ellipse
			rx = width / 2 - 10
			ry = height / 2 - 10

			# Create SVG with just the bubble (no tail) - smooth ellipse for say mode
			svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
			  <defs>
			    <ellipse id="bubble" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>
			  </defs>

			  <!-- Outer border ellipse with thick stroke -->
			  <use href="#bubble" fill="none" stroke="#000" stroke-width="{outer_stroke}"/>

			  <!-- Inner white ellipse -->
			  <use href="#bubble" fill="#fff" stroke="none"/>
			</svg>'''

		# Calculate tail geometry to be drawn later (after character)
		tail_angle = math.atan2(tail_y - cy, tail_x - cx)

		# Find the attachment point DEEP INSIDE the ellipse for seamless connection
		# The 6px border needs to be completely covered, plus we need to extend
		# far enough inside that the tail merges seamlessly with the bubble fill
		border_thickness = 6
		border_coverage = 20  # Go 20px inside to ensure seamless connection

		# Calculate how much to reduce the radius
		overlap_amount = border_coverage / min(rx, ry)
		overlap_factor = 1.0 - overlap_amount

		attach_center_x = cx + rx * overlap_factor * math.cos(tail_angle)
		attach_center_y = cy + ry * overlap_factor * math.sin(tail_angle)

		# Create two attachment points spread perpendicular to the tail direction
		tail_spread = 35  # Width of tail base at bubble
		perp_angle = tail_angle + math.pi / 2

		# Two attachment points inside the bubble
		attach1_x = attach_center_x + tail_spread * math.cos(perp_angle)
		attach1_y = attach_center_y + tail_spread * math.sin(perp_angle)
		attach2_x = attach_center_x - tail_spread * math.cos(perp_angle)
		attach2_y = attach_center_y - tail_spread * math.sin(perp_angle)

		# Calculate control points for smooth organic curves
		tail_length = math.sqrt((tail_x - attach_center_x)**2 + (tail_y - attach_center_y)**2)
		curve_offset = tail_length * 0.3  # Amount of curve

		# Control points for curved tail
		ctrl1_x = attach1_x + (tail_x - attach1_x) * 0.5 + curve_offset * math.sin(tail_angle)
		ctrl1_y = attach1_y + (tail_y - attach1_y) * 0.5 - curve_offset * math.cos(tail_angle)

		ctrl2_x = tail_x + (attach2_x - tail_x) * 0.5 + curve_offset * math.sin(tail_angle)
		ctrl2_y = tail_y + (attach2_y - tail_y) * 0.5 - curve_offset * math.cos(tail_angle)

		# Return SVG and tail geometry data
		tail_data = {
			'attach1': (attach1_x, attach1_y),
			'attach2': (attach2_x, attach2_y),
			'tip': (tail_x, tail_y),
			'ctrl1': (ctrl1_x, ctrl1_y),
			'ctrl2': (ctrl2_x, ctrl2_y)
		}

		return svg, tail_data

	def draw_balloons(self, balloontype=None):
		self.balloontype = balloontype
		''' this will create a balloon instead of using a premade one '''

		# Calculate required size based on text
		if self.balloontype != 'dream':
			self.calculate_text_size()

		# Character dimensions
		character_width = 250
		character_height = 320  # Character + base height
		margin = 20

		# Choose bubble position based on placement option
		if self.placement == 'random':
			bubble_side = random.choice(['left', 'right'])
		else:
			bubble_side = self.placement
		self.bubble_side = bubble_side

		# Canvas dimensions depend on bubble position
		# Reduce gap for shout mode since the tail extends towards the character
		gap_between = -40 if self.balloontype == 'shout' else 20
		canvas_width = margin + character_width + gap_between + self.balloon_width + margin

		# Canvas height
		top_margin = 20
		bottom_margin = 60  # Extra space so character's base is visible
		canvas_height = max(character_height, self.balloon_height) + top_margin + bottom_margin

		# Ensure minimum dimensions
		canvas_width = max(640, canvas_width)
		canvas_height = max(400, canvas_height)

		# Convert to integers
		canvas_width = int(canvas_width)
		canvas_height = int(canvas_height)

		# Update image dimensions
		self.imgW = canvas_width
		self.imgH = canvas_height

		# Character position (centered in canvas)
		if bubble_side == 'right':
			# Character on left, bubble on right
			self.character_x = margin
		else:
			# Character on right, bubble on left
			self.character_x = canvas_width - margin - character_width

		# Character positioned with bottom margin
		bottom_character_margin = 40
		self.character_y = canvas_height - character_height - bottom_character_margin

		# Balloon position
		if bubble_side == 'right':
			balloon_start_x = self.character_x + character_width + gap_between
		else:
			# Balloon on left, character on right
			balloon_start_x = self.character_x - gap_between - self.balloon_width

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

		if self.balloontype == 'say' or self.balloontype == 'shout':
			# Generate SVG speech bubble with smooth curves (say) or jagged edges (shout)
			import math

			# Character's mouth position (side facing the bubble)
			if bubble_side == 'right':
				# Bubble on right, character on left - mouth on right side of character's face
				character_mouth_x = self.character_x + 180
			else:
				# Bubble on left, character on right - mouth on left side of character's face
				character_mouth_x = self.character_x + 70
			character_mouth_y = character_head_y + 80

			# Tail coordinates relative to balloon
			tail_relative_x = character_mouth_x - balloon_left
			tail_relative_y = character_mouth_y - balloon_top

			# Generate SVG (just bubble) and get tail data for later
			svg_content, tail_data = self.create_svg_speech_bubble(
				int(self.balloon_width),
				int(self.balloon_height),
				tail_relative_x,
				tail_relative_y,
				bubble_side,
				self.balloontype
			)

			# Convert SVG to PNG
			try:
				png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
				bubble_img = Image.open(io.BytesIO(png_data))

				# Paste bubble onto canvas
				base.paste(bubble_img, (int(balloon_left), int(balloon_top)), bubble_img)
			except Exception as e:
				print(f"Error converting SVG for {self.balloontype}: {e}")
				# Fallback to simple ellipse if SVG conversion fails
				draw.ellipse((balloon_left, balloon_top, balloon_right, balloon_bottom), fill='white', outline='black')
				tail_data = None

			# Store tail data to draw AFTER character (in absolute coordinates)
			if tail_data:
				self.tail_data = {
					'attach1': (tail_data['attach1'][0] + balloon_left, tail_data['attach1'][1] + balloon_top),
					'attach2': (tail_data['attach2'][0] + balloon_left, tail_data['attach2'][1] + balloon_top),
					'tip': (tail_data['tip'][0] + balloon_left, tail_data['tip'][1] + balloon_top),
					'ctrl1': (tail_data['ctrl1'][0] + balloon_left, tail_data['ctrl1'][1] + balloon_top),
					'ctrl2': (tail_data['ctrl2'][0] + balloon_left, tail_data['ctrl2'][1] + balloon_top)
				}
			else:
				self.tail_data = None
		elif (self.balloontype == 'dream') or (self.balloontype == 'think'):
			draw.ellipse((balloon_left, balloon_top, balloon_right, balloon_bottom), fill='white', outline='black')

			# Thought bubble circles - dynamically connect to character's head
			# Position thought bubbles to connect from character's head to the balloon
			# Character head position
			if bubble_side == 'right':
				# Bubble on right, character on left - connect from right side of head
				character_head_x = self.character_x + 200
			else:
				# Bubble on left, character on right - connect from left side of head
				character_head_x = self.character_x + 50
			character_head_y = character_head_y + 60

			# Calculate connection point on the balloon (closest edge to character)
			if bubble_side == 'right':
				# Balloon is to the right, connect to left edge of balloon
				balloon_edge_x = balloon_left
			else:
				# Balloon is to the left, connect to right edge of balloon
				balloon_edge_x = balloon_right

			balloon_edge_y = balloon_top + self.balloon_height * 0.6

			# Position bubbles in a path from character to balloon
			# Small bubble near character head
			small_bubble_x = character_head_x + (15 if bubble_side == 'right' else -15)
			small_bubble_y = character_head_y
			small_radius = 8

			# Medium bubble midway
			mid_x = (balloon_edge_x + character_head_x) / 2
			mid_y = (balloon_edge_y + character_head_y) / 2
			med_radius = 15

			# Store bubble positions to draw AFTER character is composited
			self.thought_bubbles = [
				(mid_x - med_radius, mid_y - med_radius, mid_x + med_radius, mid_y + med_radius),  # Medium bubble midway
				(small_bubble_x - small_radius, small_bubble_y - small_radius, small_bubble_x + small_radius, small_bubble_y + small_radius)  # Small bubble near character
			]
		else:
			draw.ellipse((balloon_left, balloon_top, balloon_right, balloon_bottom), fill='white')
		out = Image.alpha_composite(base, overlay)
		out.save(self.balloonbase)
		return self.balloonbase

	def draw_base(self):
		# Use character position calculated in draw_balloons
		if hasattr(self, 'character_x') and hasattr(self, 'character_y'):
			self.character_posx = self.character_x
			self.character_posy = self.character_y

			# Create transparent canvas matching the current image dimensions
			base_canvas = Image.new('RGBA', (self.imgW, self.imgH), (255, 255, 255, 0))
			character = Image.open(self.characterpic).convert('RGBA')
			base_canvas.paste(character, (self.character_posx, self.character_posy), character)
			base_canvas.save(self.imagefile)

	def build_popup(self):

		# Draw the balloon (which calculates layout and creates full canvas with balloon)
		self.baloon = self.draw_balloons(balloontype=self.verb)

		# For dream mode, prepare the dream image
		if self.verb == 'dream':
			self.baloon = self.make_dream()

		# The balloon is already drawn on the full canvas at the correct position
		# We just need to overlay the character
		# Position for overlaying is (0, 0) since balloon canvas is already full size
		self.origx = 0
		self.origy = 0

		# Calculate centered position for text box within balloon (not used for dream mode)
		if self.verb != 'dream' and hasattr(self, 'text_area_width') and hasattr(self, 'text_area_height') and hasattr(self, 'balloon_left'):
			# Calculate the center of the elliptical balloon
			balloon_center_x = self.balloon_left + self.balloon_width / 2
			balloon_center_y = self.balloon_top + self.balloon_height / 2

			# Position text box so its center aligns with balloon center
			# The text box starts at center minus half its width/height
			self.textX = balloon_center_x - self.text_area_width / 2
			self.textY = balloon_center_y - self.text_area_height / 2

		# Create base image for character
		self.combo = "images/output.png"

		# First copy the balloon canvas as base
		import shutil
		shutil.copy(self.baloon, self.combo)

		# Draw character on separate image
		self.draw_base()

		# Overlay character onto the balloon canvas
		# Character is already positioned in self.imagefile at the correct coordinates
		# So composite at (0, 0) to preserve the positioning
		myimage = combine_sources(0, 0, self.combo, self.imagefile, self.combo)

		# draw text
		img = Image.open(self.combo).convert('RGBA')
		draw = ImageDraw.Draw(img)
		# Use the font size calculated in calculate_text_size(), or default to 15
		font_size = getattr(self, 'font_size', 15)
		font = ImageFont.truetype(self.fontfile, font_size)

		# Draw curved tail on top of character (for 'say' mode only) using SVG
		if hasattr(self, 'tail_data') and self.tail_data and self.verb == 'say':
			tail = self.tail_data

			attach1 = tail['attach1']
			attach2 = tail['attach2']
			tip = tail['tip']
			ctrl1 = tail['ctrl1']
			ctrl2 = tail['ctrl2']

			# Build SVG path for the tail using quadratic bezier curves
			# M = move to attach1, q = curve to tip, q = curve to attach2, Z = close path
			ctrl1_rel_x = ctrl1[0] - attach1[0]
			ctrl1_rel_y = ctrl1[1] - attach1[1]
			tip_rel_x = tip[0] - attach1[0]
			tip_rel_y = tip[1] - attach1[1]

			ctrl2_rel_x = ctrl2[0] - tip[0]
			ctrl2_rel_y = ctrl2[1] - tip[1]
			attach2_rel_x = attach2[0] - tip[0]
			attach2_rel_y = attach2[1] - tip[1]

			# Calculate points on the bubble edge for the stroke
			import math

			# Get bubble center and dimensions
			bubble_cx = self.balloon_left + self.balloon_width / 2
			bubble_cy = self.balloon_top + self.balloon_height / 2
			bubble_rx = self.balloon_width / 2 - 10
			bubble_ry = self.balloon_height / 2 - 10

			# Find where the tail meets the bubble edge
			# Calculate angle from bubble center to tip
			tail_angle = math.atan2(tip[1] - bubble_cy, tip[0] - bubble_cx)

			# Points on the ellipse edge where stroke should start
			edge_center_x = bubble_cx + bubble_rx * math.cos(tail_angle)
			edge_center_y = bubble_cy + bubble_ry * math.sin(tail_angle)

			# Perpendicular spread
			tail_spread = 35
			perp_angle = tail_angle + math.pi / 2

			stroke_start1_x = edge_center_x + tail_spread * math.cos(perp_angle)
			stroke_start1_y = edge_center_y + tail_spread * math.sin(perp_angle)
			stroke_start2_x = edge_center_x - tail_spread * math.cos(perp_angle)
			stroke_start2_y = edge_center_y - tail_spread * math.sin(perp_angle)

			# Build tail SVG using a white-filled ellipse to hide stroke inside bubble
			# This approach: draw the full stroke, then cover the inside part
			tail_svg = f'''<svg width="{img.width}" height="{img.height}" xmlns="http://www.w3.org/2000/svg">
			  <!-- Filled tail shape (deep inside for seamless connection) -->
			  <path d="M {attach1[0]:.1f},{attach1[1]:.1f} q {ctrl1_rel_x:.1f},{ctrl1_rel_y:.1f} {tip_rel_x:.1f},{tip_rel_y:.1f} q {ctrl2_rel_x:.1f},{ctrl2_rel_y:.1f} {attach2_rel_x:.1f},{attach2_rel_y:.1f} Z" fill="#fff" stroke="none"/>

			  <!-- Full stroke path (same as fill) -->
			  <path d="M {attach1[0]:.1f},{attach1[1]:.1f} q {ctrl1_rel_x:.1f},{ctrl1_rel_y:.1f} {tip_rel_x:.1f},{tip_rel_y:.1f} q {ctrl2_rel_x:.1f},{ctrl2_rel_y:.1f} {attach2_rel_x:.1f},{attach2_rel_y:.1f}" fill="none" stroke="#000" stroke-width="3"/>

			  <!-- White-filled ellipse to cover the stroke inside the bubble -->
			  <ellipse cx="{bubble_cx}" cy="{bubble_cy}" rx="{bubble_rx - 1.5}" ry="{bubble_ry - 1.5}" fill="#fff" stroke="none"/>
			</svg>'''

			# Debug: save the SVG to see what's being generated
			# with open('/tmp/debug_tail.svg', 'w') as f:
			#     f.write(tail_svg)

			# Convert tail SVG to PNG
			try:
				tail_png_data = cairosvg.svg2png(bytestring=tail_svg.encode('utf-8'))
				tail_layer = Image.open(io.BytesIO(tail_png_data))

				# Composite the tail onto the main image
				img = Image.alpha_composite(img, tail_layer)

				# Recreate draw object since img was replaced
				draw = ImageDraw.Draw(img)
			except Exception as e:
				print(f"Error converting tail SVG: {e}")

		# Draw thought bubbles on top of character (for 'think' and 'dream' modes)
		if hasattr(self, 'thought_bubbles') and self.thought_bubbles:
			for bubble_coords in self.thought_bubbles:
				draw.ellipse(bubble_coords, fill='white', outline='black')

		# For dream mode, composite the dream image onto the balloon
		if self.verb == 'dream' and hasattr(self, 'dream_image'):
			img.paste(self.dream_image, (self.dream_image_x, self.dream_image_y), self.dream_image)
			# Recreate draw object since we modified img
			draw = ImageDraw.Draw(img)

		if self.verb != 'dream':
			# Use pre-calculated text lines from calculate_text_size
			if hasattr(self, 'text_lines'):
				lines = self.text_lines
			else:
				# Fallback if text_lines wasn't calculated
				lines = textwrap.wrap(self.text, width=35)

			# Calculate text area position
			text_padding = 15

			# textX and textY point to where the text_area (including padding) should start
			text_area_x = self.origx + self.textX
			text_area_y = self.origy + self.textY

			# Draw light yellow rectangular background for text area
			# The background should be exactly the text_area size
			text_bg_x1 = text_area_x
			text_bg_y1 = text_area_y
			text_bg_x2 = text_area_x + self.text_area_width
			text_bg_y2 = text_area_y + self.text_area_height

			# Light yellow color for note/page effect
			yellow_bg = (255, 255, 224, 230)  # Light yellow with slight transparency
			draw.rectangle(
				[text_bg_x1, text_bg_y1, text_bg_x2, text_bg_y2],
				fill=yellow_bg,
				outline=(200, 200, 150),  # Subtle border
				width=1
			)

			# Draw text inside the padded area (text starts at padding offset from area edge)
			y_text = text_area_y + text_padding
			x_text = text_area_x + text_padding
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

		# Set up auto-close timer if specified
		if self.auto_close is not None:
			GLib.timeout_add_seconds(self.auto_close, self.auto_close_window)

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
		"""Handle drag end"""
		# Reset drag state
		self.drag_started = False

	def auto_close_window(self):
		"""Automatically close window after timeout"""
		self.window.close()
		return False  # Stop the timer

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
