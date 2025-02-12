# forms.py
from django import forms
from .models import CustomUser
from .models import Room, Message
from django.core.exceptions import ValidationError
import re

class RoomForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5, 'id': 'user-select'}),
        required=True
    )
    
    class Meta:
        model = Room
        fields = ['name', 'users']

    def clean_name(self):
        room_name = self.cleaned_data.get('name')
        
        # Check if the room name already exists
        if Room.objects.filter(name=room_name).exists():
            raise ValidationError('A room with this name already exists.')
        
        # Only allow Latin letters, numbers, and spaces
        if not re.match(r'^[A-Za-z0-9\s]*$', room_name):
            raise ValidationError('Room name must contain only Latin characters, numbers, and spaces.')
        
        return room_name

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(RoomForm, self).__init__(*args, **kwargs)
        
        # Customize the name field
        self.fields['name'].widget.attrs.update({
            'class': 'form-input',  # Add your custom CSS class
            'placeholder': 'Enter room name...',  # Add placeholder
            'id': 'name-input'  # Add custom ID if needed
        })

        if current_user:
            self.fields['users'].queryset = CustomUser.objects.exclude(id=current_user.id)
            self.fields['users'].label_from_instance = lambda obj: obj.username

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']  # Include the file field
