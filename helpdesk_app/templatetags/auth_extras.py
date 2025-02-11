from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.template.defaultfilters import register
from django.core.exceptions import ObjectDoesNotExist
from ..models import *

register = template.Library()


@register.filter(name="in_group")
def in_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except ObjectDoesNotExist:
        return False

    return True if group in user.groups.all() else False

@register.filter(name="can_edit")
def can_edit(report, user):
    return report.can_edit(user)

@register.filter(name="can_delete")
def can_delete(report, user):
    return report.can_delete(user)

@register.filter(name="can_complete")
def can_complete(report, user):
    return report.can_complete(user)