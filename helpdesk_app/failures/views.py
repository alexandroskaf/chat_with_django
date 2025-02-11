from json import dumps
from datetime import datetime
from django.utils.timezone import now

from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, Http404
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import (
    update_session_auth_hash,
    authenticate,
    login as _login,
    logout as _logout,
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
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
def failures_all(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    if request.method == 'GET':
        # get all failures
        failures_tables = {}
        means_id = {}
        all_means = CommunicationMeans.objects.all()
        failures = Failure.objects.get_for_user(user)

        failures_filtered = FailureFilter(
            request.GET, queryset=failures
        )


        def get_failure_table_for_user(user):
            if user.is_admin() or user.is_manager():
                return FailureTableAssignCompleteEditDelete
            elif user.is_dispatcher():
                return FailureTableCompleteEditDelete
            elif user.is_ddb() or user.is_simple_user():
                return FailureTableCompleteEditDelete_DDB_SimpleUser


        table_for_user = get_failure_table_for_user(user)
        for means in all_means:
            failures_filtered_by_means = failures_filtered.qs.filter(
                means=means
            )

            if failures_filtered_by_means.count() > 0:
                failures_tables[means.name] = table_for_user(
                    failures_filtered_by_means.order_by("-date_last_modified")
                )
                RequestConfig(request).configure(failures_tables[means.name])
                means_id[means.name] = means.id

        if request.method == "GET":
            print_form = PrintFailureForm()

        context = {
            "filters": failures_filtered,
            "failures_tables": failures_tables,
            "means_id": means_id,
            "print_form": print_form,
        }
        if len(failures_tables) == 0:
            messages.warning(
                request, "Δεν υπάρχουν αποτελέσματα για αυτή την αναζήτηση.",
            )

        return render(request, "failures/failures.html", context,)

    elif request.method == "POST":
        print(dict(request.POST.items()))
        user = get_object_or_404(CustomUser, id=request.user.id)
        failure_types = FailureType.objects.all()
        form = CreateFailureForm(request.POST, request.FILES, request=request)
        context = {
            "form": form, 
            "failure_types": failure_types
        }
        if form.is_valid():
            failure = form.save(commit=False)
            failure.supervisor_unit = failure.unit.parent
            failure.supervisor_major_formation = failure.unit.major_formation
            failure.save()
            if failure.means.name == "ΕΥΡΥΖΩΝΙΚΟ":
                form.save_m2m()
            messages.success(
                request,
                f"Η βλάβη υποβλήθηκε επιτυχώς με αριθμό {failure.number}!",
            )            

            return redirect("failures_all")
        else:
            print(str(request.POST.get("related_hermes_connection")))
            print(form.errors)
            messages.warning(
                request,
                "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στην καταχώρηση! Προσπαθήστε ξανά.",
            )
            return render(request, "failures/new_failure.html", context)

@require_http_methods(["GET"])
@login_required(login_url="login")
def failure_new(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    if request.method == "GET":
        form = CreateFailureForm(request=request)
        context = {
            "form": form, 
        }
        return render(request, "failures/new_failure.html", context)


@require_http_methods(["GET"])
@login_required(login_url="login")
def failure_edit(request, failure_id):
    user = get_object_or_404(CustomUser, id=request.user.id)
    failure = get_object_or_404(Failure, id=failure_id)
    # comments = Comment.objects.for_report(failure)

    if failure.can_edit(user):
        form = EditFailureForm(instance=failure, request=request)
        context = {
            # "comments": comments,
            "form": form,
        }
        return render(request, "failures/edit_failure.html", context)
    else:
        raise Http404()
    

@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def failure_single(request, failure_id):

    # comments = Comment.objects.for_report(failure)

    if request.method == "GET":
        user = get_object_or_404(CustomUser, id=request.user.id)
        # failure = get_object_or_404(Failure, id=failure_id)

        # check if the user can view the requested failure
        try:
            failure = Failure.objects.filter(Failure.objects.get_filter_for_user(user)).get(id=failure_id)

            # when the failure is viewed for the first time by an admin/manager/dispatcher, 
            # its state is updated from NEW to OPEN
            if not user.is_simple_user() and not user.is_ddb():
                if failure.status == State.NEW:
                    failure.status = State.OPEN
                    failure.save()

            return render(request, "failures/view_failure.html", {"failure": failure})
        except:
            raise Http404()
            # return render(request, "failures/view_failure.html", {"failure": failure})

    elif request.method == "POST":
        user = get_object_or_404(CustomUser, id=request.user.id)
        failure = get_object_or_404(Failure, id=failure_id)

        if failure.can_edit(user):
            form = EditFailureForm(
            request.POST, request.FILES, instance=failure, request=request
            )
            context = {
                # "comments": comments,
                "form": form,
            }

            if form.is_valid():
                failure = form.save(commit=False)
                if failure.status == State.CLOSED.value and failure.date_end is None:
                    failure.date_end = now()
                elif failure.status == State.PROGRESS.value and failure.date_end is not None:
                    failure.date_end = None
                # if by editing the failure, we set it in the OPEN state, remove the assigned_dispatcher, if there was one
                elif failure.status == State.OPEN:
                    failure.assigned_dispatcher = None
                # if by editing the failure, we remove the assigned_dispatcher, if there was one, set its status to OPEN
                elif failure.assigned_dispatcher == None:
                    failure.status = State.OPEN
                failure.save()
                
                # FIXME - delete directory if the attached file is removed
                if failure.attached_file is None:
                    if os.path.isdir(settings.MEDIA_ROOT + f"failures/failure_{failure.number}/"):
                        os.rmdir(settings.MEDIA_ROOT + f"failures/failure_{failure.number}/")

                # Mark has modified if the changes made by dispatcher
                if not user.is_simple_user() and form.has_changed:
                    failure = get_object_or_404(Failure, id=failure_id)
                    failure.date_last_modified = now()
                    failure.save()
                    changed_fields = []
                    # comment for every changed field
                    # for field_name in form.changed_data:
                    #     changed_fields.append(
                    #         Failure._meta.get_field(field_name).verbose_name
                    #     )
                    # if len(changed_fields) > 0:
                    #     new_comment = Comment(
                    #         report=report,
                    #         author=user,
                    #         text="Τροποποιήθηκε το πεδίο: %s" % ", ".join(changed_fields),
                    #     )
                    #     new_comment.save()

                if failure.means.name == "ΕΥΡΥΖΩΝΙΚΟ":
                    form.save_m2m()

                messages.info(
                    request, f"Η Βλάβη με αριθμό {failure.number} άλλαξε επιτυχώς!",
                )
                return redirect("failure_single", failure.id)
            else:
                print(form.errors)
                messages.warning(
                    request,
                    "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στην καταχώρηση! Προσπαθήστε ξανά.",
                )
                return render(request, "failures/edit_failure.html", context)
        
        # the user has no permission to edit this failure
        else:
            raise Http404()


@require_http_methods(["POST"])
@login_required(login_url="login")
def failure_delete(request, failure_id):
    # delete specified failure
    failure = get_object_or_404(Failure, id=failure_id)
    
    if failure.can_delete(request.user):
        try:
            failure.delete()
            messages.success(
                request, f"Η Βλάβη με αριθμό {failure.number} διαγράφηκε επιτυχώς!",
            )
            return redirect("failures_all")
        except:
            messages.warning(
                request,
                "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στην διαγραφή! Προσπαθήστε ξανά.",
            )
            return redirect("failure_single", failure_id)
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
def failure_dispatcher(request, failure_id):
    failure = get_object_or_404(Failure, id=failure_id)

    if "dispatcher_form_select" not in request.POST:
        # remove assignment
        failure.assigned_dispatcher = None
        failure.status = State.OPEN
        failure.save()

        messages.info(
            request, f"Η Βλάβη με αριθμό {failure.number} είναι σε κατάσταση ΕΚΚΡΕΜΗΣ.",
        )
        return redirect("failure_single", failure.id)  

    else:
        # change assigned dispatcher
        assigned_dispatcher_id = request.POST.get("dispatcher_form_select")
        assigned_dispatcher = get_object_or_404(CustomUser, id=assigned_dispatcher_id)
        failure.assigned_dispatcher = assigned_dispatcher
        if failure.status != State.CLOSED:
            failure.status = State.PROGRESS
        failure.save()

        messages.success(
            request, f"Η Βλάβη με αριθμό {failure.number} ανατέθηκε επιτυχώς στον διεκπεραιωτή {str(assigned_dispatcher)}!",
        )
        return redirect("failure_single", failure.id)   


@require_http_methods(["POST"])
@login_required(login_url="login")
def failure_complete(request, failure_id):
    failure = get_object_or_404(Failure, id=failure_id)
    user = get_object_or_404(CustomUser, id=request.user.id)

    if failure.can_complete(user):
        try:
            failure.date_end = now()
            failure_solution = request.POST.get("failure_solution")
            if failure_solution:
                failure.solution = failure_solution
            else:
                failure.solution = ""

            failure.status = State.CLOSED
            failure.save()
            messages.success(
                request,
                f"Η βλάβη με αριθμό {failure.number} διεκπεραιώθηκε επιτυχώς!"
            )
            return redirect("failures_all")
        except:
            messages.warning(
                request,
                "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα στη διεκπεραίωση της βλάβης! Προσπαθήστε ξανά.",
            )
            return redirect("failure_single", failure.id)
    else:
        raise Http404()


def get_failures_tables_json(user, tele_means, failures, date_from, date_to):
    tables = {}
    for means in tele_means:
        tables[means.name] = list()
        failures_filter_by_means = failures.filter(means=means).filter(
        Q(status=State.PROGRESS) | 
        Q(date_end__gte=date_from) & 
        Q(date_end__lte=date_to) 
        )

        if failures_filter_by_means.count() > 0:                
            for failure in failures_filter_by_means:
                name = "---"
                dig_connection_name = "---"
                if (means.name in ["ΔΙΔΕΣ", "ΕΨΑΔ-ΑΤΚ"]):
                    if(failure.related_dig_connection):
                        name = failure.related_dig_connection.name
                elif means.name == "ΠΥΡΣΕΙΑ":
                    if(failure.related_pyrseia_server):
                        name = failure.related_pyrseia_server.name
                elif means.name == "ΔΟΡΥΦΟΡΙΚΑ":
                    if(failure.related_satellite_node):                    
                        name = failure.related_satellite_node.name
                elif means.name == "HARP":
                    if(failure.related_harp_correspondent):                    
                        name = failure.related_harp_correspondent.correspondent
                elif means.name == "ΣΕΖΜ-ΕΡΜΗΣ":             
                    if failure.related_hermes_node:
                        name = str(failure.related_hermes_node)
                    elif failure.related_hermes_connection:
                        name = str(failure.related_hermes_connection)
                elif means.name == "ΕΥΡΥΖΩΝΙΚΟ":
                    if(failure.related_broadband_transceiver):                    
                        name = ", ".join(str(b) for b in failure.related_broadband_transceiver.all())
                if (means.name in ["ΔΙΔΕΣ", "ΕΨΑΔ-ΑΤΚ"] and failure.related_dig_connection):
                    dig_connection_name = failure.related_dig_connection.number
                else:
                    dig_connection_name = None
                tables[means.name].append({
                    "number": failure.number,
                    "name": name,
                    "dig_connection_name": dig_connection_name,
                    "failure_type": failure.failure_type,
                    "unit": failure.unit,
                    "description": failure.description,
                    "supervisor_unit": failure.supervisor_unit,
                    "date_start": failure.date_start,
                })
    
    return tables

@require_http_methods(["GET"])
@login_required(login_url="login")
def failures_print(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    date_from = datetime.strptime(request.GET["date_from"], "%d/%m/%Y")
    date_to = datetime.strptime(request.GET["date_to"], "%d/%m/%Y")

    failures_tables = {}
    tele_means = CommunicationMeans.objects.all()
    failures = Failure.objects.get_for_user(user).order_by("-date_last_modified")

    failure_tables = get_failures_tables_json(user, tele_means, failures, date_from, date_to)

    context = {
        "date_from": request.GET["date_from"],
        "date_to": request.GET["date_to"],
        "failure_tables": failure_tables,
    }
    
    return render(request, "failures/failures_print.html", context)


@require_http_methods(["GET",])
@login_required(login_url="login")
def failures_print_excel(request):
    user = get_object_or_404(CustomUser, id=request.user.id)

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = f'attachment; filename=FUNCTIONAL_STATE_{request.GET["date_from_excel"]}-{request.GET["date_to_excel"]}.xls'

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("ΒΛΑΒΕΣ")

    date_from = datetime.strptime(request.GET["date_from_excel"], "%d/%m/%Y")
    date_to = datetime.strptime(request.GET["date_to_excel"], "%d/%m/%Y")

    tele_means = CommunicationMeans.objects.all()
    failures = Failure.objects.get_for_user(user).order_by("-date_last_modified")

    failure_tables = get_failures_tables_json(user, tele_means, failures, date_from, date_to)

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    ws.write(0, 0, "ΓΕΝΙΚΟ ΕΠΙΤΕΛΕΙΟ ΣΤΡΑΤΟΥ", font_style)
    ws.write(1, 0, "487 ΤΑΓΜΑ ΔΙΑΒΙΒΑΣΕΩΝ", font_style)
    ws.write(2, 0, "ΚΕΝΤΡΟ ΕΠΙΚΟΙΝΩΝΙΩΝ", font_style)

    ws.write(4, 0, 'ΚΑΤΑΣΤΑΣΗ ΛΕΙΤΟΥΡΓΙΚΟΤΗΤΑΣ ΕΦΑΡΜΟΓΗΣ "ΚΔΕΣ-ΖΕΥΞΙΣ"', font_style)
    ws.write(5, 0, f'{request.GET["date_from_excel"]} - {request.GET["date_to_excel"]}', font_style)
    
    row_num = 8
    for name, table in failure_tables.items():
        if table:
            row_num += 1
            if name == "ΔΙΔΕΣ":
                var_column = "ΨΗΦΙΑΚΟ ΚΥΚΛΩΜΑ"
            if name == "ΔΟΡΥΦΟΡΙΚΑ":
                var_column = "ΚΟΜΒΟΣ"
            if name == "ΕΥΡΥΖΩΝΙΚΟ":
                var_column = "ΠΟΜΠΟΔΕΚΤΗΣ"
            if name == "ΕΨΑΔ-ΑΤΚ":
                var_column = "ΓΡΑΜΜΗ"
            if name == "ΠΥΡΣΕΙΑ":
                var_column = "ΕΞΥΠΗΡΕΤΗΤΗΣ"
            if name == "HARP":
                var_column = "ΑΝΤΑΠΟΚΡΙΤΗΣ"
            if name == "ΣΕΖΜ-ΕΡΜΗΣ":
                var_column = "ΚΟΜΒΟΣ/ΖΕΥΞΗ"

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            ws.write(row_num, 0, name, font_style)
            row_num += 1

            columns = ["Α/Α", var_column, "ΤΥΠΟΣ ΒΛΑΒΗΣ", "ΠΕΡΙΓΡΑΦΗ", "ΜΟΝΑΔΑ (ΣΧΗΜΑΤΙΣΜΟΣ)", "ΑΠΟ"]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            font_style = xlwt.XFStyle()
            for failure in table:
                row_num += 1

                ws.write(row_num, 0, str(failure["number"]), font_style)
                if failure['dig_connection_name']:
                    ws.write(row_num, 1, f"DIG {str(failure['dig_connection_name'])} {str(failure['name'])}", font_style)
                else:
                    ws.write(row_num, 1, str(failure["name"]), font_style)
                ws.write(row_num, 2, str(failure["failure_type"]), font_style)
                ws.write(row_num, 3, str(failure["description"]), font_style)
                ws.write(row_num, 4, f"{str(failure['unit'])} ({str(failure['supervisor_unit'])})", font_style)
                ws.write(row_num, 5, str(failure["date_start"]), font_style)

            row_num += 1

    wb.save(response)

    return response



#THESE 2 FUNCTIONS (dashboard and dashboard_redirect )

def dashboard(request):
    labels = []     
    data = []       
    means = []
    units = []
    units.append("ΟΛΕΣ")
    means.append("ΟΛΑ")

    for failure in Failure.objects.all(): # Failure is a class declared in helpdesk_app/models.py
        means_name = failure.means.name
        if failure.unit.name not in units:
            units.append(failure.unit.name)

        if means_name not in labels:
            tmp_queryset = Failure.objects.filter( Q(status="CL") & Q(means__name=means_name))
            if tmp_queryset.count() != 0:
                labels.append(means_name)
                data.append(tmp_queryset.count())

    if request.method == 'POST':
        dashboard_id = request.POST.get('submitString')
        return redirect('dashboard_redirect', dashboard_id)


    selected_unit = units[0]
    units.remove(selected_unit)

    for l in labels:
        means.append(l)

    selected_mean = means[0]
    means.remove(selected_mean)

    Sum = sum(data)
    data_prc = []
    prc_first_value = 0
    first_value = 0
    first_type = " "
    for i in range(0,len(data)):
        data_prc.append(round(100 * (data[i] / Sum),2))
        prc_first_value = data_prc[0]
        first_value = data[0]

    color_pallet = ["rgba(143,48,33,1)", "rgba(107,106,44,1)", "rgba(29,71,66,1)","rgba(29,49,71,1)","rgba(40,32,77,1)","rgba(66,27,47,1)","rgba(82,65,33,1)"]

    return render(request, 'dashboard.html', {
        'labels'          : labels,
        'data'            : data,
        'data_prc'        : data_prc,
        'units'           : units,
        'means'           : means,
        'color_pallet'    : color_pallet,
        'selected_mean'   : selected_mean,
        'selected_unit'   : selected_unit,
    })

def dashboard_redirect(request,dashboard_id):
    labels = []
    data = []
    data_prc = []
    units = []
    means = []
    type_labels = []
    first_type = []

    prc_first_value = 0
    first_value = 0
    first_mean = " "

    units.append("ΟΛΕΣ")
    means.append("ΟΛΑ")

    index = dashboard_id.find("+")
    selected_unit = dashboard_id[0:index]
    selected_mean = dashboard_id[index + 1: len(dashboard_id)]
    selected_unit = selected_unit.replace("-","/")

    if selected_mean == "ΟΛΑ" and selected_unit == "ΟΛΕΣ":
        for failure in Failure.objects.all():
            means_name = failure.means.name
            if means_name not in labels:
                tmp_queryset = Failure.objects.filter( Q(status="CL") & Q(means__name=means_name))
                if tmp_queryset.count() != 0:
                    labels.append(means_name)
                    data.append(tmp_queryset.count())
    
    elif selected_mean != "ΟΛΑ" and selected_unit == "ΟΛΕΣ":
        for failure in Failure.objects.all():
            failure_type = failure.failure_type.name
            if failure_type not in labels:
                tmp_queryset = Failure.objects.filter( Q(status="CL") & Q(means__name=selected_mean) & Q(failure_type__name=failure_type))
                if tmp_queryset.count() != 0:
                    labels.append(failure_type)
                    data.append(tmp_queryset.count())

    elif selected_mean == "ΟΛΑ" and selected_unit != "ΟΛΕΣ":
        for failure in Failure.objects.all():
            means_name = failure.means.name
            if means_name not in labels:
                tmp_queryset = Failure.objects.filter( Q(status="CL") & Q(unit__name=selected_unit) & Q(means__name=means_name))
                if tmp_queryset.count() != 0:
                    labels.append(means_name)
                    data.append(tmp_queryset.count())

    else:
        for failure in Failure.objects.all():
            failure_type = failure.failure_type.name
            if failure_type not in labels:
                tmp_queryset = Failure.objects.filter( Q(status="CL") & Q(unit__name=selected_unit) & Q(means__name=selected_mean) & Q(failure_type__name=failure_type))
                if tmp_queryset.count() != 0:
                    labels.append(failure_type)
                    data.append(tmp_queryset.count())

    for failure in Failure.objects.all():
        if failure.unit.name not in units:
            units.append(failure.unit.name)
    units.remove(selected_unit)

    for failure in Failure.objects.all():
        if failure.means.name not in means:
            means.append(failure.means.name)
    means.remove(selected_mean)

    Sum = sum(data)
    for i in range(0,len(data)):
        data_prc.append(round(100 * (data[i] / Sum),2))

    if data_prc and data_prc[0] == 100 :
        prc_first_value = data_prc[0]
        first_value = data[0]
        if selected_mean == "ΟΛΑ": 
            first_mean = labels[0]
        else :
            first_mean = selected_mean
        if selected_unit == "ΟΛΕΣ":
            for failure in Failure.objects.all():
                failure_type = failure.failure_type.name
                if failure_type not in type_labels:
                    tmp_queryset = Failure.objects.filter( Q(status="CL") & Q(means__name=first_mean) & Q(failure_type__name=failure_type))
                    if tmp_queryset.count() != 0:
                        type_labels.append(failure_type)

        else:
            for failure in Failure.objects.all():
                failure_type = failure.failure_type.name
                if failure_type not in type_labels:
                    tmp_queryset = Failure.objects.filter( Q(status="CL") & Q(unit__name=selected_unit) & Q(means__name=first_mean) & Q(failure_type__name=failure_type))
                    if tmp_queryset.count() != 0:
                        type_labels.append(failure_type)

        first_type = type_labels[0]

    color_pallet = ["rgba(143,48,33,1)", "rgba(107,106,44,1)", "rgba(29,71,66,1)","rgba(29,49,71,1)","rgba(40,32,77,1)","rgba(66,27,47,1)","rgba(82,65,33,1)"]
    for i in range(5):
        color_pallet += color_pallet

    return render(request, 'dashboard.html', {
        'labels'          : labels,
        'data'            : data,
        'data_prc'        : data_prc,
        'units'           : units,
        'means'           : means,
        'color_pallet'    : color_pallet,
        'selected_mean'   : selected_mean,
        'selected_unit'   : selected_unit,
        'prc_first_value' : prc_first_value,
        'first_value'     : first_value,
        'first_type'      : first_type,
        'first_mean'      : first_mean,
    })
