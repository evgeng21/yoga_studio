from django.contrib import admin


from .models import Profile, Client, Course, Schedule, Lesson, Subscription, ClientSubscription


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


class ScheduleInline(admin.TabularInline):  # Или используйте StackedInline
    model = Schedule
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [ScheduleInline]


# @admin.register(Schedule)
# class ScheduleAdmin(admin.ModelAdmin):
#     pass


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientSubscription)
class ClientSubscriptionAdmin(admin.ModelAdmin):
    pass
