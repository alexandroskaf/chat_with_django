import hashlib
from django import template

register = template.Library()

@register.filter(name='room_color')
def room_color(room_name):
    # Generate a color hash based on the room name
    hash_object = hashlib.md5(room_name.encode())
    hash_hex = hash_object.hexdigest()
    # Convert part of the hash to a color code
    color = f"#{hash_hex[:6]}"  # First 6 characters of hash for color
    return color
