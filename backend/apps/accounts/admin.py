from django.contrib import admin

from .models import EmailVerificationToken, Role, User, UserProfile

admin.site.register(Role)
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(EmailVerificationToken)
