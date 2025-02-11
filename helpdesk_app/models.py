from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q
from django.db.models import Max

from .models_managers import *
from .validators import *
from .rank_choices import *

from django.core.validators import RegexValidator

# middleware configuration

from django.conf import settings
from django.contrib.auth.models import User

from django.db import models
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', User)





# the default django User model will not be used; instead we use the AUTH_USER_MODEL we declare
# in settings.py, which will be defined here

class Visitor(models.Model):
    """Model representing a simple user of the helpdesk application."""
    
    # this model 'extends' the CustomUser model
    user = models.OneToOneField(AUTH_USER_MODEL, null=False, related_name='visitor', on_delete=models.CASCADE)
    # session data key
    session_key = models.CharField(null=False, max_length=40)

# end of middleware configuration

class Unit(models.Model):
    """Model representing a unit served by the helpdesk application"""

    # unit name
    name = models.CharField(unique=True, max_length=100, verbose_name="Όνομα σχηματισμού/μονάδας")

    # unit location
    location = models.CharField(blank = True, null=True, max_length=100, verbose_name="Τοποθεσία")

    # parent formation that the unit is a part of
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name="parent_related_name", verbose_name="Σχηματισμός που υπάγεται")

    # major formation that the unit is a part of
    major_formation = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name="major_formation_related_name", verbose_name="Μείζων σχηματισμός")

    # returns true if this unit is a formation
    is_formation = models.BooleanField(default=False, verbose_name="Σχηματισμός")

    # returns true if this unit is 'major'
    is_major = models.BooleanField(default=False, verbose_name="Μείζων")

    objects = UnitManager()

    def __str__(self):
        """String for representing the Unit object."""
        return self.name

    class Meta:
        verbose_name = "Σχηματισμός - Μονάδα"
        verbose_name_plural = "Σχηματισμοί - Μονάδες"


class CommunicationMeans(models.Model):
    """Model representing a communication system"""

    # system name
    name = models.CharField(unique=True, max_length=100, verbose_name="Όνομα Συστήματος")

    objects = CommunicationMeansManager()
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Επικοινωνιακό Σύστημα"
        verbose_name_plural = "Επικοινωνιακά Συστήματα"


class CustomUser(AbstractUser):
    """Model representing a user, deviating from the default Django User model"""

    unit = models.ForeignKey(Unit, null=True, on_delete=models.SET_NULL, verbose_name=Unit._meta.verbose_name)

    means = models.ManyToManyField(CommunicationMeans, blank=True, verbose_name="Υπεύθυνος Τηλεπικοινωνιακού Μέσου",)

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

    def __str__(self):
        """String for representing the CustomUser model."""
        if self.last_name is None:
            name = f"{self.first_name}"
        else:
            name = f"{self.first_name} {self.last_name}"
        unit = str(self.unit)

        if self.is_admin():
            return f"{name} ({unit}/admin)"
        
        elif self.is_manager():
            return f"{name} ({unit}/manager)"

        elif self.is_dispatcher():
            return f"{name} ({unit}/{str(self.means.first())})"

        else:
            return f"{name} ({unit})"

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

class NetworkSpeed(models.Model):
    """Model representing the available network speeds."""

    # network speed value
    name = models.CharField(primary_key=True, unique=True, max_length=100, verbose_name="Ταχύτητα")

    def __str__(self):
        """String for representing the NetworkSpeed object."""
        return self.name

    class Meta:
        verbose_name = "Ταχύτητα"
        verbose_name_plural = "Ταχύτητες"


class Routing(models.Model):
    """Model representing the different types of routing options."""

    # routing name
    name = models.CharField(primary_key=True, unique=True, max_length=100, verbose_name="Όνομα Δρομολόγησης")

    def __str__(self):
        """String for representing the Routing object."""
        return self.name

    class Meta:
        verbose_name = "Δρομολόγηση"
        verbose_name_plural = "Δρομολογήσεις"


class DigConnection(models.Model):
    """Model representing all digital connections between units."""

    # unique number identifing this digital connection
    number = models.PositiveIntegerField(unique=True, verbose_name="Αριθμός")

    # symbolic name for this connection
    name = models.CharField( max_length=100, default="", blank=True, null=True, verbose_name="Σύνδεση", )

    # the formation which the "unit_form" unit is a part of
    formation_from = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="formation_dig_conn_a", verbose_name="Σχηματισμός Α")

    # the unit that this digital connection begins from
    unit_from = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="unit_from", verbose_name="Μονάδα Α")

    # the formation which the "unit_to" unit is a part of
    formation_to = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="formation_dig_conn_b", verbose_name="Σχηματισμός Β")

    # the unit that this digital connection ends in
    unit_to = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="unit_to", verbose_name="Μονάδα Β")

    # the speed of this digial connection
    speed = models.ForeignKey(NetworkSpeed, blank=True, null=True, on_delete=models.PROTECT, verbose_name=NetworkSpeed._meta.verbose_name)

    # the communication system that this digital connection uses
    means = models.ForeignKey(CommunicationMeans,null=True,on_delete=models.PROTECT,verbose_name=CommunicationMeans._meta.verbose_name,)

    # routing system used for this digital connection
    route = models.ForeignKey(Routing,null=True,on_delete=models.PROTECT,verbose_name=Routing._meta.verbose_name,)

    # eksokeimeni
    external = models.BooleanField( default=False, verbose_name="Εξωκείμενη Γραμμή ΕΨΑΔ", )

    objects = DigConnectionManager()

    def __str__(self):
        number = str(self.number)
        means = str(self.means)
        name = str(self.name)
        if self.external:
            is_external = " | ΕΞΩΚΕΙΜΕΝΗ"
        else:
            is_external = ""
        return f"DIG {number}: {name} ({means}{is_external})"

    class Meta:
        verbose_name = "Ψηφιακό Κύκλωμα"
        verbose_name_plural = "Ψηφιακά Κυκλώματα"


class PyrseiaServer(models.Model):
    #Εξυπηρετητές Πυρσεία

    name = models.CharField(null=True, max_length=100, verbose_name="Όνομα Εξυπηρετητή")

    # the unit that the server is a part of
    unit = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="unit_pyrseia", verbose_name="Μονάδα")

    # the formation which the node's unit is a part of
    formation = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="formation_pyrseia", verbose_name="Σχηματισμός")

    #server domain ID
    domain = models.CharField( unique=True, max_length=100, verbose_name="Domain",)

    #the server with whom it is directly connected
    exchange = models.CharField( unique=True, max_length=100, verbose_name="Exchange", )

    esxi = models.GenericIPAddressField(  unique=True, max_length=100, verbose_name="ESXi", )

    #Default Gateway
    default_gateway = models.GenericIPAddressField(unique=True,max_length=100,verbose_name="Default Gateway",)

    objects = PyrseiaServerManager()

    def __str__(self):
        return f"ΠΥΡΣΕΙΑ - {self.name}"

    class Meta:
        verbose_name = "Εξυπηρετητής Πυρσεία"
        verbose_name_plural = "Εξυπηρετητές Πυρσεία"


class BroadbandTransceiver(models.Model):
    #Πομποδέκτες Ευρυζωνικού

    #Hostname-ID
    hostname = models.CharField( unique=True, max_length=100, verbose_name="Hostname", )

    #Units it connects
    coupling = models.CharField(null=True, blank=True, max_length=100, verbose_name="Ζεύξη", )

    #Hidden(?)(coupling code)
    coupling_code = models.CharField(null=True, blank=True, max_length=100, verbose_name="Κωδικός Ζεύξης", )

    # broadband tranceiver model
    model = models.CharField(null=True, blank=True, max_length=100, verbose_name="Μοντέλο", )

    # the formation which the "unit_form" unit is a part of
    formation = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.PROTECT, related_name="formation_broadband", verbose_name="Σχηματισμός")

    # the unit that this digital connection begins from
    unit_from = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.PROTECT, related_name="unit_from_broadband", verbose_name="Από")

    # the unit that this digital connection ends in
    unit_to = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.PROTECT, related_name="unit_to_broadband", verbose_name="Προς")

    objects = BroadbandTransceiverManager()

    def __str__(self):
        if self.coupling is None: 
            coupling = ""
        else:
            coupling = f" {self.coupling}"
        return f"{self.hostname}{coupling}"

    class Meta:
        verbose_name = "Πομποδέκτης Ευρυζωνικού"
        verbose_name_plural = "Πομποδέκτες Ευρυζωνικού"


class SatelliteNode(models.Model):
    #Δορυφορικοί Κόμβοι

    #Name of the Node
    name = models.CharField( unique=True, max_length=100, verbose_name="Όνομα Κόμβου", )

    # the unit that this satellite node belongs to
    unit = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="unit_satellite", verbose_name="Από")

    # The location-Unit in which the Node is put
    formation = models.ForeignKey( Unit, null=True, on_delete=models.PROTECT, related_name="formation_satellite", verbose_name="Ένταξη σε Δορυφορικό Δίκτυο Σχηματισμού",)

    objects = SatelliteNodeManager()

    def __str__(self):
        return f"{self.name} ({str(self.formation)})" 

    class Meta:
        verbose_name = "Δορυφορικός Κόμβος"
        verbose_name_plural = "Δορυφορικοί Κόμβοι"


class HermesNode(models.Model):
    #Κόμβοι Ερμή

    #Number -ID of the node
    number = models.PositiveIntegerField( unique=True, verbose_name="Αριθμός Κόμβου", )

    #Location of the Node
    location = models.CharField( max_length=100, verbose_name="Τοποθεσία", )

    #Type of the Node
    node_type = models.CharField( max_length=100, verbose_name="Τύπος Κόμβου", )

    # the formation which the node's unit is a part of
    formation = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="formation_hermes_node", verbose_name="Σχηματισμός")

    # the unit that the hermes node is a part of
    unit = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, related_name="unit_hermes_node", verbose_name="Μονάδα")

    objects = HermesNodeManager()

    def __str__(self):
        return f"{self.number} {str(self.location)}" 

    class Meta:
        verbose_name = "Κόμβος Ερμή"
        verbose_name_plural = "Κόμβοι Ερμή"


class HermesConnection(models.Model):
    #Ζεύξεις Ερμή

    #Number-ID of the Connection
    number = models.PositiveIntegerField( unique=True, verbose_name="Αριθμός Ζεύξης", )

    #Starting Point of the Connection
    node_from = models.ForeignKey( HermesNode, null=True, on_delete=models.PROTECT, related_name="node_from", verbose_name="Από",)

    #Ending Point of the Connection
    node_to = models.ForeignKey( HermesNode, null=True, on_delete=models.PROTECT, related_name="node_to", verbose_name="Προς",)

    objects = HermesConnectionManager()

    def __str__(self):
        id = str(self.id)
        node_from = str(self.node_from)
        node_to = str(self.node_to)
        return f"HLN {id}: {node_from} - {node_to}"

    class Meta:
        verbose_name = "Ζεύξη Ερμή"
        verbose_name_plural = "Ζεύξεις Ερμή"


class HarpCorrespondent(models.Model):
    #Ανταποκριτές Χαρπ

    #Name of the Harp correspondent
    correspondent = models.CharField( max_length=100, verbose_name="Ανταποκριτής", )

    #Formation to which the correspondent is located
    formation = models.ForeignKey( Unit, null=True, on_delete=models.PROTECT, related_name="formation", verbose_name="Σχηματισμός",)

    #Unit to which the correspondent is located
    unit = models.ForeignKey( Unit, null=True, on_delete=models.PROTECT, related_name="unit", verbose_name="Μονάδα",)

    #Number-ID of the Correspondent
    number = models.PositiveIntegerField( unique=True, verbose_name="Aριθμός Ανταποκριτή",)

    #Device Type of the Correspondent
    device_type = models.CharField( max_length=100, verbose_name="Τύπος Συσκευής", )

    #is the correspondent being tracked or not
    is_track_harp = models.BooleanField( default=False, verbose_name="Track Harp", )

    objects = HarpCorrespondentManager()

    def __str__(self):
        return f"{str(self.correspondent)}" 
        

    class Meta:
        verbose_name = "Ανταποκριτής Harp"
        verbose_name_plural = "Ανταποκριτές Harp"


class State(models.TextChoices):
    # possible Failure states - in order

    NEW = "NE", _("ΝΕΑ")
    OPEN = "OP", _("ΕΚΚΡΕΜΗΣ")
    PROGRESS = "PR", _("ΣΕ ΕΞΕΛΙΞΗ")
    CLOSED = "CL", _("ΔΙΕΚΠΕΡΑΙΩΜΕΝΗ")


# class Comment(models.Model):
#     #Σχόλια

#     #Report to which the comment is made(?)
#     report = models.ForeignKey( Report, null=True, on_delete=models.CASCADE, related_name="report", verbose_name="Αναφορά",)

#     #Author of the comment
#     author = models.ForeignKey( CustomUser, null=True, on_delete=models.SET_NULL, related_name="author", verbose_name="Χρηστης", )

#     #Actual Text of the comment
#     text = models.TextField( verbose_name="Σχόλιο", )
    
#     #Date on which the comment is created
#     created_date = models.DateTimeField( auto_now=True, verbose_name="Ημερομηνία καταχώρησης", )

#     #Flag indicating if the comment has been approved
#     approved_comment = models.BooleanField( default=False, verbose_name="Έγκυρο",)

#     objects = CommentManager()

#     def save(self, *args, **kwargs):
#         self.text = self.text.upper()
#         super(Comment, self).save(*args, **kwargs)

#     def approve(self):
#         self.approved_comment = True
#         self.save()

#     def __str__(self):
#         return self.text

#     class Meta:
#         verbose_name = "Σχόλιο Αναφοράς"
#         verbose_name_plural = "Σχόλια Αναφορών"


class FailureType(models.Model):
    """Model representing different types of failure."""

    # name of the current failure
    name = models.CharField( max_length=100, verbose_name="Όνομα Βλάβης", )

    # communication means that this failure affects (dides, pyrseia,..)
    means = models.ForeignKey(CommunicationMeans, null=True, on_delete=models.PROTECT, verbose_name=CommunicationMeans._meta.verbose_name,)

    def __str__(self):
        if self.means is not None:
            return f"{self.name} - {str(self.means)}"
        else:
            return self.name

    class Meta:
        verbose_name = "Τύπος Βλάβης"
        verbose_name_plural = "Τύπος Βλάβης"


class Failure(models.Model):   

    """Model representing a single failure."""

    # the location where a user-provided file, if any, will be stored
    # check MEDIA_ROOT, MEDIA_URL configurations from settings/common.py
    def upload_location(self, filename):
        return f"failures/failure_{self.number}/{filename}"

    # number of the failure - just for display reasons
    # created by the create_failure_number method when the failure is first saved in the db
    number = models.IntegerField(unique=True, verbose_name="Α/Α", )

    # simple-small description of the Failure
    description = models.TextField(blank=True, verbose_name="Περιγραφή", )

    # the communication means on which the Failure was caused
    means = models.ForeignKey(CommunicationMeans, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=CommunicationMeans._meta.verbose_name,)

    # Failure type, based on the communication means (different means have different types of Failure)
    failure_type = models.ForeignKey(FailureType, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=FailureType._meta.verbose_name,)
    
    # unit where the Failure is located
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.PROTECT, verbose_name="Επηρεαζόμενος Κόμβος",)

    # formation where the unit hierarchically belongs to
    supervisor_unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.PROTECT, related_name="supervisor_unit", verbose_name="Προϊστάμενος Σχηματισμός",)

    # major formation where the unit hierachically belongs to
    supervisor_major_formation = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.PROTECT, related_name="supervisor_major_formation", verbose_name="Προϊστάμενος Μείζων Σχηματισμός",)

    # current state of the Failure
    status = models.CharField(max_length=2, choices=State.choices, default=State.NEW, verbose_name="Κατάσταση",)

    # failure occurred on this day
    date_occurred = models.DateField( blank=True, null=True, verbose_name="Παρουσιάστηκε στις",)

    # Failure submission date
    date_start = models.DateTimeField( blank=True, null=True, verbose_name="Ημερομηνία Καταχώρησης",)

    # Failure last modification date
    date_last_modified = models.DateTimeField(auto_now=True, verbose_name="Τελευταία Ενημέρωση",)

    # Failure resolution date
    date_end = models.DateTimeField(blank=True, null=True, verbose_name="Ημερομηνία Διεκπεραίωσης",)

    # rank of the Failure submitter
    submitter_rank = models.CharField( max_length = 10, choices = RANK_CHOICES, default = 'lxias', verbose_name = 'Βαθμός Καταχωρητή')

    # name of the Failure submitter
    submitter_name = models.CharField( max_length = 30, null=True, verbose_name = 'Όνομα Καταχωρητή')

    # user account of the submitter
    submitter_user = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="submitter_user", verbose_name="Λογαριασμός Χρήστη Καταχωρητή",)

    # dispatcher assigned to resolve this report
    assigned_dispatcher = models.ForeignKey(CustomUser, limit_choices_to={'groups__name': "dispatchers"}, blank=True, null = True, on_delete=models.SET_NULL, related_name = "dispatcher_user", verbose_name="Διεκπεραιωτής Βλάβης",)

    # steps to solve the failure - provided by the failure's assigned dispatcher - optional
    solution = models.TextField(blank=True, verbose_name="Επίλυση", )

    # user-provided file referring to this Failure
    attached_file = models.FileField(blank=True, null=True, upload_to=upload_location, verbose_name="Επισυναπτόμενο Αρχείο", validators=[validate_file_extension], )

    # regular expression to validate the phone number provided by the submitter
    phone_regex = RegexValidator(regex=r"^\+?1?\d{7,15}$", message="Το τηλέφωνο επικοινωνίας πρέπει να είναι της μορφής 1234567890 με ή χωρίς εθνικό πρόθεμα", )
    
    # contact
    # primary phone
    primary_phone = models.CharField(verbose_name="Τηλέφωνο επικοινωνίας No.1", validators=[phone_regex], max_length=17, blank=True,)

    # secondary phone 
    secondary_phone = models.CharField(verbose_name="Τηλέφωνο επικοινωνίας No.2", validators=[phone_regex], max_length=17, blank=True,)

    # digital connection affected by this Failure - for both DIDES and EPSAD failures
    related_dig_connection = models.ForeignKey( DigConnection, blank=True, null=True, on_delete=models.SET_NULL, related_name="related_dig_connection", verbose_name=DigConnection._meta.verbose_name, )

    # satellite node affected by this Failure
    related_satellite_node = models.ForeignKey( SatelliteNode, blank=True, null=True, on_delete=models.SET_NULL, related_name="related_satellite_node", verbose_name=SatelliteNode._meta.verbose_name, )

    # broadband transceiver affected by this Failure
    related_broadband_transceiver = models.ManyToManyField( BroadbandTransceiver, blank=True, related_name="related_broadband_transceiver", verbose_name=BroadbandTransceiver._meta.verbose_name, )

    # harp correspondent affected by this Failure
    related_harp_correspondent = models.ForeignKey( HarpCorrespondent, blank=True, null=True, on_delete=models.SET_NULL, related_name="related_harp_correspondent", verbose_name=HarpCorrespondent._meta.verbose_name, )

    # ERMIS 
    related_hermes_node = models.ForeignKey(HermesNode, blank=True, null=True, on_delete=models.SET_NULL, related_name="related_hermes_node", verbose_name=HermesNode._meta.verbose_name, )
    related_hermes_connection = models.ForeignKey(HermesConnection, blank=True, null=True, on_delete=models.SET_NULL, related_name="related_hermes_connection", verbose_name=HermesConnection._meta.verbose_name, )

    # pyrseia server affected by this Failure
    related_pyrseia_server = models.ForeignKey( PyrseiaServer, blank=True, null=True, on_delete=models.SET_NULL, related_name="related_pyrseia_server", verbose_name=PyrseiaServer._meta.verbose_name,)

    # custom object manager
    objects = FailureManager()

    # using the python @property decorator, we can use is_modified both as a method and as a field
    @property
    def is_modified(self):
        if self.date_start != self.date_last_modified:
            return True
        return False

    # save the newly created Failure
    def save(self, *args, **kwargs):
        # if this Failure is being created right now, so this is the first time it is saved
        if self.pk is None:
            self.create_failure_number()
            self.date_start = timezone.localtime(timezone.now())

        # capitalize Failure description and submitter name
        self.description = self.description.upper()
        self.submitter_name = self.submitter_name.upper()

        super(Failure, self).save(*args, **kwargs)

    # custom delete method, to be able to first delete any provided attached files 
    def delete(self, *args, **kwargs):
        self.attached_file.delete()
        super(Failure, self).delete(*args, **kwargs)

    # function that creates this failure's number
    def create_failure_number(self):
        if Failure.objects.count() == 0:
            new_failure_number_value = 0
        else:
            # get the most recent failure's number
            last_failure_number = Failure.objects.all().aggregate(Max("number"))
            # extract the last 4 digits
            last_failure_number_value = str(last_failure_number["number__max"])[-4:]
            # add 1
            new_failure_number_value = int(last_failure_number_value) + 1

        # id convention -> 77 + 5-digit-formatted id
        id_string = "77" + format(new_failure_number_value, "05d")
        self.number = id_string


    # returns True if the user making the request is this Failure's original submitter
    def submitted_by(self, user):
        return self.submitter_user == user

    # returns True if the user making the request is this Failure's assigned dispatcher
    def dispatched_by(self, user):
        return self.assigned_dispatcher == user

    # returns True if the user making the request has editing rights on this failure
    def can_edit(self, user):
        # a failure can be edited by
        if user.is_admin() or user.is_manager():
            return True
        
        elif user.is_ddb():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        elif user.is_dispatcher():
            if self.submitted_by(user) or self.dispatched_by(user):
                return True
            else:
                return False
            
        elif user.is_simple_user():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        else:
            return False

    # returns True if the user making the request has deleting rights on this failure
    def can_delete(self, user):
        if user.is_admin() or user.is_manager():
            return True

        elif user.is_ddb():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        elif user.is_dispatcher():
            if self.submitted_by(user) or self.dispatched_by(user):
                return True
            elif self.means in user.means.all():
                return True
            else:
                return False
            
        elif user.is_simple_user():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        else:
            return False

    # returns True if the user making the request has completing rights on this failure
    def can_complete(self, user):
        if (user.is_admin() or user.is_manager()) and self.status != State.CLOSED:
            return True

        elif user.is_ddb():
            if self.status != State.CLOSED:
                return True 
            else:
                return False
        
        elif user.is_dispatcher():
            if self.submitted_by(user) or self.dispatched_by(user):
                return True
            else:
                return False     

        elif user.is_simple_user():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        else:
            return False  

    def __str__(self):
        return "{0}-{1}".format(self.number, self.description)

    class Meta:
        verbose_name = "Βλάβη"
        verbose_name_plural = "Βλάβες"


class Report(models.Model):   

    """Model representing a single report."""

    # the location where a user-provided file, if any, will be stored
    # check MEDIA_ROOT, MEDIA_URL configurations from settings/common.py
    def upload_location(self, filename):
        return f"reports/report_{self.number}/{filename}"

    # number of the report - just for display reasons
    # created by the create_report_number method when the report is first saved in the db
    number = models.IntegerField(unique=True, verbose_name="Α/Α", )

    # simple-small description of the Failure
    description = models.TextField(blank=True, verbose_name="Περιγραφή", )

    # the communication means on which the Failure was caused
    means = models.ForeignKey(CommunicationMeans, null=True, on_delete=models.SET_NULL, verbose_name=CommunicationMeans._meta.verbose_name,)
 
    # unit where the report is located
    unit = models.ForeignKey(Unit, null=True, on_delete=models.PROTECT, verbose_name="Κόμβος Αναφοράς",)

    # formation where the unit hierarchically belongs to
    supervisor_unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.PROTECT, related_name="supervisor_unit_report", verbose_name="Προϊστάμενος Σχηματισμός",)

    # major formation where the unit hierachically belongs to
    supervisor_major_formation = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.PROTECT, related_name="supervisor_major_formation_report", verbose_name="Προϊστάμενος Μείζων Σχηματισμός",)

    # current state of the _report
    status = models.CharField(max_length=2, choices=State.choices, default=State.NEW, verbose_name="Κατάσταση",)

    # report submission date
    date_start = models.DateTimeField( blank=True, null=True, verbose_name="Ημερομηνία Καταχώρησης",)

    # report last modification date
    date_last_modified = models.DateTimeField( auto_now=True, verbose_name="Τελευταία Ενημέρωση",)

    # report resolution date
    date_end = models.DateTimeField( blank=True, null=True, verbose_name="Ημερομηνία Διεκπεραίωσης",)

    # rank of the report submitter
    submitter_rank = models.CharField( max_length = 10, choices = RANK_CHOICES, default = 'lxias', verbose_name = 'Βαθμός Καταχωρητή')

    # name of the report submitter
    submitter_name = models.CharField( max_length = 30, null=True, verbose_name = 'Όνομα Καταχωρητή')

    # user account of the submitter
    submitter_user = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL, related_name="submitter_user_report", verbose_name="Λογαριασμός Χρήστη Καταχωρητή",)

    # dispatcher assigned to resolve this report
    assigned_dispatcher = models.ForeignKey(CustomUser, limit_choices_to={'groups__name': "dispatchers"}, blank=True, null = True, on_delete=models.SET_NULL, related_name = "dispatcher_user_report", verbose_name="Διεκπεραιωτής Αναφοράς",)

    # steps to solve the report - provided by the failure's assigned dispatcher - optional
    solution = models.TextField(blank=True, verbose_name="Επίλυση", )

    # user-provided file referring to this report
    attached_file = models.FileField(blank=True, null=True, upload_to=upload_location, verbose_name="Επισυναπτόμενο Αρχείο", validators=[validate_file_extension], )

    # regular expression to validate the phone number provided by the submitter
    phone_regex = RegexValidator(regex=r"^\+?1?\d{7,15}$", message="Το τηλέφωνο επικοινωνίας πρέπει να είναι της μορφής 1234567890 με ή χωρίς εθνικό πρόθεμα", )
    
    # contact
    # primary phone
    primary_phone = models.CharField(verbose_name="Τηλέφωνο επικοινωνίας No.1", validators=[phone_regex], max_length=17, blank=True,)

    # secondary phone 
    secondary_phone = models.CharField(verbose_name="Τηλέφωνο επικοινωνίας No.2", validators=[phone_regex], max_length=17, blank=True,)

    # custom object manager
    objects = ReportManager()

    # using the python @property decorator, we can use is_modified both as a method and as a field
    @property
    def is_modified(self):
        if self.date_start != self.date_last_modified:
            return True
        return False

    # save the newly created report
    def save(self, *args, **kwargs):
        # if this report is being created right now, so this is the first time it is saved
        if self.pk is None:
            self.create_report_number()
            self.date_start = timezone.localtime(timezone.now())

        # capitalize report description and submitter name
        self.description = self.description.upper()
        self.submitter_name = self.submitter_name.upper()

        super(Report, self).save(*args, **kwargs)

    # custom delete method, to be able to first delete any provided attached files 
    def delete(self, *args, **kwargs):
        self.attached_file.delete()
        super(Report, self).delete(*args, **kwargs)

    # function that creates this report's number
    def create_report_number(self):
        if Report.objects.count() == 0:
            new_report_number_value = 0
        else:
            # get the most recent report's number
            last_report_number = Report.objects.all().aggregate(Max("number"))
            # extract the last 4 digits
            last_report_number_value = str(last_report_number["number__max"])[-4:]
            # add 1
            new_report_number_value = int(last_report_number_value) + 1

        # id convention -> 11 + 5-digit-formatted id
        id_string = "11" + format(new_report_number_value, "05d")
        self.number = id_string


    # returns True if the user making the request is this report's original submitter
    def submitted_by(self, user):
        return self.submitter_user == user

    # returns True if the user making the request is this report's assigned dispatcher
    def dispatched_by(self, user):
        return self.assigned_dispatcher == user

    # returns True if the user making the request has editing rights on this report
    def can_edit(self, user):
        # a report can be edited by
        if user.is_admin() or user.is_manager():
            return True
        
        elif user.is_ddb():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        elif user.is_dispatcher():
            if self.submitted_by(user) or self.dispatched_by(user):
                return True
            else:
                return False
            
        elif user.is_simple_user():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        else:
            return False

    # returns True if the user making the request has deleting rights on this report
    def can_delete(self, user):
        if user.is_admin() or user.is_manager():
            return True

        elif user.is_ddb():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        elif user.is_dispatcher():
            if self.submitted_by(user) or self.dispatched_by(user):
                return True
            elif self.means in user.means.all():
                return True
            else:
                return False
            
        elif user.is_simple_user():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        else:
            return False

    # returns True if the user making the request has completing rights on this report
    def can_complete(self, user):
        if (user.is_admin() or user.is_manager()) and self.status != State.CLOSED:
            return True

        elif user.is_ddb():
            if self.status != State.CLOSED:
                return True 
            else:
                return False
        
        elif user.is_dispatcher():
            if self.submitted_by(user) or self.dispatched_by(user):
                return True
            else:
                return False     

        elif user.is_simple_user():
            if self.submitted_by(user) and self.status != State.CLOSED:
                return True
            else:
                return False

        else:
            return False  

    def __str__(self):
        return "{0}-{1}".format(self.number, self.description)

    class Meta:
        verbose_name = "Αναφορά"
        verbose_name_plural = "Αναφορές"


