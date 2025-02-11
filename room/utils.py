from PIL import Image, ImageDraw, ImageFont
import random
import os
import hashlib
from django.conf import settings




def get_room_background_color(name):
    # Use the room name (or slug) to generate a unique but consistent color for each room
    hash_object = hashlib.md5(name.encode())
    hex_color = hash_object.hexdigest()[:6]  # Take the first 6 characters of the hash
    return f"#{hex_color}"  # Return it as a hex color code (e.g. #f0a1c2)


def get_initials(name):
    # Get the first two initials of the room name (even if it's a single word)
    words = name.split()
    initials = ''.join([word[0].upper() for word in words[:2]])  # First two initials
    return initials
