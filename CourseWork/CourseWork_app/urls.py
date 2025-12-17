from django.urls import path, re_path
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.home, name='home'),
    path('navigator/', views.navigator, name='navigator'),
    path('patients/', views.patients_list, name='patients'),
    path('doctors/', views.doctors_list, name='doctors'),
    path('diagnoses/', views.diagnoses, name='diagnoses'),
    path('specialties/', views.specialties_list, name='specialties'),
    path('about/', views.about, name='about'),

    # Просмотр деталей
    re_path(r'^patient/(?P<patient_id>\d+)/$', views.medical_records, name='medical_records'),
    re_path(r'^doctor/(?P<doctor_id>\d+)/$', views.doctor_profile, name='doctor_profile'),
    re_path(r'^diagnose/(?P<diagnose_id>\d+)/$', views.treatment_regimes, name='treatment_regimes'),

    # Пациенты
    path('patient/<int:pk>/full-update/', views.patient_full_update, name='patient_full_update'),
    path('patient/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('export/patients.txt', views.export_patients_txt, name='export_patients_txt'),
    path('export/patients.xlsx', views.export_patients_excel, name='export_patients_excel'),

    # Врачи
    path('doctor/<int:pk>/full-update/', views.doctor_full_update, name='doctor_full_update'),
    path('doctor/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    path('export/doctors.txt', views.export_doctors_txt, name='export_doctors_txt'),
    path('export/doctors.xlsx', views.export_doctors_excel, name='export_doctors_excel'),

    # Диагнозы
    path('diagnosis/<int:pk>/full-update/', views.diagnosis_full_update, name='diagnosis_full_update'),
    path('diagnosis/<int:pk>/delete/', views.diagnosis_delete, name='diagnosis_delete'),
    path('export/diagnoses.txt', views.export_diagnoses_txt, name='export_diagnoses_txt'),
    path('export/diagnoses.xlsx', views.export_diagnoses_excel, name='export_diagnoses_excel'),

    # Лечение
    path('treatment/<int:pk>/update/', views.treatment_update, name='treatment_update'),
    path('treatment/<int:pk>/delete/', views.treatment_delete, name='treatment_delete'),

    # Записи на прием
    path('appointments_list/', views.appointments_list, name='appointments_list'),
    path('appointment/<int:pk>/full-update/', views.appointment_update, name='appointment_update'),
    path('appointment/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),

    # Специальности
    path('specialty/<int:pk>/update/', views.specialty_update, name='specialty_update'),
    path('specialty/<int:pk>/delete/', views.specialty_delete, name='specialty_delete'),

    # Дополнительные пути
    path('appointment/', views.appointment_create, name='appointment_create'),
    path('appointment/success/', views.appointment_success, name='appointment_success'),
    path('random-doctor/', views.doctor_redirect, name='random_doctor'),
    path('redirect-example/', views.redirect_example, name='redirect_example'),
    path('old-patients/', views.old_patients_redirect, name='old_patients'),
    path('export/general/excel/', views.export_general_report, name='export_general_report'),

    # Параметры по умолчанию (уберите если не нужны)
    path('patient-view/', views.patient_view, name='patient_view_default'),
    path('diagnose-view/<int:diagnose_id>/', views.diagnose_view, name='diagnose_view'),
    re_path(r'^doctor-view/$', views.doctor_view, name='doctor_view_default'),
    re_path(r'^doctor-view/(?P<doctor_id>\d+)/$', views.doctor_view, name='doctor_view'),
]