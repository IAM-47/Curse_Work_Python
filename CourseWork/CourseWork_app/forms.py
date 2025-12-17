from django import forms
from .models import *
from datetime import date


class AddPatientForm(forms.Form):
    """Форма добавления пациента"""
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    middle_name = forms.CharField(
        max_length=100,
        label='Отчество',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class AppointmentForm(forms.ModelForm):
    """Форма записи на прием"""

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'diagnoses', 'symptoms', 'appointment_date', 'appointment_time']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'diagnoses': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опишите симптомы...'}),
            'appointment_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'min': date.today().isoformat()}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
        labels = {
            'patient': 'Пациент',
            'doctor': 'Врач',
            'diagnoses': 'Диагноз (необязательно)',
            'symptoms': 'Симптомы',
            'appointment_date': 'Дата приема',
            'appointment_time': 'Время приема',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Doctor, Diagnosis
        self.fields['patient'].queryset = Patient.objects.all().order_by('last_name')
        self.fields['doctor'].queryset = Doctor.objects.all().order_by('last_name')
        self.fields['diagnoses'].queryset = Diagnosis.objects.all().order_by('code')


class DoctorForm(forms.ModelForm):
    """Форма для добавления и редактирования врачей"""

    class Meta:
        model = Doctor
        fields = ['last_name', 'first_name', 'middle_name', 'specialty', 'experience', 'phone']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'specialty': 'Специальность',
            'experience': 'Стаж',
            'phone': 'Телефон',
        }


class DoctorProfileForm(forms.ModelForm):
    """Форма для профилей врачей"""

    class Meta:
        model = DoctorProfile
        fields = ['education', 'qualification', 'certificates', 'additional_info']
        widgets = {
            'education': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.Select(attrs={'class': 'form-control'}),
            'certificates': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'education': 'Образование',
            'qualification': 'Квалификаци',
            'certificates': 'Сертификаты',
            'additional_info': 'Дата рождения',
        }


class PatientForm(forms.ModelForm):
    """Форма для добавления и редактирования пациентов"""

    class Meta:
        model = Patient
        fields = ['last_name', 'first_name', 'middle_name', 'birth_date']

        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'birth_date': 'Дата рождения',
        }


class DiagnosisForm(forms.ModelForm):
    """Форма для добавления и редактирования диагнозов"""

    class Meta:
        model = Diagnosis
        fields = ['code', 'name', 'symptoms', 'required_tests', 'examinations', 'specialty']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: A00.0'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название диагноза'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите симптомы...'
            }),
            'required_tests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Необходимые анализы и обследования'
            }),
            'examinations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные обследования'
            }),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'code': 'Код МКБ',
            'name': 'Название диагноза',
            'symptoms': 'Симптомы',
            'required_tests': 'Необходимые анализы',
            'examinations': 'Обследования',
            'specialty': 'Специальность',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['specialty'].queryset = Specialty.objects.all().order_by('name')


class TreatmentRegimeForm(forms.ModelForm):
    """Форма для методов лечения"""

    class Meta:
        model = TreatmentRegime
        fields = ['diagnoses', 'treatment_method', 'treatment_type', 'medications', 'duration', 'effectiveness_control']
        # ↑ используем diagnoses вместо diagnosis
        widgets = {
            'diagnoses': forms.Select(attrs={'class': 'form-control'}),
            'treatment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Медикаментозное лечение'
            }),
            'treatment_type': forms.Select(attrs={'class': 'form-control'}),
            'medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Перечень препаратов и дозировки'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 14 дней'
            }),
            'effectiveness_control': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Критерии эффективности лечения'
            }),
        }
        labels = {
            'diagnoses': 'Диагноз',  # ← здесь тоже
            'treatment_method': 'Метод лечения',
            'treatment_type': 'Тип лечения',
            'medications': 'Препараты',
            'duration': 'Длительность лечения',
            'effectiveness_control': 'Контроль эффективности',
        }


class MedicalRecordForm(forms.ModelForm):
    """Форма для медицинских карт пациентов"""

    class Meta:
        model = MedicalRecord
        fields = ['patient', 'gender', 'address', 'phone', 'insurance_policy', 'snils',
                  'passport_series', 'passport_number', 'education']

        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите полный адрес'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            'insurance_policy': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер полиса ОМС'
            }),
            'snils': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXX-XXX-XXX XX',
                'pattern': '\d{3}-\d{3}-\d{3} \d{2}'
            }),
            'passport_series': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXX',
                'maxlength': '4',
                'pattern': '\d{4}'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXXXX',
                'maxlength': '6',
                'pattern': '\d{6}'
            }),
            'education': forms.Select(attrs={'class': 'form-control'}),
        }

        labels = {
            'patient': 'Пациент',
            'gender': 'Пол',
            'address': 'Адрес',
            'phone': 'Телефон',
            'insurance_policy': 'Полис ОМС',
            'snils': 'СНИЛС',
            'passport_series': 'Серия паспорта',
            'passport_number': 'Номер паспорта',
            'education': 'Образование',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.all().order_by('last_name', 'first_name')


class SpecialtyForm(forms.ModelForm):
    """Форма для специальностей врачей"""

    class Meta:
        model = Specialty
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Терапевт, Хирург, Кардиолог'
            }),
        }
        labels = {
            'name': 'Название специальности',
        }


class PatientCombinedForm(forms.Form):
    """Форма для редактирования пациента + медкарты"""

    # Поля пациента
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    middle_name = forms.CharField(
        max_length=100,
        label='Отчество',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    # Поля медкарты
    gender = forms.ChoiceField(
        choices=MedicalRecord.GENDER_CHOICES,
        required=False,
        label='Пол',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,
        label='Адрес',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    phone = forms.CharField(
        required=False,
        max_length=20,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    insurance_policy = forms.CharField(
        required=False,
        max_length=20,
        label='Полис ОМС',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    snils = forms.CharField(
        required=False,
        max_length=14,
        label='СНИЛС',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    passport_series = forms.CharField(
        required=False,
        max_length=4,
        label='Серия паспорта',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    passport_number = forms.CharField(
        required=False,
        max_length=6,
        label='Номер паспорта',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    education = forms.ChoiceField(
        choices=MedicalRecord.EDUCATION_CHOICES,
        required=False,
        label='Образование',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class DoctorCombinedForm(forms.Form):
    """Форма для редактирования врача + профиля"""

    # Поля врача
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    middle_name = forms.CharField(
        max_length=100,
        label='Отчество',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        label='Специальность',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    experience = forms.IntegerField(
        label='Стаж (лет)',
        min_value=0,
        max_value=50,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Поля профиля
    education = forms.CharField(
        required=False,
        max_length=200,
        label='Образование',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    qualification = forms.ChoiceField(
        choices=DoctorProfile.QUALIFICATION_CHOICES,
        required=False,
        label='Квалификация',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    certificates = forms.CharField(
        required=False,
        label='Сертификаты',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    additional_info = forms.CharField(
        required=False,
        label='Дополнительная информация',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class DiagnosisCombinedForm(forms.Form):
    """Форма для редактирования диагноза + метода лечения"""

    # Поля диагноза
    code = forms.CharField(
        max_length=20,
        label='Код МКБ',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        max_length=200,
        label='Название диагноза',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        label='Специальность',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    symptoms = forms.CharField(
        required=False,
        label='Симптомы',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    required_tests = forms.CharField(
        required=False,
        label='Необходимые анализы',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    examinations = forms.CharField(
        required=False,
        label='Обследования',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

    # Поля метода лечения
    treatment_method = forms.CharField(
        required=False,
        max_length=200,
        label='Метод лечения',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    treatment_type = forms.ChoiceField(
        choices=TreatmentRegime.TREATMENT_TYPE_CHOICES,
        required=False,
        label='Тип лечения',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    medications = forms.CharField(
        required=False,
        label='Препараты',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    duration = forms.CharField(
        required=False,
        max_length=100,
        label='Длительность',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    effectiveness_control = forms.CharField(
        required=False,
        label='Контроль эффективности',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

class SearchForm(forms.Form):
    """Универсальная форма поиска"""

    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск...',
            'style': 'width: 300px;'
        }),
        label=''
    )

    search_by = forms.ChoiceField(
        choices=[
            ('last_name', 'По фамилии'),
            ('first_name', 'По имени'),
            ('code', 'По коду'),
            ('name', 'По названию'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 150px;'}),
        label='Искать'
    )


