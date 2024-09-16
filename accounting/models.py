from datetime import timedelta

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="profile")
    first_name = models.CharField(max_length=30, verbose_name="Имя")
    last_name = models.CharField(max_length=30, verbose_name="Фамилия")
    birthday = models.DateField(verbose_name="Дата рождения")
    experience = models.IntegerField(verbose_name="Год начала работы")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if len(str(self.experience)) != 4:
            raise ValueError('Год должен состоять из 4 цифр')
        super(Profile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class Client(models.Model):
    phone_regex_validator = RegexValidator(
        regex=r'^\+\d{9,15}$',
        message="Формат ввода: '+71234567890'. От 9 до 15 символов.",
    )

    first_name = models.CharField(max_length=30, verbose_name="Имя")
    last_name = models.CharField(max_length=30, verbose_name="Фамилия")
    birthday = models.DateField(verbose_name="Дата рождения")
    phone_number = models.CharField(
        verbose_name='Номер телефона',
        max_length=17,
        unique=False,
        validators=[phone_regex_validator],
        blank=True,
    )
    is_from_club = models.BooleanField(default=True, verbose_name="Привёл клуб")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование")
    teacher = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Преподаватель", related_name="courses")
    description = models.TextField(verbose_name="Описание", blank=True)

    def __str__(self):
        # Получаем все расписания для данного курса
        schedules = self.schedules.all()

        # Словарь для сопоставления номеров дней недели с названиями
        days_mapping = {
            0: 'пн',
            1: 'вт',
            2: 'ср',
            3: 'чт',
            4: 'пт',
            5: 'сб',
            6: 'вс'
        }

        # Список для хранения формата "пн, ср, пт"
        days = {}

        # Собираем дни и времена
        for schedule in schedules:
            day_name = days_mapping[schedule.day_of_week]
            if day_name not in days:
                days[day_name] = []
            days[day_name].append(schedule.start_time.strftime("%H:%M"))

        # Форматируем строку
        days_str = ", ".join(days.keys())
        times_str = ", ".join([f"{time} ({day})" for day, time_list in days.items() for time in time_list])

        return f"{self.name}, {days_str} {times_str}"

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"


class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ])
    start_time = models.TimeField()

    def __str__(self):
        return f'{self.course.name} - {self.get_day_of_week_display()} {self.start_time}'

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name='lessons', null=True, verbose_name='Направление')
    lesson_date = models.DateField(verbose_name="Дата")
    lesson_time = models.TimeField(verbose_name="Время")
    teacher = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, verbose_name="Преподаватель", related_name="lessons")
    clients = models.ManyToManyField(Client, verbose_name="Клиенты", related_name="lessons", blank=True)
    is_conducted = models.BooleanField(default=False, verbose_name="Проведён")

    def __str__(self):
        return f'{self.course.name}, {self.lesson_date} - {self.lesson_time}'

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'


class Subscription(models.Model):
    SUBSCRIPTION_TYPE = (
        ('limited', 'Ограниченный'),
        ('unlimited', 'Безлимитный'),
    )

    name = models.CharField(max_length=100)
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_TYPE)
    duration = models.PositiveIntegerField(help_text="Срок действия в месяцах (0 - бессрочно)")
    num_sessions = models.PositiveIntegerField(help_text="Количество занятий (0 - безлимитный)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", default=0)

    def __str__(self):
        return f"Абонемент: {self.name}, Тип: {self.get_subscription_type_display()}"

    class Meta:
        verbose_name = 'Тип абонемента'
        verbose_name_plural = 'Типы абонементов'


class ClientSubscription(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_subscriptions", verbose_name="Клиент")
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)  # Для ограниченных абонементов
    purchase_date = models.DateField(auto_now_add=True)
    first_used_date = models.DateField(null=True, blank=True)

    @property
    def expiration_date(self):
        if self.subscription.duration > 0:
            return self.first_used_date + timedelta(days=self.subscription.duration)
        return None

    def __str__(self):
        return f'{self.client.first_name} {self.client.last_name}, {self.subscription.name}'

    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'

