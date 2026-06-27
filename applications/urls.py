from django.urls import path
from . import views, portal_views

urlpatterns = [
    path('',                  views.home,           name='home'),
    path('apply/',            views.apply,          name='apply'),
    path('success/',          views.success,        name='success'),
    path('guidelines/',       views.guidelines,     name='guidelines'),
    path('projects/',         views.projects,       name='projects'),
    path('contact/',          views.contact,        name='contact'),
    path('forms/',            views.forms_download, name='forms'),
    path('login/',            views.user_login,     name='login'),
    path('logout/',           views.user_logout,    name='logout'),
    path('dashboard/',        portal_views.dashboard, name='dashboard'),
    path('dashboard/export/', views.export_csv,     name='export_csv'),
    path('dashboard/export-minimal/', views.export_minimal_csv, name='export_minimal_csv'),
    path('dashboard/export-pdf/', views.export_pdf, name='export_pdf'),
    path('dashboard/export-pdf/<int:app_id>/', views.export_pdf_single, name='export_pdf_single'),
]
