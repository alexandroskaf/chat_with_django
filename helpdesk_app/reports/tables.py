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

def get_reports_link(**kwargs):
    record = kwargs.get("record", None)
    return f"window.location.href='/reports/{record.id}';"


# bare minimum report table
class ReportTableBare(tables.Table):
    unit = tables.Column(verbose_name="Σχηματισμός (Μονάδα)")
    date_from = tables.Column(verbose_name="Από",empty_values=())
    means = tables.Column(verbose_name="Σύστημα",empty_values=())

    def render_date_from(self, record):
        t_temp = timezone.localtime(record.date_start)
        return format_html("{}",t_temp.strftime("%d/%m/%Y %H:%M"))

    class Meta:
        model = Report
        attrs = {"class": "table table-hover"}
        fields = ("number", "means", "unit", "supervisor_unit", "date_from",)
        sequence = ("number", "means", "unit", "supervisor_unit", "date_from",)


# report table for admins/manager
class ReportTableAssignCompleteEditDelete(ReportTableBare):
    assign_entry = tables.TemplateColumn(template_name="reports/assign_report_column.html", verbose_name="",)
    complete_entry = tables.TemplateColumn(template_name="reports/complete_report_column.html", verbose_name="",)
    edit_entry = tables.TemplateColumn(template_name="reports/edit_report_column.html", verbose_name="", )
    delete_entry = tables.TemplateColumn(template_name="reports/delete_report_column.html", verbose_name="",)

    class Meta(ReportTableBare.Meta):
        sequence = ReportTableBare.Meta.sequence + (
            "assign_entry",
            "complete_entry",
            "edit_entry", 
            "delete_entry",
            )
        row_attrs = {"class": status_color, 
        "onclick":get_reports_link
        }


# report table for dispatchers
class ReportTableCompleteEditDelete(ReportTableBare):
    complete_entry = tables.TemplateColumn(template_name="reports/complete_report_column.html", verbose_name="",)
    edit_entry = tables.TemplateColumn(template_name="reports/edit_report_column.html", verbose_name="", )
    delete_entry = tables.TemplateColumn(template_name="reports/delete_report_column.html", verbose_name="",)

    class Meta(ReportTableBare.Meta):
        sequence = ReportTableBare.Meta.sequence + (
            "complete_entry",
            "edit_entry", 
            "delete_entry",
            )
        row_attrs = {"class": status_color, 
        "onclick":get_reports_link
        }


# report table for ddb and simple users - for common UI for NEW and OPEN failures
class ReportTableCompleteEditDelete_DDB_SimpleUser(ReportTableBare):
    complete_entry = tables.TemplateColumn(template_name="reports/complete_report_column.html", verbose_name="",)
    edit_entry = tables.TemplateColumn(template_name="reports/edit_report_column.html", verbose_name="", )
    delete_entry = tables.TemplateColumn(template_name="reports/delete_report_column.html", verbose_name="",)

    class Meta(ReportTableBare.Meta):
        sequence = ReportTableBare.Meta.sequence + (
            "complete_entry",
            "edit_entry", 
            "delete_entry",
            )
        row_attrs = {"class": status_color_ddb_simpleuser, 
        "onclick":get_reports_link
        }


# report table to export - for everyone who has the right to view this
class ReportTablePrint(ReportTableBare):
    number = tables.Column(verbose_name="Α/Α",empty_values=())    

    class Meta:
        model = Report
        attrs = {"class": "table "} 
        exclude = (
            "means",
            "supervisor_major_formation",
        )
        fields = (
            "description",
        )
        sequence = (
            "number",
            "description",
            "unit",
            "supervisor_unit",
            "date_from",
        )
        orderable = False
