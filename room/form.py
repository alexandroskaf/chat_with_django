from django import forms
from helpdesk_app.models import CustomUser
from helpdesk_app.models import Room

class RoomForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = Room
        fields = ['name', 'slug', 'users']  # Add users field
