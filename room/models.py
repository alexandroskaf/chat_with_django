from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q
from django.db.models import Max



from django.core.validators import RegexValidator

# middleware configuration

from django.conf import settings
from django.contrib.auth.models import User

from django.db import models

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', User)

class CustomUser(AbstractUser):
    """Model representing a user, deviating from the default Django User model"""

   

    # regular expression to validate the user's phone number
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{7,15}$",
        message="Το τηλέφωνο επικοινωνίας πρέπει να είναι της μορφής 1234567890 με ή χωρίς εθνικό πρόθεμα",
    )

    # phone number
    phone = models.CharField(
        verbose_name="Τηλέφωνο επικοινωνίας",
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )  # validators should be a list

    # for security reasons, every user should update their original reasons
    password_has_changed = models.BooleanField(
        default=False,
        verbose_name="Ανανέωση Κωδικού",
    )
    
    # returns true if the user is a admin
    def is_admin(self):
        return self.groups.filter(name="admins").exists()

    # returns true if the user is a manager
    def is_manager(self):
        return self.groups.filter(name="managers").exists()

    # returns true if the user is a dispatcher
    def is_dispatcher(self):
        return self.groups.filter(name="dispatchers").exists()

    def is_ddb(self):
        return self.groups.filter(name="ddb").exists()

    # returns true if the user has no particular role
    def is_simple_user(self):
        return not (
            self.is_admin() or self.is_manager() or self.is_dispatcher() or self.is_ddb()
        )

    

    class Meta:
        verbose_name = "Χρήστης"
        verbose_name_plural = "Χρήστες"

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    users = models.ManyToManyField(CustomUser, through='RoomUser', related_name='rooms')  # Specify through

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='messages', on_delete=models.CASCADE)
    # room_test = models.ForeignKey(Room, related_name='messages_test', on_delete=models.CASCADE,  null=True)

    content = models.TextField()
    file = models.FileField(upload_to='uploads/', blank=True)  # Add this line
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)

class RoomUser(models.Model):  # Intermediate model to track users in rooms
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    last_seen_message = models.ForeignKey(Message, null=True, blank=True, on_delete=models.SET_NULL)  # Tracks the last seen message
    is_in_room = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False) 
    class Meta:
        unique_together = (('room', 'user'),)  # Ensure unique pairs of room and user
        db_table = 'room_room_users'

    def __str__(self):
        return f'{self.user.username} in {self.room.name}'