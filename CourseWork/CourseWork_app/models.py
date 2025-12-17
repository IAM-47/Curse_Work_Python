from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator




class Specialty(models.Model):
    """Специальности врачей"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название специальности")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"
        ordering = ['id']
        app_label = 'CourseWork_app'
        db_table = 'specialties'

class Doctor(models.Model):
    """Врачи"""
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True)
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.PROTECT,
        verbose_name="Специальность",
        related_name='doctors'
    )
    experience = models.IntegerField(
        verbose_name="Стаж (лет)",
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def __str__(self):
        return f"{self.full_name} ({self.specialty.name})"

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ['id']
        app_label = 'CourseWork_app'
        db_table = 'doctors'

class Patient(models.Model):
    """Пациенты"""
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True)
    birth_date = models.DateField(verbose_name="Дата рождения")

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def __str__(self):
        return f"{self.full_name} (р. {self.birth_date})"

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"
        ordering = ['id']
        app_label = 'CourseWork_app'
        db_table = 'patients'

class Diagnosis(models.Model):
    """Диагнозы"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Код МКБ-10")
    name = models.CharField(max_length=200, verbose_name="Наименование диагноза")
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Специальность",
        related_name='diagnoses'
    )
    symptoms = models.TextField(verbose_name="Симптомы", blank=True)
    required_tests = models.TextField(verbose_name="Необходимые анализы", blank=True)
    examinations = models.TextField(verbose_name="Обследования", blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Диагноз"
        verbose_name_plural = "Диагнозы"
        ordering = ['id']
        app_label = 'CourseWork_app'
        db_table = 'diagnoses'









class DoctorProfile(models.Model):
    """Профили врачей"""
    QUALIFICATION_CHOICES = [
        ('candidate', 'Кандидат медицинских наук'),
        ('doctor', 'Доктор медицинских наук'),
        ('highest', 'Врач высшей категории'),
        ('first', 'Врач первой категории'),
        ('second', 'Врач второй категории'),
    ]

    doctor = models.OneToOneField(
        Doctor,
        on_delete=models.CASCADE,
        verbose_name="Врач",
        related_name='profile'
    )
    education = models.CharField(max_length=200, verbose_name="Образование")
    qualification = models.CharField(
        max_length=100,
        choices=QUALIFICATION_CHOICES,
        verbose_name="Квалификация",
        blank=True
    )
    certificates = models.TextField(verbose_name="Сертификаты", blank=True)
    additional_info = models.TextField(verbose_name="Дополнительная информация", blank=True)

    def __str__(self):
        return f"Профиль: {self.doctor.full_name}"

    class Meta:
        verbose_name = "Профиль врача"
        verbose_name_plural = "Профили врачей"
        app_label = 'CourseWork_app'
        db_table = 'doctor_profiles'

class MedicalRecord(models.Model):
    """Медицинские карты"""
    GENDER_CHOICES = [
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
    ]

    EDUCATION_CHOICES = [
        ('Дошкольное образование', 'Дошкольное образование'),
        ('Начальное общее образование', 'Начальное общее образование'),
        ('Основное общее образование', 'Основное общее образование'),
        ('Среднее общее образование', 'Среднее общее образование'),
        ('Среднее профессиональное образование', 'Среднее профессиональное образование'),
        ('Высшее образование — бакалавриат', 'Высшее образование — бакалавриат'),
        ('Высшее образование — специалитет', 'Высшее образование — специалитет'),
        ('Высшее образование — магистратура', 'Высшее образование — магистратура'),
        ('Послевузовское образование', 'Послевузовское образование'),
        ('Дополнительное образование детей', 'Дополнительное образование детей'),
    ]

    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        verbose_name="Пациент",
        related_name='medical_record'
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Пол", blank=True)
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    insurance_policy = models.CharField(max_length=20, verbose_name="Номер полиса")
    snils = models.CharField(max_length=14, verbose_name="СНИЛС")
    passport_series = models.CharField(max_length=4, verbose_name="Серия паспорта")
    passport_number = models.CharField(max_length=6, verbose_name="Номер паспорта")
    education = models.CharField(max_length=100, choices=EDUCATION_CHOICES, verbose_name="Образование")

    def __str__(self):
        return f"Медкарта: {self.patient.full_name}"

    class Meta:
        verbose_name = "Медицинская карта"
        verbose_name_plural = "Медицинские карты"
        app_label = 'CourseWork_app'
        db_table = 'med_records'

class TreatmentRegime(models.Model):
    """Методы лечения"""
    TREATMENT_TYPE_CHOICES = [
        ('Амбулаторный', 'Амбулаторный'),
        ('Стационарный', 'Стационарный'),
    ]

    diagnoses = models.ForeignKey(
        Diagnosis,
        on_delete=models.CASCADE,
        verbose_name="Диагноз",
        related_name='treatment_regimes',
        db_column='diagnoses_id',
    )
    treatment_method = models.CharField(max_length=200, verbose_name="Метод лечения")
    treatment_type = models.CharField(max_length=50, choices=TREATMENT_TYPE_CHOICES, verbose_name="Тип лечения")
    medications = models.TextField(verbose_name="Препараты")
    duration = models.CharField(max_length=100, verbose_name="Длительность")
    effectiveness_control = models.TextField(verbose_name="Контроль эффективности")

    def __str__(self):
        return f"{self.diagnoses.code} - {self.treatment_method}"

    class Meta:
        verbose_name = "Метод лечения"
        verbose_name_plural = "Методы лечения"
        app_label = 'CourseWork_app'
        db_table = 'treatment_regimes'

class Appointment(models.Model):
    """Записи на прием"""
    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        verbose_name="Пациент",
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        verbose_name="Врач",
        related_name='appointments'
    )
    diagnoses = models.ForeignKey(
        Diagnosis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Диагноз",
        related_name='appointments',
        db_column='diagnoses_id'
    )
    symptoms = models.TextField(verbose_name="Симптомы", blank=True)
    appointment_date = models.DateField(verbose_name="Дата приема")
    appointment_time = models.TimeField(verbose_name="Время приема")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")

    class Meta:
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        app_label = 'CourseWork_app'
        db_table = 'appointments'

    def __str__(self):
        return f"{self.patient.full_name} → {self.doctor.full_name} ({self.appointment_date} {self.appointment_time})"