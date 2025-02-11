import json
from datetime import datetime
from django.utils.timezone import now

from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, Http404
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    update_session_auth_hash,
    authenticate,
    login as _login,
    logout as _logout,
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.template import loader
from django.contrib import messages
from django_tables2 import RequestConfig

import xlwt

from ..models import *
from .forms import *
from .tables import *
from ..models_managers import *
from .filters import *
from ..utils import *


@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def reports_all(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    if request.method == 'GET':
        # get all reports
        reports_tables = {}
        means_id = {}
        all_means = CommunicationMeans.objects.all()
        reports = Report.objects.get_for_user(user)

        reports_filtered = ReportFilter(
            request.GET, queryset=reports
        )



        def get_report_table_for_user(user):
            if user.is_admin() or user.is_manager():
                return ReportTableAssignCompleteEditDelete
            elif user.is_dispatcher():
                return ReportTableCompleteEditDelete
            elif user.is_ddb() or user.is_simple_user():
                return ReportTableCompleteEditDelete_DDB_SimpleUser


        table_for_user = get_report_table_for_user(user)
        for means in all_means:
            reports_filtered_by_means = reports_filtered.qs.filter(
                means=means
            )

            if reports_filtered_by_means.count() > 0:
                reports_tables[means.name] = table_for_user(
                    reports_filtered_by_means.order_by("-date_last_modified")
                )
                RequestConfig(request).configure(reports_tables[means.name])
                means_id[means.name] = means.id

        if request.method == "GET":
            print_form = PrintReportForm()

        context = {
            "filters": reports_filtered,
            "reports_tables": reports_tables,
            "means_id": means_id,
            "print_form": print_form,
        }
        if len(reports_tables) == 0:
            messages.warning(
                request, "Δεν υπάρχουν αποτελέσματα για αυτή την αναζήτηση.",
            )

        return render(request, "reports/reports.html", context,)

    elif request.method == "POST":
        user = get_object_or_404(CustomUser, id=request.user.id)
        form = CreateReportForm(request.POST, request.FILES, request=request)
        context = {
            "form": form, 
        }
        if form.is_valid():
            report = form.save(commit=False)
            report.supervisor_unit = report.unit.parent
            report.supervisor_major_formation = report.unit.major_formation
            report.save()
            messages.success(
                request,
                f"Η βλάβη υποβλήθηκε επιτυχώς με αριθμό {report.number}!",
            )            

            return redirect("reports_all")
        else:
            messages.warning(
                request,
                "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στην καταχώρηση! Προσπαθήστε ξανά.",
            )
            return render(request, "reports/new_report.html", context)

@require_http_methods(["GET"])
@login_required(login_url="login")
def report_new(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    form = CreateReportForm(request=request)
    
    return render(request, "reports/new_report.html", {"form": form})


@require_http_methods(["GET"])
@login_required(login_url="login")
def report_edit(request, report_id):
    user = get_object_or_404(CustomUser, id=request.user.id)
    report = get_object_or_404(Report, id=report_id)

    if report.can_edit(user):
        form = EditReportForm(instance=report, request=request)
        return render(request, "reports/edit_report.html", {"form": form})
    else:
        raise Http404()
    

@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def report_single(request, report_id):
    if request.method == "GET":
        user = get_object_or_404(CustomUser, id=request.user.id)

        try:
            report = Report.objects.filter(Report.objects.get_filter_for_user(user)).get(id=report_id)

            # when the report is viewed for the first time by an admin/manager/dispatcher, 
            # its state is updated from NEW to OPEN
            if not user.is_simple_user() and not user.is_ddb():
                if report.status == State.NEW:
                    report.status = State.OPEN
                    report.save()

            return render(request, "reports/view_report.html", {"report": report})
        except:
            raise Http404()

    elif request.method == "POST":
        user = get_object_or_404(CustomUser, id=request.user.id)
        report = get_object_or_404(Report, id=report_id)

        if report.can_edit(user):
            form = EditReportForm(
            request.POST, request.FILES, instance=report, request=request
            )

            if form.is_valid():
                report = form.save(commit=False)
                if report.status == State.CLOSED.value and report.date_end is None:
                    report.date_end = now()
                elif report.status == State.PROGRESS.value and report.date_end is not None:
                    report.date_end = None
                # if by editing the report, we set it in the OPEN state, remove the assigned_dispatcher, if there was one
                elif report.status == State.OPEN:
                    report.assigned_dispatcher = None
                # if by editing the report, we remove the assigned_dispatcher, if there was one, set its status to OPEN
                elif report.assigned_dispatcher == None:
                    report.status = State.OPEN
                report.save()

                # Mark has modified if the changes made by dispatcher
                if not user.is_simple_user() and form.has_changed:
                    report = get_object_or_404(Report, id=report_id)
                    report.date_last_modified = now()
                    report.save()
                    changed_fields = []

                messages.info(
                    request, f"Η Βλάβη με αριθμό {report.number} άλλαξε επιτυχώς!",
                )
                return redirect("report_single", report.id)
            else:
                messages.warning(
                    request,
                    "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στην επεξεργασία! Προσπαθήστε ξανά.",
                )
                return render(request, "reports/edit_report.html", {"form": form})
        
        # the user has no permission to edit this report
        else:
            raise Http404()


@require_http_methods(["POST"])
@login_required(login_url="login")
def report_delete(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    if report.can_delete(request.user):
        try:
            report.delete()
            messages.success(
                request, f"Η Αναφορά με αριθμό {report.number} διαγράφηκε επιτυχώς!",
            )
            return redirect("reports_all")
        except:
            messages.warning(
                request,
                "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στη διαγραφή! Προσπαθήστε ξανά.",
            )
            return redirect("report_single", report_id)
    else:
        raise Http404()


def group_required(*group_names):
   """Requires user membership in at least one of the groups passed in."""

   def in_groups(u):
       if u.is_authenticated:
           if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
               return True
       return False
   return user_passes_test(in_groups)
    
@require_http_methods(["POST"])
@login_required(login_url="login")
@group_required("admins", "managers")
def report_dispatcher(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if "dispatcher_form_select" not in request.POST:
        # remove assignment
        report.assigned_dispatcher = None
        report.status = State.OPEN
        report.save()

        messages.info(
            request, f"Η Αναφορά με αριθμό {report.number} είναι σε κατάσταση ΕΚΚΡΕΜΗΣ.",
        )
        return redirect("report_single", report.id)  

    else:
        # change assigned dispatcher
        assigned_dispatcher_id = request.POST.get("dispatcher_form_select")
        assigned_dispatcher = get_object_or_404(CustomUser, id=assigned_dispatcher_id)
        report.assigned_dispatcher = assigned_dispatcher
        report.status = State.PROGRESS
        report.save()

        messages.success(
            request, f"Η Αναφορά με αριθμό {report.number} ανατέθηκε επιτυχώς στον διεκπεραιωτή {str(assigned_dispatcher)}!",
        )
        return redirect("report_single", report.id)   


@require_http_methods(["POST"])
@login_required(login_url="login")
def report_complete(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    user = get_object_or_404(CustomUser, id=request.user.id)

    if report.can_complete(user):
        try:
            report.date_end = now()
            report.status = State.CLOSED
            report_solution = request.POST.get("report_solution")
            if report_solution:
                report.solution = report_solution
            else:
                report.solution = ""

            report.save()
            messages.success(
                request,
                f"Η αναφορά με αριθμό {report.number} διεκπεραιώθηκε επιτυχώς!"
            )
            return redirect("reports_all")
        except:
            messages.warning(
                request,
                "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στην διεκπεραίωση της αναφοράς! Προσπαθήστε ξανά.",
            )
            return redirect("report_single", report.id)
    else:
        raise Http404()


def get_reports_tables_json(user, tele_means, reports, date_from, date_to):
    tables = {}
    for means in tele_means:
        tables[means.name] = list()
        reports_filter_by_means = reports.filter(means=means).filter(
        Q(status=State.PROGRESS) | 
        Q(date_end__gte=date_from) & 
        Q(date_end__lte=date_to) 
        )

        if reports_filter_by_means.count() > 0:                
            for report in reports_filter_by_means:
                tables[means.name].append({
                    "number": report.number,
                    "unit": report.unit,
                    "description": report.description,
                    "supervisor_unit": report.supervisor_unit,
                    "date_start": report.date_start,
                })
    
    return tables


@require_http_methods(["GET"])
@login_required(login_url="login")
def reports_print(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    date_from = datetime.strptime(request.GET["date_from"], "%d/%m/%Y")
    date_to = datetime.strptime(request.GET["date_to"], "%d/%m/%Y")

    reports_tables = {}
    tele_means = CommunicationMeans.objects.all()
    reports = Report.objects.get_for_user(user).order_by("-date_last_modified")

    reports_tables = get_reports_tables_json(user, tele_means, reports, date_from, date_to)

    context = {
        "date_from": request.GET["date_from"],
        "date_to": request.GET["date_to"],
        "reports_tables": reports_tables,
    }
    
    return render(request, "reports/reports_print.html", context)


@require_http_methods(["GET",])
@login_required(login_url="login")
def reports_print_excel(request):
    user = get_object_or_404(CustomUser, id=request.user.id)

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = f'attachment; filename=REPORTS_{request.GET["date_from_excel"]}-{request.GET["date_to_excel"]}.xls'

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("ΑΝΑΦΟΡΕΣ")

    date_from = datetime.strptime(request.GET["date_from_excel"], "%d/%m/%Y")
    date_to = datetime.strptime(request.GET["date_to_excel"], "%d/%m/%Y")

    tele_means = CommunicationMeans.objects.all()
    reports = Report.objects.get_for_user(user).order_by("-date_last_modified")

    report_tables = get_reports_tables_json(user, tele_means, reports, date_from, date_to)

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    ws.write(0, 0, "ΓΕΝΙΚΟ ΕΠΙΤΕΛΕΙΟ ΣΤΡΑΤΟΥ", font_style)
    ws.write(1, 0, "487 ΤΑΓΜΑ ΔΙΑΒΙΒΑΣΕΩΝ", font_style)
    ws.write(2, 0, "ΚΕΝΤΡΟ ΕΠΙΚΟΙΝΩΝΙΩΝ", font_style)

    ws.write(4, 0, 'ΚΑΤΑΣΤΑΣΗ ΑΝΑΦΟΡΩΝ ΕΦΑΡΜΟΓΗΣ "ΚΔΕΣ-ΖΕΥΞΙΣ"', font_style)
    ws.write(5, 0, f'{request.GET["date_from_excel"]} - {request.GET["date_to_excel"]}', font_style)
    
    row_num = 8
    for name, table in report_tables.items():
        if table:
            row_num += 1

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            ws.write(row_num, 0, name, font_style)
            row_num += 1

            columns = ["Α/Α","ΠΕΡΙΓΡΑΦΗ", "ΜΟΝΑΔΑ (ΣΧΗΜΑΤΙΣΜΟΣ)", "ΑΠΟ"]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            font_style = xlwt.XFStyle()
            for report in table:
                row_num += 1

                ws.write(row_num, 0, str(report["number"]), font_style)
                ws.write(row_num, 1, str(report["description"]), font_style)
                ws.write(row_num, 2, f"{str(report['unit'])} ({str(report['supervisor_unit'])})", font_style)
                ws.write(row_num, 3, str(report["date_start"]), font_style)

            row_num += 1

    wb.save(response)

    return response   

