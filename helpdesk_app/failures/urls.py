from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from . import views
from django.urls import include

urlpatterns = [
    path('', views.failures_all, name='failures_all'),
    path('new', views.failure_new, name='failure_new'),
    path('print', views.failures_print, name='failures_print'),
    path('print_excel', views.failures_print_excel, name='failures_print_excel'),
    path('<int:failure_id>/', views.failure_single, name='failure_single'),
    path('<int:failure_id>/edit', views.failure_edit, name='failure_edit'),
    path('<int:failure_id>/delete', views.failure_delete, name='failure_delete'),
    path('<int:failure_id>/dispatcher', views.failure_dispatcher, name='failure_dispatcher'),
    path('<int:failure_id>/complete', views.failure_complete, name='failure_complete'),
] 