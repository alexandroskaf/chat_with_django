from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .reports.forms import *
from .failures.forms import *
from .forms import *
from .models import *

admin.site.site_header = "Διαχείριση ΚΔΕΣ - Ζεύξις"
admin.site.index_title = "Διαχειριστική διεπαφή"
admin.site.site_title = "ΚΔΕΣ - Ζεύξις"

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_max_show_all = 400
    list_display = ["name", "location", "parent", "major_formation", "is_formation", "is_major"]
    search_fields = ['name']
    ordering = ["name"]
    form = UnitForm

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields["last_login"].disabled = True
        self.fields["date_joined"].disabled = True

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "unit", "phone", "last_login", "password_has_changed"]
    search_fields = ["username", "unit__name"]
    model = CustomUser
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            ("Πρόσθετες Πληροφορίες"),
            {"fields": ("unit", "phone", "means", "password_has_changed"),},
        ),
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            ("Πρόσθετες Πληροφορίες"),
            {"fields": ("unit", "phone", "means", "password_has_changed"),},
        ),
    )
    form = CustomUserChangeForm

@admin.register(NetworkSpeed)
class NetworkSpeedAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    form = NetworkSpeedForm

@admin.register(Routing)
class RoutingAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    form = RoutingForm

@admin.register(PyrseiaServer)
class PyrseiaServerAdmin(admin.ModelAdmin):
    list_display = ["name", "unit", "formation", "domain", "exchange", "esxi", "default_gateway"]
    search_fields = ["formation__name", "domain", "exchange", "esxi", "default_gateway" ]
    form =  PyrseiaServerForm

@admin.register(BroadbandTransceiver)
class BroadbandTransceiverAdmin(admin.ModelAdmin):
    list_display = [ "coupling", "hostname", "coupling_code", "model", "formation", "unit_from", "unit_to"]
    search_fields = ["coupling", "hostname", "coupling_code", "model", "formation__name", "unit_from__name", "unit_to__name"]
    form =  BroadbandTransceiverForm

@admin.register(SatelliteNode)
class SatelliteNodeAdmin(admin.ModelAdmin):
    list_display = ["name", "unit", "formation"]
    search_fields = ["name", "formation__name"]
    form =  SatelliteNodeForm

@admin.register(HermesNode)
class HermesNodeAdmin(admin.ModelAdmin):
    list_display = ["number", "location", "node_type", "unit", "formation"]
    search_fields = ["number", "location", "node_type", "unit__name", "formation__name"]
    form =  HermesNodeForm

@admin.register(HermesConnection)
class HermesConnectionAdmin(admin.ModelAdmin):
    list_display = ["number", "node_from", "node_to"]
    search_fields = ["number", "node_from__location", "node_to__location"]
    form =  HermesConnectionForm

@admin.register(HarpCorrespondent)
class HarpCorrespondentAdmin(admin.ModelAdmin):
    list_max_show_all = 600    
    list_display = ["correspondent", "formation", "unit", "number", "device_type", "is_track_harp"]
    search_fields = ["correspondent", "formation__name", "unit__name", "number", "device_type"]
    form =  HarpCorrespondentForm

# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Comment._meta.get_fields()]
#     search_fields =["report__number"]

@admin.register(Failure)
class FailureAdmin(admin.ModelAdmin):
    list_display = [
        "number",
        "failure_type",
        "means",
        "status",
        "description",
        "unit",
        "date_start",
        "date_last_modified",
        "date_end",
    ]
    search_fields =["number", "unit__name", "supervisor_unit__name", "supervisor_major_formation__name"]
    form = FailureAdminForm

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "number",
        "status",
        "description",
        "unit",
        "date_start",
        "date_last_modified",
        "date_end",
    ]
    search_fields =["number", "unit__name", "supervisor_unit__name"]
    form = ReportAdminForm

@admin.register(FailureType)
class FailureTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "means"]
    ordering = ["means"]
    search_fields =["name", "means__name"]
    form = FailureTypeAdminForm

@admin.register(CommunicationMeans)
class CommunicationMeansAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    form = CommunicationMeansAdminForm

@admin.register(DigConnection)
class DigConnectionAdmin(admin.ModelAdmin):
    list_max_show_all = 1300   
    list_display = ["number", "name", "formation_from", "unit_from", "formation_to", "unit_to", "means", "route", "speed", "external"]
    search_fields = ["number", "unit_from__name", "unit_to__name", "means__name", "route__name", "speed__name", "external"]
    form = DigConnectionAdminForm
