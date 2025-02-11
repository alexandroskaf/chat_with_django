from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from .models import *
from datetime import date, datetime, timedelta
from django.utils import timezone
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
from .rank_choices import *
from django.db.models import Q


#form to input a new Unit
class UnitForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(UnitForm, self).clean()
        is_formation = cleaned_data.get("is_formation", None)
        is_major = cleaned_data.get("is_major", None)
        if is_major and is_formation == False:
            raise forms.ValidationError(
                "Μείζων μπορεί να είναι μόνο Σχημάτισμος. \n Παρακαλώ επιλέξτε το πέδιο Σχηματισμού."
            )

    class Meta:
        model = Unit
        fields = "__all__"


#form to edit the info of a User
class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)

        # check user group
        is_admin = self.request.user.is_admin()

        # remove unused fields
        del self.fields["password"]

        # set fields to disable
        self.fields["last_login"].disabled = True
        if not is_admin:
            self.fields["unit"].disabled = True

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ["username", "first_name", "last_name", "unit", "phone", "last_login"]


#form to change a password
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(user, *args, **kwargs)
        
        # hide helptext (PasswordChangeForm translation failure)
        for fieldname in ['new_password1', 'new_password2']:
            self.fields[fieldname].help_text = None


#form to add a new Network Speed
class NetworkSpeedForm(forms.ModelForm):
    class Meta:
        model = NetworkSpeed
        fields = "__all__"


#form to add a new routing
class RoutingForm(forms.ModelForm):
    class Meta:
        model = Routing
        fields = "__all__"


#form to add a new Pyrseia Server
class PyrseiaServerForm(forms.ModelForm):
    class Meta:
        model = PyrseiaServer
        fields = "__all__"


#form to add a new Broadband Tranceiver
class BroadbandTransceiverForm(forms.ModelForm):
    class Meta:
        model = BroadbandTransceiver
        fields = "__all__"


#form to add a new Satellite Node
class SatelliteNodeForm(forms.ModelForm):
    class Meta:
        model = SatelliteNode
        fields = "__all__"


#form to add a new Hermes Node
class HermesNodeForm(forms.ModelForm):
    class Meta:
        model = HermesNode
        fields = "__all__"


#form to add a new Hermes Connection
class HermesConnectionForm(forms.ModelForm):
    class Meta:
        model = HermesConnection
        fields = "__all__"


#form to add a new Harp Correspondent
class HarpCorrespondentForm(forms.ModelForm):
    class Meta:
        model = HarpCorrespondent
        fields = "__all__"


# #form to input a comment
# class CommentForm(forms.ModelForm):
#     def clean(self):
#         current_user = self.request.user
#         cleaned_data = super(CommentForm, self).clean()

#         return cleaned_data

#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop("request", None)
#         self.report = kwargs.pop("report")
#         super(CommentForm, self).__init__(*args, **kwargs)

#         current_user = self.request.user

#         self.fields["report"].initial = self.report
#         self.fields["report"].disabled = True

#     class Meta:
#         model = Comment
#         # fields = "__all__"
#         exclude = ["author", "approved_comment"]
#         widgets = {
#             "text": forms.Textarea(
#                 attrs={
#                     "class": "form-control form-control-section",
#                     "rows": 4,
#                     "placeholder": "Π.Χ ΜE THN ΕΠΑΝΝΕΚΙΝΙΣΗ ΤΟΥ ΣΥΣΤΗΜΑΤΟΣ Η ΒΛΑΒΗ ΕΠΙΔΙΟΡΘΩΘΗΚΕ",
#                 }
#             ),
#         }


# # form to add a new FailureType 
class FailureTypeAdminForm(forms.ModelForm):
    class Meta:
        model = FailureType
        fields = "__all__"


#form to add a new CommunicationMeans
class CommunicationMeansAdminForm(forms.ModelForm):
    class Meta:
        model = CommunicationMeans
        fields = "__all__"


#form to add a new digital connection
class DigConnectionAdminForm(forms.ModelForm):
    class Meta:
        model = DigConnection
        fields = "__all__"
