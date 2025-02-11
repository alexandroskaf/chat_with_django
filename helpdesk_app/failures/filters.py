import django_filters

from django import forms
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

from ..models import *
from datetime import date, datetime, timedelta


class FailureFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(FailureFilter, self).__init__(*args, **kwargs)

        today_morning = datetime.now().replace(hour=7, minute=00, second=00)
        yesterday_morning = today_morning - timedelta(days=1)
        self.form.fields["date_end"].initial = slice(yesterday_morning,today_morning)

    failure_type = django_filters.ModelMultipleChoiceFilter(
        queryset=FailureType.objects.all(),
    )
    status = django_filters.MultipleChoiceFilter(choices=[
                (State.NEW.value, State.NEW.label),
                (State.OPEN.value, State.OPEN.label),
                (State.PROGRESS.value, State.PROGRESS.label),
                (State.CLOSED.value, State.CLOSED.label),
            ],)
    unit = django_filters.ModelMultipleChoiceFilter(queryset=Unit.objects.all())

    means = django_filters.ModelMultipleChoiceFilter(
        queryset=CommunicationMeans.objects.all()
    )
    date_start = django_filters.DateTimeFromToRangeFilter()
    date_end = django_filters.DateTimeFromToRangeFilter(method='date_end_custom')

    def date_end_custom(self, queryset,name, value):
        if value.start is not None and value.stop is not None: 
            value.start.replace(hour=7)
            value.stop.replace(hour=7)
            return queryset.filter(Q(status=State.PROGRESS) | Q(date_end__gte=value.start) & Q(date_end__lte=value.stop) )
        elif value.start is None:
            value.stop.replace(hour=7)
            return queryset.filter(Q(date_end__lte=value.stop) | Q(status=State.PROGRESS))
        elif value.stop is None:
            value.start.replace(hour=7)
            return queryset.filter(Q(date_end__gte=value.start) | Q(status=State.PROGRESS))


    class Meta:
        model = Failure
        fields = {"description": ["icontains"]}
