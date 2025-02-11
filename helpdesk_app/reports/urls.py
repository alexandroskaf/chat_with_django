from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from . import views
from django.urls import include

urlpatterns = [
    path('', views.reports_all, name='reports_all'),
    path('new', views.report_new, name='report_new'),
    path('print', views.reports_print, name='reports_print'),
    path('print_excel', views.reports_print_excel, name='reports_print_excel'),
    path('<int:report_id>/', views.report_single, name='report_single'),
    path('<int:report_id>/edit', views.report_edit, name='report_edit'),
    path('<int:report_id>/delete', views.report_delete, name='report_delete'),
    path('<int:report_id>/dispatcher', views.report_dispatcher, name='report_dispatcher'),
    path('<int:report_id>/complete', views.report_complete, name='report_complete'),

]