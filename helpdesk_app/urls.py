from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from . import views
from .failures.views import dashboard,dashboard_redirect

from django.urls import include

urlpatterns = [
    # home
    path('', views.home, name='home'),
    
    # registration
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('change_password/', views.change_password, name='change_password'),

    # Dashboard URLs
    path('dashboard/', dashboard, name='dashboard'),
    #Redirection based on the drop down list selection
    path(r'dashboard/<str:dashboard_id>',dashboard_redirect, name='dashboard_redirect'),


    # failures urls
    path('failures/', include('helpdesk_app.failures.urls')),
    # reports urls
    path('reports/', include('helpdesk_app.reports.urls')),


    # ajax calls
    #re_path(r'^ajax/dashboard_chart/$', views.dashboard_chart, name='dashboard_chart'),
    re_path(r'^ajax/get_failure_types/$', views.get_failure_types, name='get_failure_types'),
    re_path(r'^ajax/get_related_data_dig/$', views.get_related_data_dig, name='get_related_data_dig'),
    re_path(r'^ajax/get_related_data_harp/$', views.get_related_data_harp, name='get_related_data_harp'),
    re_path(r'^ajax/get_related_data_satellite/$', views.get_related_data_satellite, name='get_related_data_satellite'),
    re_path(r'^ajax/get_related_data_pyrseia/$', views.get_related_data_pyrseia, name='get_related_data_pyrseia'),
    re_path(r'^ajax/get_related_data_hermes_connection/$', views.get_related_data_hermes_connection, name='get_related_data_hermes_connection'),
    re_path(r'^ajax/get_related_data_hermes_node/$', views.get_related_data_hermes_node, name='get_related_data_hermes_node'),
    re_path(r'^ajax/get_related_data_broadband/$', views.get_related_data_broadband, name='get_related_data_broadband'),
    re_path(r'^ajax/get_dispatchers/$', views.get_dispatchers, name='get_dispatchers'),
    re_path(r'^ajax/get_counters/$', views.get_counters, name='get_counters'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
