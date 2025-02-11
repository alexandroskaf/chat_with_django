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

from .models import *
from .forms import *
from .tables import *
from .models_managers import *
from .filters import *
from .utils import *


################## HOME ###################
@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def home(request):
    user = get_object_or_404(CustomUser, id=request.user.id)

    # counters for failures
    all_failures_count = Failure.objects.count_all(user)
    new_failures_count = Failure.objects.count_new(user)
    open_failures_count = Failure.objects.count_open(user)
    progress_failures_count = Failure.objects.count_progress(user)
    closed_failures_count = Failure.objects.count_closed(user)

    # counters for reports
    all_reports_count = Report.objects.count_all(user)
    new_reports_count = Report.objects.count_new(user)
    open_reports_count = Report.objects.count_open(user)
    progress_reports_count = Report.objects.count_progress(user)
    closed_reports_count = Report.objects.count_closed(user)

    if user.is_admin() or user.is_manager() or user.is_dispatcher():
        user_ui_format = "home.html"
    elif user.is_ddb() or user.is_simple_user():
        user_ui_format = "home_for_user.html"

    context = {
        "user": user,
        "all_failures": all_failures_count,
        "new_failures": new_failures_count,
        "open_failures": open_failures_count,
        "progress_failures": progress_failures_count,
        "closed_failures": closed_failures_count,
        "all_reports": all_reports_count,
        "new_reports": new_reports_count,
        "open_reports": open_reports_count,
        "progress_reports": progress_reports_count,
        "closed_reports": closed_reports_count,
    }

    return render(request, user_ui_format, context)


############## REGISTRATION ###############
@require_http_methods(["GET", "POST"])
def login(request):
    if not request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "registration/login.html")
        elif request.method == "POST":     
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                _login(request, user)
                if user.password_has_changed == False:
                    return redirect("change_password")
                else:
                    return redirect("home")
            else:
                # Return an 'invalid login' error message.
                messages.error(
                    request, "Παρακαλώ εισάγετε το σωστό όνομα και κωδικό χρήστη."
                )
                return render(request, "registration/login.html")
    else:
        return redirect("home")


@require_http_methods(["GET"])
@login_required(login_url="login")
def logout(request):
    _logout(request)
    return redirect("login")


@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.password_has_changed = True
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Ο κωδικός σας άλλαξε!")
            return redirect("home")
        else:
            messages.error(request, "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα!")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "registration/change_password.html", {"form": form})


@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def user_profile(request):

    if request.method == "GET":
        user = get_object_or_404(CustomUser, id=request.user.id)
        form = CustomUserChangeForm(instance=user, request=request)
    elif request.method == "POST":
        user = get_object_or_404(CustomUser, id=request.user.id)
        form = CustomUserChangeForm(request.POST, instance=user, request=request)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Ο χρήστης {} ενημερώθηκε επιτυχώς!".format(user.username)
            )
        else:
            messages.warning(request, "Δυστυχώς, παρουσιάστηκε κάποιο πρόβλημα!")

    return render(request, "registration/user_profile.html", {"form": form,})


################ DASHBOARD ################
# dashboard function is implemented at helpdesk_app/failures/views.py 
# In the future this function might replace the the one at the failures directory
# @require_http_methods(["GET", "POST"])
# @login_required(login_url="login")
# def dashboard(request):
#     current_user = get_object_or_404(CustomUser, id=request.user.id)
#     if current_user.is_simple_user():
#         raise Http404()

#     comm_means_progress = CommunicationMeans.objects.get_progress(current_user)

#     context = {
#         "comm_means_progress": comm_means_progress,
#     }
#     return render(request, "dashboard.html", context)


############## AJAX CALLS #################
@require_http_methods(["GET"])
@login_required(login_url="login")
def get_failure_types(request):
    means_name = request.GET.get("means_name", None)
    failure_types = list(
        FailureType.objects.filter(Q(means__name=means_name) | Q(means=None)).values()
    )
    data = {"means": means_name, "failure_types": failure_types}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_related_data_dig(request):
    # relevant only for the case when epsad is selected, to distinguish between internal and external connections.
    # means_input of size 2 means that a "|" was used to indicate the external connections choice
    means_input = request.GET.get("means_name", None).split("|")
    if len(means_input) == 2:
        epsad_external = True
    else:
        epsad_external = False

    means_name = means_input[0]
    unit_name = request.GET.get("unit_name", None)

    unit = Unit.objects.get(name=unit_name)
    means = CommunicationMeans.objects.get(name=means_name)

    # if a non-formation unit is selected, search the connections that belong to its parent formation
    if not unit.is_formation:
        unit = unit.parent

    dig_list = []
    for dig in DigConnection.objects.filter((Q(unit_from=unit) | Q(unit_to=unit)) & Q(means=means) & Q(external=epsad_external)):
        dig_list.append({"id": dig.id, "name": str(dig)})

    data = {"related_dig_connections": dig_list}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_related_data_harp(request):
    unit_name = request.GET.get("unit_name", None)

    unit = Unit.objects.get(name=unit_name)

    if not unit.is_formation:
        unit = unit.parent

    harp_list = []
    for harp in HarpCorrespondent.objects.filter(unit=unit):
        harp_list.append({"id": harp.id, "name": str(harp)})

    data = {"related_harp_correspondent": harp_list}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_related_data_satellite(request):
    unit_name = request.GET.get("unit_name", None)

    unit = Unit.objects.get(name=unit_name)

    if not unit.is_formation:
        unit = unit.parent

    satellite_list = []
    for satellite in SatelliteNode.objects.filter(Q(unit__name=str(unit))):
        satellite_list.append({"id": satellite.id, "name": str(satellite)})

    data = {"related_satellite_node": satellite_list}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_related_data_broadband(request):
    unit_name = request.GET.get("unit_name", None)

    unit = Unit.objects.get(name=unit_name)

    if not unit.is_formation:
        unit = unit.parent

    broadband_list = []
    for broadband in BroadbandTransceiver.objects.filter(unit_from=unit):
        broadband_list.append({"id": broadband.id, "name": str(broadband)})

    data = {"related_broadband_transceiver": broadband_list}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_related_data_pyrseia(request):
    unit_name = request.GET.get("unit_name", None)

    unit = Unit.objects.get(name=unit_name)

    if not unit.is_formation:
        unit = unit.parent

    pyrseia_servers = []
    for server in PyrseiaServer.objects.filter(Q(unit__name=str(unit))):
        pyrseia_servers.append({"id": server.id, "name": str(server)})

    data = {"related_pyrseia_server": pyrseia_servers}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_related_data_hermes_connection(request):
    unit_name = request.GET.get("unit_name", None)

    unit = Unit.objects.get(name=unit_name)

    if not unit.is_formation:
        unit = unit.parent

    hermes_connections = []
    for conn in HermesConnection.objects.filter(Q(node_from__unit__name=str(unit))):
        hermes_connections.append({"id": conn.id, "name": str(conn)})

    data = {"related_hermes_connection": hermes_connections}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_related_data_hermes_node(request):
    unit_name = request.GET.get("unit_name", None)

    unit = Unit.objects.get(name=unit_name)

    if not unit.is_formation:
        unit = unit.parent

    hermes_nodes = []
    for node in HermesNode.objects.filter(Q(unit__name=str(unit))):
        hermes_nodes.append({"id": node.id, "name": str(node)})

    data = {"related_hermes_node": hermes_nodes}

    return JsonResponse(data)


@require_http_methods(["GET"])
@login_required(login_url="login")
def get_dispatchers(request):
    means_name = request.GET.get("means_name", None)

    means = CommunicationMeans.objects.get(name=means_name)


    dispatchers = []
    for user in CustomUser.objects.filter(
        Q(means__in = [means])
        ):
        dispatchers.append({"id": user.id, "name": str(user)})

    data = {"dispatcher_form_select": dispatchers}

    return JsonResponse(data)

@require_http_methods(["GET"])
@login_required(login_url="login")
def get_counters(request):
    user = get_object_or_404(CustomUser, id=request.user.id)

    new_failures_count = Failure.objects.count_new(user)
    open_failures_count = Failure.objects.count_open(user)
    progress_failures_count = Failure.objects.count_progress(user)
    closed_failures_count = Failure.objects.count_closed(user)

    # counters for reports
    new_reports_count = Report.objects.count_new(user)
    open_reports_count = Report.objects.count_open(user)
    progress_reports_count = Report.objects.count_progress(user)
    closed_reports_count = Report.objects.count_closed(user)

    counter_data = {
      "new_failures_count": new_failures_count,
      "open_failures_count": open_failures_count,
      "progress_failures_count": progress_failures_count,
      "closed_failures_count": closed_failures_count,
      "new_reports_count": new_reports_count,
      "open_reports_count": open_reports_count,
      "progress_reports_count": progress_reports_count,
      "closed_reports_count": closed_reports_count
    }

    return JsonResponse(counter_data)
