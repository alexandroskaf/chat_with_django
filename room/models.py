# from helpdesk_app.models import CustomUser
# from django.db import models

# class Room(models.Model):
#     name = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)
#     users = models.ManyToManyField(CustomUser, through='RoomUser', related_name='rooms')  # Specify through

#     def __str__(self):
#         return self.name


# class RoomUser(models.Model):  # Intermediate model
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = (('room', 'user'),)  # Ensure unique pairs of room and user
#         db_table = 'room_room_users'

# class Message(models.Model):
#     room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, related_name='messages', on_delete=models.CASCADE)
#     content = models.TextField()
#     date_added = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ('date_added',)
