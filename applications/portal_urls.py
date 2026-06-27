"""
portal_urls.py  —  Include this in new_spark_website/urls.py as:
    path('portal/', include('applications.portal_urls')),
"""
from django.urls import path
from . import portal_views

urlpatterns = [
    # Auth
    path('login/',                                    portal_views.portal_login,                name='portal_login'),
    path('logout/',                                   portal_views.portal_logout,               name='portal_logout'),

    # Dashboard
    path('dashboard/',                                portal_views.dashboard,            name='portal_dashboard'),

    # Application detail + actions
    path('application/<int:app_id>/',                 portal_views.portal_application_detail,   name='portal_application_detail'),
    path('application/<int:app_id>/action/',          portal_views.portal_update_status,        name='portal_update_status'),
    path('application/<int:app_id>/delete/',          portal_views.portal_delete_application,   name='portal_delete_application'),
    path('application/<int:app_id>/export-pdf/',      portal_views.portal_export_pdf_single,    name='portal_export_pdf_single'),

    # Exports
    path('export/csv/',                               portal_views.portal_export_csv,           name='portal_export_csv'),
    path('export/pdf/',                               portal_views.portal_export_pdf_summary,   name='portal_export_pdf'),

    # User management (SuperAdmin only)
    path('users/',                                    portal_views.portal_users,                name='portal_users'),
    path('users/create/',                             portal_views.portal_create_reviewer,      name='portal_create_reviewer'),
    path('users/<int:user_id>/remove/',               portal_views.portal_remove_reviewer,      name='portal_remove_reviewer'),
]
