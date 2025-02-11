from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from ..models import *
from datetime import date, datetime, timedelta
from django.utils import timezone
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
from ..rank_choices import *
from django.db.models import Q


#form to create a new report
class CreateReportForm(forms.ModelForm):
    def clean(self):
        user = self.request.user
        cleaned_data = super(CreateReportForm, self).clean()

        # Check end date
        if user.is_dispatcher() or user.is_simple_user():
            date_start = date.today()
            date_end = cleaned_data.get("date_end")
            if date_end is not None:
                if date_end < date_start:
                    raise forms.ValidationError(
                        "Η ημερομηνία διεκπεραίωσης δεν μπορεί να είναι προγενέστερη της σημερινής"
                    )

        # Check state
        if cleaned_data.get("status") is None:
            cleaned_data["status"] = State.NEW

        if cleaned_data.get("submitter_user") is None:
            cleaned_data["submitter_user"] = self.request.user

        # Check description
        if cleaned_data.get("description") == "":
            cleaned_data["description"] = "---"

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(CreateReportForm, self).__init__(*args, **kwargs)

        user = self.request.user

        self.fields["status"].initial = State.NEW
        self.fields["status"].disabled = True

        self.fields["submitter_user"].initial = user
        self.fields["submitter_user"].disabled = True


        self.fields["unit"] = forms.ModelChoiceField(
          queryset = Unit.objects.for_user(user),
          initial = user.unit,
        )


        self.fields["submitter_rank"] = forms.ChoiceField(
            label=Report._meta.get_field('submitter_rank').verbose_name,
            choices = RANK_CHOICES,
            initial = 'lxias',
            widget=forms.Select(attrs={"class": "form-control form-control-section"}),
        )        


        self.fields["primary_phone"] = forms.CharField(
            required=True,
            label=Report._meta.get_field('primary_phone').verbose_name,
            initial=user.phone,
            widget=forms.TextInput(
                attrs={"class": "form-control form-control-section",
                       "placeholder": "ΕΨΑΔ Ή ΕΞΩΤΕΡΙΚΉ",
                }
            ),
        )

        self.fields["secondary_phone"] = forms.CharField(
            required=False,
            label=Report._meta.get_field('secondary_phone').verbose_name,
            initial=user.phone,
            widget=forms.TextInput(
                attrs={"class": "form-control form-control-section",
                       "placeholder": "ΕΨΑΔ Ή ΕΞΩΤΕΡΙΚΉ",
                }
            ),
        )

        del self.fields["date_end"]


    class Meta:
        model = Report
        exclude = ["number", "assigned_dispatcher"]
        help_texts = {"description": "Δώστε την περιγραφή του Αναφοράς. Μέχρι 200 κεφαλαίους χαρακτήρες.",}
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-section",
                    "rows": 3,
                    "placeholder": "---",
                }
            ),
            "submitter_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-section",
                    "placeholder": "---",
                }
            ),
            "submitter_rank": forms.Select(attrs={"class": "form-control form-control-section"}),
            "unit": forms.Select(attrs={"class": "form-control form-control-section"}),
            "means": forms.Select(attrs={"class": "form-control form-control-section"}),
            "status": forms.Select(attrs={"class": "form-control form-control-section"}),
            "attached_file": forms.FileInput(attrs={"class": "form-control-file"}),
        }


# #form to edit a report
class EditReportForm(forms.ModelForm):
    def clean(self):
        user = self.request.user
        cleaned_data = super(EditReportForm, self).clean()

        # Check end date
        date_start = timezone.localtime(self.instance.date_start)
        date_end = cleaned_data.get("date_end")
        if date_end is not None:
            if date_end < date_start:
                raise forms.ValidationError(
                    "Η ημερομηνία διεκπεραίωσης δεν μπορεί να είναι προγενέστερη της καταχώρησης"
                )

        return cleaned_data
       

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(EditReportForm, self).__init__(*args, **kwargs)

        user = self.request.user

        self.fields["status"] = forms.ChoiceField(
            choices=[
                (State.NEW.value, State.NEW.label),
                (State.OPEN.value, State.OPEN.label),
                (State.PROGRESS.value, State.PROGRESS.label),
                (State.CLOSED.value, State.CLOSED.label),
            ],
            label="Κατάσταση",
        )

        self.fields["unit"].initial = self.instance.unit

        
        self.fields["primary_phone"] = forms.CharField(
            required=True,
            label=Report._meta.get_field('primary_phone').verbose_name,
            initial=self.instance.primary_phone,
            widget=forms.TextInput(
                attrs={"class": "form-control form-control-section",
                       "placeholder": "ΕΨΑΔ Ή ΕΞΩΤΕΡΙΚΉ",
                }
            ),
        )

        self.fields["secondary_phone"] = forms.CharField(
            required=False,
            label=Report._meta.get_field('secondary_phone').verbose_name,
            initial=self.instance.secondary_phone,
            widget=forms.TextInput(
                attrs={"class": "form-control form-control-section",
                       "placeholder": "ΕΨΑΔ Ή ΕΞΩΤΕΡΙΚΉ",
                }
            ),
        )

        self.fields["assigned_dispatcher"] = forms.ModelChoiceField(
            required=False,
            queryset=CustomUser.objects.filter(Q(means__in = [self.instance.means])),        
            initial=self.instance.assigned_dispatcher,            
            label=Report._meta.get_field('assigned_dispatcher').verbose_name,
        )

        self.fields["number"].disabled = True
        self.fields["means"].disabled = True

        #self.fields.pop("unit")
        self.fields.pop("supervisor_unit")
        self.fields.pop("submitter_name")
        self.fields.pop("submitter_rank")
        self.fields.pop("submitter_user")
        self.fields.pop("date_start")
        self.fields.pop("date_end")

        if user.is_simple_user():
            self.fields.pop("status")

    class Meta:
        model = Report
        exclude = []
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-section",
                    "rows": 3,
                }
            ),
            "solution": forms.Textarea(
                attrs={
                    "class": "form-control form-control-section",
                    "rows": 3,
                }
            ),
            "means": forms.Select(attrs={"class": "form-control form-control-section"}),
            "status": forms.Select(attrs={"class": "form-control form-control-section"}),
            "unit": forms.Select(attrs={"class": "form-control form-control-section"}),
        }


# form to enter dates for report export
class PrintReportForm(forms.Form):
    date_from = forms.DateTimeField(label="Απο")
    date_to = forms.DateTimeField(label="Eως")

    def clean(self):
        cleaned_data = super(PrintReportForm, self).clean()

        if cleaned_data.get("date_to") < cleaned_data.get("date_from"):
            raise forms.ValidationError(
                "Η ημερομηνία δεν ειναι σωστή!"
            )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(PrintReportForm, self).__init__(*args, **kwargs)
        today_morning = datetime.now()
        today_morning = today_morning.replace(hour=7, minute=00, second=00)
        yesterday_morning = today_morning -timedelta(days=1)

        self.fields["date_from"].initial = yesterday_morning
        self.fields["date_to"].initial = today_morning


# admin form to add a new Report
class ReportAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ReportAdminForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ReportAdminForm, self).__init__(*args, **kwargs)
        self.fields["number"].disabled = True

    class Meta:
        model = Report
        fields = "__all__"

