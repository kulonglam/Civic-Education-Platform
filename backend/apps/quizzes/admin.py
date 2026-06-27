from django.contrib import admin

from .models import Certificate, Question, Quiz, QuizAttempt

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizAttempt)
admin.site.register(Certificate)
