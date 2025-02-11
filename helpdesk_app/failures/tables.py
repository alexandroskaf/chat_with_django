import django_tables2 as tables
from django.utils.html import format_html
from django.utils import formats, timezone
from ..models import *

from django_tables2.utils import A 


def status_color(**kwargs):
    report = kwargs.get("record", None)
    if report.status == State.CLOSED:
        return ""
    elif report.status == State.OPEN:
        return "open-failure-table-row"
    elif report.status == State.PROGRESS:
        return "progress-failure-table-row"
    elif report.status == State.NEW:
        return "new-failure-table-row"
    else:
        return ""

def status_color_ddb_simpleuser(**kwargs):
    report = kwargs.get("record", None)
    if report.status == State.CLOSED:
        return ""
    elif report.status == State.OPEN or report.status == State.NEW:
        return "open-failure-table-row"
    elif report.status == State.PROGRESS:
        return "progress-failure-table-row"
    else:
        return ""

def get_failures_link(**kwargs):
    record = kwargs.get("record", None)
    return f"window.location.href='/failures/{record.id}';"


# bare minimum failure table
class FailureTableBare(tables.Table):
    unit = tables.Column(verbose_name="Σχηματισμός (Μονάδα)")
    date_from = tables.Column(verbose_name="Από",empty_values=())
    means = tables.Column(verbose_name="Σύστημα",empty_values=())

    def render_date_from(self, record):
        t_temp = timezone.localtime(record.date_start)
        return format_html("{}",t_temp.strftime("%d/%m/%Y %H:%M"))

    class Meta:
        model = Failure
        attrs = {"class": "table table-hover"}
        fields = ("number", "means", "failure_type", "unit", "supervisor_unit", "date_from",)
        sequence = ("number", "means", "failure_type", "unit", "supervisor_unit", "date_from",)


# failure table for admins/manager
class FailureTableAssignCompleteEditDelete(FailureTableBare):
    assign_entry = tables.TemplateColumn(template_name="failures/assign_failure_column.html", verbose_name="",)
    complete_entry = tables.TemplateColumn(template_name="failures/complete_failure_column.html", verbose_name="",)
    edit_entry = tables.TemplateColumn(template_name="failures/edit_failure_column.html", verbose_name="", )
    delete_entry = tables.TemplateColumn(template_name="failures/delete_failure_column.html", verbose_name="",)

    class Meta(FailureTableBare.Meta):
        sequence = FailureTableBare.Meta.sequence + (
            "assign_entry",
            "complete_entry",
            "edit_entry", 
            "delete_entry",
            )
        row_attrs = {"class": status_color, 
        "onclick":get_failures_link
        }


# failure table for dispatchers
class FailureTableCompleteEditDelete(FailureTableBare):
    complete_entry = tables.TemplateColumn(template_name="failures/complete_failure_column.html", verbose_name="",)
    edit_entry = tables.TemplateColumn(template_name="failures/edit_failure_column.html", verbose_name="", )
    delete_entry = tables.TemplateColumn(template_name="failures/delete_failure_column.html", verbose_name="",)

    class Meta(FailureTableBare.Meta):
        sequence = FailureTableBare.Meta.sequence + (
            "complete_entry",
            "edit_entry", 
            "delete_entry",
            )
        row_attrs = {"class": status_color, 
        "onclick":get_failures_link
        }


# failure table for ddb and simple users - for common UI for NEW and OPEN failures
class FailureTableCompleteEditDelete_DDB_SimpleUser(FailureTableBare):
    complete_entry = tables.TemplateColumn(template_name="failures/complete_failure_column.html", verbose_name="",)
    edit_entry = tables.TemplateColumn(template_name="failures/edit_failure_column.html", verbose_name="", )
    delete_entry = tables.TemplateColumn(template_name="failures/delete_failure_column.html", verbose_name="",)

    class Meta(FailureTableBare.Meta):
        sequence = FailureTableBare.Meta.sequence + (
            "complete_entry",
            "edit_entry", 
            "delete_entry",
            )
        row_attrs = {"class": status_color_ddb_simpleuser, 
        "onclick":get_failures_link
        }


# failure table to export - for everyone who has the right to view this
class FailureTablePrint(FailureTableBare):
    number = tables.Column(verbose_name="Α/Α",empty_values=())
    related_dig_connection = tables.Column(verbose_name="ΑΡΙΘΜΟΣ ΚΥΚΛΩΜΑΤΟΣ",empty_values=())
    related_pyrseia_server = tables.Column(verbose_name="ΕΞΥΠΗΡΕΤΗΤΗΣ",empty_values=())
    related_harp_correspondent = tables.Column(verbose_name="ΑΝΤΑΠΟΚΡΙΤΗΣ",empty_values=())
    related_satellite_node = tables.Column(verbose_name="ΚΟΜΒΟΣ",empty_values=())
    related_broadband_transceiver = tables.Column(verbose_name="ΠΟΜΠΟΔΕΚΤΗΣ",empty_values=())
    related_hermes_node = tables.Column(verbose_name="ΚΟΜΒΟΣ",empty_values=())
    related_hermes_connection = tables.Column(verbose_name="ΖΕΥΞΗ",empty_values=())
    failure_type = tables.Column(verbose_name="ΤΥΠΟΣ ΒΛΑΒΗΣ",empty_values=())
    date_from = tables.Column(verbose_name="ΑΠΟ",empty_values=())
    unit = tables.Column(verbose_name="ΑΠΟ",empty_values=())
    # comments = tables.Column(accessor = "comment.text",verbose_name="Ενέργειες",empty_values=())

    def render_unit(self, record):
        failure = Failure.objects.get(pk=record.id)
        return format_html("{}({})", failure.unit, failure.supervisor_unit)

    def render_related_dig_connection(self, record):
        failure = Failure.objects.get(pk=record.id)
        if(failure.means.name in ["ΔΙΔΕΣ", "ΕΨΑΔ-ΑΤΚ"] ):
            if failure.related_dig_connection is None:
                return format_html(" ")
            else:
                return format_html("DIG {} {}",failure.related_dig_connection.number, failure.related_dig_connection.name)
        else:
            return format_html(" ")

    def render_related_server(self, record):
        failure = Failure.objects.get(pk=record.id)
        if failure.means.name == "ΠΥΡΣΕΙΑ":
            if failure.related_pyrseia_server is None:
                return format_html(" ")
            else:
                return format_html("{}",str(failure.related_pyrseia_server.name))
        else:
            return format_html(" ")

    def render_related_harp_correspondent(self, record):
        failure = Failure.objects.get(pk=record.id)
        if failure.means.name == "HARP":
            if failure.related_harp_correspondent is None:
                return format_html(" ")
            else:
                return format_html("{}",str(failure.related_harp_correspondent.correspondent))
        else:
            return format_html(" ")

    def render_related_satellite_node(self, record):
        failure = Failure.objects.get(pk=record.id)
        if failure.means.name == "ΔΟΡΥΦΟΡΙΚΑ":
            if failure.related_satellite_node is None:
                return format_html(" ")
            else:
                return format_html("{}",str(failure.related_satellite_node.name))
        else:
            return format_html(" ")

    def render_related_hermes_node(self, record):
        failure = Failure.objects.get(pk=record.id)
        if failure.means.name == "ΕΡΜΗΣ":
            if not failure.related_hermes_node is None:
                return format_html("{}",str(failure.related_hermes_node.number))
            else:
                return format_html(" ")

    def render_related_hermes_connection(self, record):
        failure = Failure.objects.get(pk=record.id)
        if failure.means.name == "ΕΡΜΗΣ":
            if not failure.related_hermes_connection is None:
                return format_html("{}",str(failure.related_hermes_connection.number))
            else:
                return format_html(" ")


    # def render_comments(self, record):
    #     comment = Comment.objects.get_last_for_report(record.id)
    #     if comment is None:
    #         return format_html(" --- ")
    #     else:
    #         return format_html("{}",str(comment))

    class Meta:
        model = Failure
        attrs = {"class": "table "} 
        exclude = (
            "means",
            "supervisor_major_formation",
            "supervisor_unit",
        )
        fields = (
            "description",
            "failure_type"
        )
        sequence = (
            "number",
            "related_dig_connection",
            "related_pyrseia_server",
            "related_harp_correspondent",
            "related_satellite_node",
            "related_hermes_node",
            "related_hermes_connection",
            "failure_type",
            "description",
            "unit",
            "date_from",
        )
        orderable = False
