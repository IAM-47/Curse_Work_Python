from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse
from .forms import *
from .models import *
from datetime import datetime, date
import random, io
import pandas as pd



def appointments_list(request):
    """Список записей на прием"""
    appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-appointment_date',
                                                                                    '-appointment_time')

    return render(request, 'appointments_list.html', {
        'appointments': appointments,
    })


def navigator(request):
    """Страница-навигатор"""
    return render(request, 'navigator.html')


def about(request):
    """О системе"""
    return render(request, 'about.html')


def home(request):
    """Главная страница"""
    stats = {
        'doctors_count': Doctor.objects.count(),
        'patients_count': Patient.objects.count(),
        'appointments_today': Appointment.objects.filter(
            appointment_date=date.today(),
            status='scheduled'
        ).count(),
        'specialties_count': Specialty.objects.count(),
    }
    return render(request, 'index.html', {'stats': stats})


def patients_list(request):
    """Список пациентов из БД Django"""
    search_query = request.GET.get('search', '')

    if search_query:
        patients = Patient.objects.filter(
            Q(last_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(middle_name__icontains=search_query)
        ).order_by('id')
    else:
        patients = Patient.objects.all().order_by('id')

    # Преобразуем для шаблона
    patients_data = []
    for index, patient in enumerate(patients, start=1):
        patients_data.append({
            'id': patient.id,
            '№': index,
            'Фамилия': patient.last_name,
            'Имя': patient.first_name,
            'Отчество': patient.middle_name if patient.middle_name else '',
            'дата_рождения': patient.birth_date.strftime('%d.%m.%Y'),
            'Возраст': patient.age
        })

    # Обработка добавления пациента
    if request.method == 'POST' and 'add_patient' in request.POST:
        form = AddPatientForm(request.POST)
        if form.is_valid():
            new_patient = Patient(
                last_name=form.cleaned_data['last_name'],
                first_name=form.cleaned_data['first_name'],
                middle_name=form.cleaned_data.get('middle_name', ''),
                birth_date=form.cleaned_data['birth_date']
            )
            new_patient.save()
            return redirect('patients')
    else:
        form = AddPatientForm()

    return render(request, 'patients.html', {
        'patients': patients_data,
        'search_query': search_query,
        'patient_form': form,
    })


def medical_records(request, patient_id):
    """Карточка пациента из БД Django"""
    patient = get_object_or_404(Patient, id=patient_id)

    try:
        medical_record = patient.medical_record
        record_data = {
            'Пол': medical_record.gender,
            'Адрес': medical_record.address,
            'Телефон': medical_record.phone,
            'Полис': medical_record.insurance_policy,
            'СНИЛС': medical_record.snils,
            'Серия': medical_record.passport_series,
            'Номер': medical_record.passport_number,
            'Образование': medical_record.education,
        }
    except MedicalRecord.DoesNotExist:
        record_data = {}

    patient_data = {
        'Фамилия': patient.last_name,
        'Имя': patient.first_name,
        'Отчество': patient.middle_name if patient.middle_name else '',
        'дата_рождения': patient.birth_date.strftime('%d.%m.%Y'),
    }

    return render(request, 'medical_records.html', {
        'patient': patient_data,
        'medical_record': record_data,
        'patient_id': patient_id
    })


def diagnoses(request):
    """Список диагнозов из БД Django"""
    search_query = request.GET.get('search', '')

    # Обработка добавления диагноза
    if request.method == 'POST' and 'add_diagnose' in request.POST:
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('diagnoses')
    else:
        form = DiagnosisForm()



    if search_query:
        diagnoses_list = Diagnosis.objects.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(specialty__name__icontains=search_query)
        ).select_related('specialty')
    else:
        diagnoses_list = Diagnosis.objects.select_related('specialty').all()

    # Преобразуем для шаблона
    diagnoses_data = []
    for index, diagnosis in enumerate(diagnoses_list, start=1):
        diagnoses_data.append({
            'id': diagnosis.id,
            '№': index,
            'Код_МКБ': diagnosis.code,
            'Наименование': diagnosis.name,
            'Категория': diagnosis.specialty.name if diagnosis.specialty else 'Не указана',
            'Симптомы': diagnosis.symptoms[:100] + '...' if len(diagnosis.symptoms) > 100 else diagnosis.symptoms,
        })

    return render(request, 'diagnoses.html', {
        'diagnoses': diagnoses_data,
        'search_query': search_query,
        'diagnosis_form': form,
    })


def specialties_list(request):
    """Список специальностей из БД Django"""
    search_query = request.GET.get('search', '')
    # Обработка добавления специальности
    if request.method == 'POST' and 'add_specialty' in request.POST:
        form = SpecialtyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('specialties')
    else:
        form = SpecialtyForm()


    if search_query:
        specialties = Specialty.objects.filter(
            Q(name__icontains=search_query)
        ).order_by('id')
    else:
        specialties = Specialty.objects.all().order_by('id')

    # Преобразуем для шаблона
    specialties_data = []
    for index, specialty in enumerate(specialties, start=1):
        # Считаем сколько врачей этой специальности
        doctors_count = Doctor.objects.filter(specialty=specialty).count()
        # Считаем сколько диагнозов относится к этой специальности
        diagnoses_count = Diagnosis.objects.filter(specialty=specialty).count()

        specialties_data.append({
            'id': specialty.id,
            '№': index,
            'Название': specialty.name,
            'Количество врачей': doctors_count,
            'Количество диагнозов': diagnoses_count,
        })

    return render(request, 'specialties.html', {
        'specialties': specialties_data,
        'search_query': search_query,
        'total_count': specialties.count(),
        'specialties_form': form,
    })


def treatment_regimes(request, diagnose_id):
    """Режим лечения из БД Django"""
    diagnosis = get_object_or_404(Diagnosis, id=diagnose_id)

    try:
        treatment = diagnosis.treatment_regimes.first()  # берем первый метод лечения
        method_data = {
            'Метод_лечения': treatment.treatment_method,
            'Тип_лечения': treatment.treatment_type,
            'Препараты': treatment.medications,
            'Длительность': treatment.duration,
            'Контроль_эффективности': treatment.effectiveness_control,
        }
    except:
        method_data = {}

    diagnosis_data = {
        'Код_МКБ': diagnosis.code,
        'Наименование': diagnosis.name,
        'Категория': diagnosis.specialty.name if diagnosis.specialty else 'Не указана',
        'Симптомы': diagnosis.symptoms,
        'Необходимые_анализы': diagnosis.required_tests,
        'Обследования': diagnosis.examinations,
    }

    return render(request, 'treatment_regimes.html', {
        'diagnose': diagnosis_data,
        'method': method_data,
        'diagnose_id': diagnose_id,
    })


def doctors_list(request):
    """Список врачей из БД Django"""
    search_query = request.GET.get('search', '')

    if request.method == 'POST' and 'add_doctor' in request.POST:
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctors')
    else:
        form = DoctorForm()  # Пустая форма для GET запроса

    # Затем выполняем поиск
    if search_query:
        doctors = Doctor.objects.filter(
            Q(last_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(middle_name__icontains=search_query) |
            Q(specialty__name__icontains=search_query)
        ).select_related('specialty')
    else:
        doctors = Doctor.objects.select_related('specialty').all()

    # Преобразуем для шаблона
    doctors_data = []
    for index, doctor in enumerate(doctors, start=1):
        doctors_data.append({
            'id': doctor.id,
            '№': index,
            'Фамилия': doctor.last_name,
            'Имя': doctor.first_name,
            'Отчество': doctor.middle_name if doctor.middle_name else '',
            'Специальность': doctor.specialty.name if doctor.specialty else 'Не указана',
            'Стаж': f"{doctor.experience} лет",
            'Телефон': doctor.phone,
        })

    return render(request, 'doctors.html', {
        'doctors': doctors_data,
        'search_query': search_query,
        'doctor_form': form,  # Это ключевое!
    })


def doctor_profile(request, doctor_id):
    """Профиль врача из БД Django"""
    doctor = get_object_or_404(Doctor, id=doctor_id)


    try:
        profile = doctor.profile
        profile_data = {
            'Образование': profile.education,
            'Квалификация': profile.get_qualification_display(),
            'Сертификаты': profile.certificates,
            'Доп. Информация': profile.additional_info,
        }
    except DoctorProfile.DoesNotExist:
        profile_data = {}

    doctor_data = {
        'Фамилия': doctor.last_name,
        'Имя': doctor.first_name,
        'Отчество': doctor.middle_name if doctor.middle_name else '',
        'Специальность': doctor.specialty.name,
        'Стаж': f"{doctor.experience} лет",
        'Телефон': doctor.phone,
    }

    return render(request, 'doctor_profiles.html', {
        'doctor': doctor_data,
        'profile': profile_data,
        'doctor_id': doctor_id,
    })


def patient_view(request, patient_id=1):
    """Просмотр пациента по умолчанию"""
    return redirect('medical_records', patient_id=patient_id)


def doctor_view(request, doctor_id=1):
    """Просмотр врача по умолчанию"""
    return redirect('doctor_profile', doctor_id=doctor_id)


def diagnose_view(request, diagnose_id=5):
    """Просмотр диагноза по умолчанию"""
    return redirect('treatment_regimes', diagnose_id=diagnose_id)


def redirect_example(request):
    """Пример переадресации"""
    return redirect('patients')


def old_patients_redirect(request):
    """Переадресация со старого URL"""
    return redirect('patient_view', patient_id=1)


def doctor_redirect(request):
    """Переадресация на случайного врача"""
    doctor_ids = list(Doctor.objects.values_list('id', flat=True))
    if doctor_ids:
        random_id = random.choice(doctor_ids)
        return redirect('doctor_profile', doctor_id=random_id)
    return redirect('doctors')


def appointment_create(request):
    """Создание записи на прием в БД Django"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Сохраняем в БД Django
            appointment = form.save(commit=False)
            appointment.status = 'scheduled'
            appointment.created_at = datetime.now()
            appointment.save()
            return redirect('appointment_success')
    else:
        form = AppointmentForm()

    return render(request, 'appointment.html', {
        'form': form,
        'back_url': '/appointments_list/',
    })


def appointment_success(request):
    """Страница успешной записи"""
    return render(request, 'appointment_success.html')


def diagnosis_by_code(request, code):
    """Поиск диагноза по коду МКБ"""
    diagnosis = get_object_or_404(Diagnosis, code=code)
    return render(request, 'diagnosis_by_code.html', {
        'diagnosis': diagnosis
    })


def patient_search(request, name):
    """Поиск пациента по имени"""
    patients = Patient.objects.filter(
        Q(last_name__icontains=name) |
        Q(first_name__icontains=name) |
        Q(middle_name__icontains=name)
    ).order_by('last_name', 'first_name')

    patients_data = []
    for patient in patients:
        patients_data.append({
            'id': patient.id,
            'ФИО': f"{patient.last_name} {patient.first_name} {patient.middle_name}".strip(),
            'Дата рождения': patient.birth_date.strftime('%d.%m.%Y'),
            'Возраст': patient.age
        })

    return render(request, 'patient_search.html', {
        'patients': patients_data,
        'search_name': name
    })


def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        patient.delete()
        return redirect('patients')

    return render(request, 'confirm_delete.html', {
        'object': f"{patient.last_name} {patient.first_name}",
        'object_name': 'пациента'
    })


def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)

    if request.method == 'POST':
        doctor.delete()
        return redirect('doctors')

    return render(request, 'confirm_delete.html', {
        'object': f"{doctor.last_name} {doctor.first_name}",
        'object_name': 'врача'
    })


def diagnosis_delete(request, pk):
    diagnosis = get_object_or_404(Diagnosis, pk=pk)

    if request.method == 'POST':
        diagnosis.delete()
        return redirect('diagnoses')

    return render(request, 'confirm_delete.html', {
        'object': f"{diagnosis.code} - {diagnosis.name}",
        'object_name': 'диагноз'
    })


def specialty_delete(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)

    if request.method == 'POST':
        specialty.delete()
        return redirect('specialties')

    return render(request, 'confirm_delete.html', {
        'object': specialty.name,
        'object_name': 'специальность'
    })


def treatment_update(request, pk):
    treatment = get_object_or_404(TreatmentRegime, pk=pk)
    if request.method == 'POST':
        form = TreatmentRegimeForm(request.POST, instance=treatment)
        if form.is_valid():
            form.save()
            return redirect('treatment_regimes', diagnose_id=treatment.diagnoses_id)
    else:
        form = TreatmentRegimeForm(instance=treatment)
    return render(request, 'update_form.html', {'form': form, 'title': 'Редактировать метод лечения'})


def medical_record_update(request, pk):
    try:
        medical_record = MedicalRecord.objects.get(patient_id=pk)
    except MedicalRecord.DoesNotExist:
        medical_record = MedicalRecord(patient_id=pk)

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=medical_record)
        if form.is_valid():
            form.save()
            return redirect('medical_records', patient_id=pk)
    else:
        form = MedicalRecordForm(instance=medical_record)

    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'update_form.html', {
        'form': form,
        'title': f'Редактировать карточку пациента: {patient.last_name} {patient.first_name}'
    })


def treatment_delete(request, pk):
    treatment = get_object_or_404(TreatmentRegime, pk=pk)

    if request.method == 'POST':
        treatment.delete()
        return redirect('diagnoses')

    return render(request, 'confirm_delete.html', {
        'object': f"{treatment.diagnoses.code} - {treatment.treatment_method}",
        'object_name': 'метод лечения'
    })


def specialty_update(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    if request.method == 'POST':
        form = SpecialtyForm(request.POST, instance=specialty)
        if form.is_valid():
            form.save()
            return redirect('specialties')
    else:
        form = SpecialtyForm(instance=specialty)
    return render(request, 'update_form.html', {
        'form': form,
        'title': f'Редактировать специальность: {specialty.name}',
        'back_url': reverse('specialties'),
    })


def appointment_update(request, pk):
    appointments_list = get_object_or_404(Specialty, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointments_list)
        if form.is_valid():
            form.save()
            return redirect('appointments_list')
    else:
        form = AppointmentForm(instance=appointments_list)
    return render(request, 'update_form.html', {
        'form': form,
        'title': f'Редактировать запись',
        'back_url': reverse('appointments_list'),
    })


def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        appointment.delete()
        return redirect('appointments_list')

    return render(request, 'confirm_delete.html', {
        'object_name': 'запись'
    })


def patient_full_update(request, pk):
    """Редактирование пациента и его медкарты вместе"""
    patient = get_object_or_404(Patient, pk=pk)

    try:
        medical_record = patient.medical_record
    except MedicalRecord.DoesNotExist:
        medical_record = MedicalRecord(patient=patient)

    if request.method == 'POST':
        form = PatientCombinedForm(request.POST)
        if form.is_valid():
            # Обновляем пациента
            patient.last_name = form.cleaned_data['last_name']
            patient.first_name = form.cleaned_data['first_name']
            patient.middle_name = form.cleaned_data.get('middle_name', '')
            patient.birth_date = form.cleaned_data['birth_date']
            patient.save()

            # Обновляем медкарту
            medical_record.gender = form.cleaned_data.get('gender', '')
            medical_record.address = form.cleaned_data.get('address', '')
            medical_record.phone = form.cleaned_data.get('phone', '')
            medical_record.insurance_policy = form.cleaned_data.get('insurance_policy', '')
            medical_record.snils = form.cleaned_data.get('snils', '')
            medical_record.passport_series = form.cleaned_data.get('passport_series', '')
            medical_record.passport_number = form.cleaned_data.get('passport_number', '')
            medical_record.education = form.cleaned_data.get('education', '')
            medical_record.save()

            return redirect('medical_records', patient_id=pk)
    else:
        # Заполняем форму текущими данными
        initial_data = {
            'last_name': patient.last_name,
            'first_name': patient.first_name,
            'middle_name': patient.middle_name,
            'birth_date': patient.birth_date,
            'gender': medical_record.gender,
            'address': medical_record.address,
            'phone': medical_record.phone,
            'insurance_policy': medical_record.insurance_policy,
            'snils': medical_record.snils,
            'passport_series': medical_record.passport_series,
            'passport_number': medical_record.passport_number,
            'education': medical_record.education,
        }
        form = PatientCombinedForm(initial=initial_data)

    return render(request, 'update_form.html', {
        'form': form,
        'title': f'Редактировать пациента: {patient.full_name}',
        'back_url_card': f'/patient/{pk}/',
        'back_url': f'/patients/',
    })


def doctor_full_update(request, pk):
    """Редактирование врача и его профиля вместе"""
    doctor = get_object_or_404(Doctor, pk=pk)

    try:
        profile = doctor.profile
    except DoctorProfile.DoesNotExist:
        profile = DoctorProfile(doctor=doctor)

    if request.method == 'POST':
        form = DoctorCombinedForm(request.POST)
        if form.is_valid():
            # Обновляем врача
            doctor.last_name = form.cleaned_data['last_name']
            doctor.first_name = form.cleaned_data['first_name']
            doctor.middle_name = form.cleaned_data.get('middle_name', '')
            doctor.specialty = form.cleaned_data['specialty']
            doctor.experience = form.cleaned_data['experience']
            doctor.phone = form.cleaned_data['phone']
            doctor.save()

            # Обновляем профиль
            profile.education = form.cleaned_data.get('education', '')
            profile.qualification = form.cleaned_data.get('qualification', '')
            profile.certificates = form.cleaned_data.get('certificates', '')
            profile.additional_info = form.cleaned_data.get('additional_info', '')
            profile.save()

            return redirect('doctor_profile', doctor_id=pk)
    else:
        # Заполняем форму текущими данными
        initial_data = {
            'last_name': doctor.last_name,
            'first_name': doctor.first_name,
            'middle_name': doctor.middle_name,
            'specialty': doctor.specialty,
            'experience': doctor.experience,
            'phone': doctor.phone,
            'education': profile.education,
            'qualification': profile.qualification,
            'certificates': profile.certificates,
            'additional_info': profile.additional_info,
        }
        form = DoctorCombinedForm(initial=initial_data)

    return render(request, 'update_form.html', {
        'form': form,
        'title': f'Редактировать врача: {doctor.full_name}',
        'back_url_p': f'/doctor/{pk}/',
        'back_url': f'/doctors/'
    })


def diagnosis_full_update(request, pk):
    """Редактирование диагноза и метода лечения вместе"""
    diagnosis = get_object_or_404(Diagnosis, pk=pk)

    # Пробуем получить метод лечения
    treatment = TreatmentRegime.objects.filter(diagnoses=diagnosis).first()

    if request.method == 'POST':
        form = DiagnosisCombinedForm(request.POST)
        if form.is_valid():
            # Обновляем диагноз
            diagnosis.code = form.cleaned_data['code']
            diagnosis.name = form.cleaned_data['name']
            diagnosis.specialty = form.cleaned_data.get('specialty')
            diagnosis.symptoms = form.cleaned_data.get('symptoms', '')
            diagnosis.required_tests = form.cleaned_data.get('required_tests', '')
            diagnosis.examinations = form.cleaned_data.get('examinations', '')
            diagnosis.save()

            # Обновляем или создаем метод лечения
            treatment_method = form.cleaned_data.get('treatment_method', '')
            if treatment_method:  # если есть данные о лечении
                if treatment:  # если лечение уже существует
                    treatment.treatment_method = treatment_method
                    treatment.treatment_type = form.cleaned_data.get('treatment_type', '')
                    treatment.medications = form.cleaned_data.get('medications', '')
                    treatment.duration = form.cleaned_data.get('duration', '')
                    treatment.effectiveness_control = form.cleaned_data.get('effectiveness_control', '')
                    treatment.save()
                else:  # создаем новое лечение
                    TreatmentRegime.objects.create(
                        diagnoses=diagnosis,
                        treatment_method=treatment_method,
                        treatment_type=form.cleaned_data.get('treatment_type', ''),
                        medications=form.cleaned_data.get('medications', ''),
                        duration=form.cleaned_data.get('duration', ''),
                        effectiveness_control=form.cleaned_data.get('effectiveness_control', '')
                    )

            return redirect('treatment_regimes', diagnose_id=pk)
    else:
        # Заполняем форму текущими данными
        initial_data = {
            'code': diagnosis.code,
            'name': diagnosis.name,
            'specialty': diagnosis.specialty,
            'symptoms': diagnosis.symptoms,
            'required_tests': diagnosis.required_tests,
            'examinations': diagnosis.examinations,
        }

        # Добавляем данные лечения, если они есть
        if treatment:
            initial_data.update({
                'treatment_method': treatment.treatment_method,
                'treatment_type': treatment.treatment_type,
                'medications': treatment.medications,
                'duration': treatment.duration,
                'effectiveness_control': treatment.effectiveness_control,
            })

        form = DiagnosisCombinedForm(initial=initial_data)

    return render(request, 'update_form.html', {
        'form': form,
        'title': f'Редактировать диагноз: {diagnosis.code}',
        'back_url_treatment': f'/diagnose/{pk}/',
        'back_url': f'/diagnoses/',
    })


def export_patients_txt(request):
    patients = Patient.objects.all().order_by('last_name', 'first_name')

    content = "МЕДИЦИНСКАЯ СИСТЕМА - ОТЧЕТ ПО ПАЦИЕНТАМ\n"
    content += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    content += "=" * 60 + "\n\n"

    for i, patient in enumerate(patients, 1):
        content += f"{i}. {patient.last_name} {patient.first_name} {patient.middle_name}\n"
        content += f"   Дата рождения: {patient.birth_date.strftime('%d.%m.%Y')}\n"
        content += f"   Возраст: {patient.age} лет\n"

        try:
            record = patient.medical_record
            if record.phone:
                content += f"   Телефон: {record.phone}\n"
        except:
            pass

        content += "\n"

    content += f"\nВсего пациентов: {patients.count()}\n"

    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="patients_report.txt"'
    return response


def export_patients_excel(request):
    """Экспорт пациентов в Excel"""
    patients = Patient.objects.all().order_by('last_name', 'first_name')

    data = []
    for patient in patients:
        try:
            record = patient.medical_record
            phone = record.phone
            address = record.address
        except:
            phone = ''
            address = ''

        data.append({
            'Фамилия': patient.last_name,
            'Имя': patient.first_name,
            'Отчество': patient.middle_name,
            'Дата рождения': patient.birth_date.strftime('%d.%m.%Y'),
            'Возраст': patient.age,
            'Телефон': phone,
            'Адрес': address,
        })

    df = pd.DataFrame(data)

    # Создаем Excel файл в памяти
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Пациенты', index=False)

        # Настраиваем ширину колонок
        worksheet = writer.sheets['Пациенты']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 30)

    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="patients_report.xlsx"'
    return response


def export_doctors_txt(request):
    """Экспорт врачей в TXT"""
    doctors = Doctor.objects.select_related('specialty').all()

    content = "МЕДИЦИНСКАЯ СИСТЕМА - ОТЧЕТ ПО ВРАЧАМ\n"
    content += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    content += "=" * 60 + "\n\n"

    for i, doctor in enumerate(doctors, 1):
        content += f"{i}. {doctor.last_name} {doctor.first_name} {doctor.middle_name}\n"
        content += f"   Специальность: {doctor.specialty.name if doctor.specialty else 'Не указана'}\n"
        content += f"   Стаж: {doctor.experience} лет\n"
        content += f"   Телефон: {doctor.phone}\n"

        try:
            profile = doctor.profile
            if profile.education:
                content += f"   Образование: {profile.education}\n"
        except:
            pass

        content += "\n"

    content += f"\nВсего врачей: {doctors.count()}\n"

    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="doctors_report.txt"'
    return response


def export_doctors_excel(request):
    """Экспорт врачей в Excel"""
    doctors = Doctor.objects.select_related('specialty').all()

    data = []
    for doctor in doctors:
        try:
            profile = doctor.profile
            education = profile.education
            qualification = profile.get_qualification_display()
        except:
            education = ''
            qualification = ''

        data.append({
            'Фамилия': doctor.last_name,
            'Имя': doctor.first_name,
            'Отчество': doctor.middle_name,
            'Специальность': doctor.specialty.name if doctor.specialty else '',
            'Стаж': doctor.experience,
            'Телефон': doctor.phone,
            'Образование': education,
            'Квалификация': qualification,
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Врачи', index=False)

        worksheet = writer.sheets['Врачи']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 30)

    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="doctors_report.xlsx"'
    return response


def export_diagnoses_txt(request):
    """Экспорт диагнозов в TXT"""
    diagnoses = Diagnosis.objects.select_related('specialty').all()

    content = "МЕДИЦИНСКАЯ СИСТЕМА - ОТЧЕТ ПО ДИАГНОЗАМ\n"
    content += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    content += "=" * 60 + "\n\n"

    for i, diagnosis in enumerate(diagnoses, 1):
        content += f"{i}. {diagnosis.code} - {diagnosis.name}\n"
        content += f"   Категория: {diagnosis.specialty.name if diagnosis.specialty else 'Не указана'}\n"

        if diagnosis.symptoms and len(diagnosis.symptoms) > 100:
            content += f"   Симптомы: {diagnosis.symptoms[:100]}...\n"
        elif diagnosis.symptoms:
            content += f"   Симптомы: {diagnosis.symptoms}\n"

        content += "\n"

    content += f"\nВсего диагнозов: {diagnoses.count()}\n"

    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="diagnoses_report.txt"'
    return response


def export_diagnoses_excel(request):
    """Экспорт диагнозов в Excel"""
    diagnoses = Diagnosis.objects.select_related('specialty').all()

    data = []
    for diagnosis in diagnoses:
        treatment = TreatmentRegime.objects.filter(diagnoses=diagnosis).first()

        data.append({
            'Код МКБ': diagnosis.code,
            'Наименование': diagnosis.name,
            'Категория': diagnosis.specialty.name if diagnosis.specialty else '',
            'Симптомы': diagnosis.symptoms[:200] if diagnosis.symptoms else '',
            'Метод лечения': treatment.treatment_method if treatment else '',
            'Препараты': treatment.medications if treatment else '',
            'Длительность': treatment.duration if treatment else '',
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Диагнозы', index=False)

        worksheet = writer.sheets['Диагнозы']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 40)

    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="diagnoses_report.xlsx"'
    return response


def export_general_report(request):
    """Общий отчет по всей системе в Excel"""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 1. Сводная страница
        summary_data = {
            'Показатель': ['Пациенты', 'Врачи', 'Диагнозы', 'Специальности', 'Записи на сегодня'],
            'Количество': [
                Patient.objects.count(),
                Doctor.objects.count(),
                Diagnosis.objects.count(),
                Specialty.objects.count(),
                Appointment.objects.filter(
                    appointment_date=datetime.now().date(),
                    status='scheduled'
                ).count()
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Сводка', index=False)

        # 2. Пациенты
        patients_data = []
        for patient in Patient.objects.all():
            try:
                record = patient.medical_record
                phone = record.phone
                address = record.address
            except:
                phone = ''
                address = ''

            patients_data.append({
                'ФИО': f"{patient.last_name} {patient.first_name} {patient.middle_name}".strip(),
                'Дата рождения': patient.birth_date,
                'Возраст': patient.age,
                'Телефон': phone,
                'Адрес': address,
            })

        if patients_data:
            df_patients = pd.DataFrame(patients_data)
            df_patients.to_excel(writer, sheet_name='Пациенты', index=False)

        # 3. Врачи
        doctors_data = []
        for doctor in Doctor.objects.select_related('specialty').all():
            try:
                profile = doctor.profile
                education = profile.education
            except:
                education = ''

            doctors_data.append({
                'ФИО': f"{doctor.last_name} {doctor.first_name} {doctor.middle_name}".strip(),
                'Специальность': doctor.specialty.name if doctor.specialty else '',
                'Стаж': doctor.experience,
                'Телефон': doctor.phone,
                'Образование': education,
            })

        if doctors_data:
            df_doctors = pd.DataFrame(doctors_data)
            df_doctors.to_excel(writer, sheet_name='Врачи', index=False)

        # 4. Диагнозы
        diagnoses_data = []
        for diagnosis in Diagnosis.objects.select_related('specialty').all():
            treatment = TreatmentRegime.objects.filter(diagnoses=diagnosis).first()
            diagnoses_data.append({
                'Код МКБ': diagnosis.code,
                'Наименование': diagnosis.name,
                'Специальность': diagnosis.specialty.name if diagnosis.specialty else '',
                'Симптомы': (diagnosis.symptoms or '')[:200],
                'Метод лечения': treatment.treatment_method if treatment else '',
                'Препараты': treatment.medications if treatment else '',
                'Длительность': treatment.duration if treatment else '',
            })

        if diagnoses_data:
            df_diagnoses = pd.DataFrame(diagnoses_data)
            df_diagnoses.to_excel(writer, sheet_name='Диагнозы', index=False)


    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="medical_system_full_report.xlsx"'
    return response