import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from helpdesk_app.models import Room, Message, CustomUser, RoomUser
from .forms import RoomForm, MessageForm
from django.conf import settings
import re
import hashlib
def get_safe_group_name(room_name):
    # Remove any characters that are not alphanumeric or hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9-]', '-', room_name)
    # Create a hash if the sanitized name is too long or if you want uniqueness
    return sanitized[:50]  # Limit length if needed

@login_required
def rooms(request):
    rooms = Room.objects.filter(users=request.user)
    room_unread_counts = {}
    
    for room in rooms:
        room_user = RoomUser.objects.filter(room=room, user=request.user).first()

        if room_user:
            last_seen_message = room_user.last_seen_message
            total_messages = room.messages.all()

            if not last_seen_message:
                unread_count = total_messages.count()
            else:
                unread_count = total_messages.filter(id__gt=last_seen_message.id).count()

            room_unread_counts[room.id] = unread_count
        else:
            room_unread_counts[room.id] = 0  # No messages if no RoomUser entry exists
   
    return render(request, 'room/room.html', {'rooms': rooms, 'room_unread_counts': room_unread_counts})
  







@login_required
def room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    
    # Ensure the room belongs to the user, or they are a participant
    if request.user not in room.users.all():
        return redirect('rooms')  # Redirect to rooms list if the user doesn't have access

    messages = Message.objects.filter(room=room).order_by('date_added')
    

    # Update last_seen_message to the most recent message when the user enters the room
    room_user, created = RoomUser.objects.get_or_create(room=room, user=request.user)
    room_user.last_seen_message = messages.last() if messages.exists() else None
    room_user.save()

    # Fetch only rooms associated with the user for the sidebar
    rooms = Room.objects.filter(users=request.user)

    return render(request, 'room/room.html', {
        'room': room,
        'rooms': rooms,  # Sidebar shows only rooms the user is part of
        'messages': messages,
        'room_name': room.slug,  # Pass the current room's slug for active class
    })




@login_required
def create_room(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        selected_user_ids = post_data.get('selected_users', '').split(',')
        selected_user_ids = [user_id for user_id in selected_user_ids if user_id.isdigit()]
        post_data.setlist('users', selected_user_ids)

        form = RoomForm(post_data, current_user=request.user)

        if form.is_valid():
            room_name = form.cleaned_data['name']
            # Check if a room with the same name already exists
            if Room.objects.filter(name=room_name).exists():
                form.add_error('name', 'Το όνομα αυτό χρησιμοποιείται ήδη.')  # Add custom error message
            else:
                room = form.save(commit=False)
                room.slug = room_name.replace(' ', '-').lower()
                room.save()

                # Automatically add the creator to the room
                room.users.add(request.user)

                # Add selected users to the room
                selected_users = CustomUser.objects.filter(id__in=selected_user_ids)
                room.users.add(*selected_users)

                return redirect('rooms')  # Redirect to rooms list after creating
        else:
            print("Form errors:", form.errors)
    else:
        form = RoomForm(current_user=request.user)

    return render(request, 'room/create_room.html', {'form': form})


# def check_room_name(request):
#     room_name = request.GET.get('name-input', '').strip()
    
#     if Room.objects.filter(name=room_name).exists():
#         return JsonResponse({'exists': True})
#     else:
#         return JsonResponse({'exists': False})

