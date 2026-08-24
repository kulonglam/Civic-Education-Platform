import uuid

from django.conf import settings
from django.db import models

from apps.tenants.models import TenantModel


class Quiz(TenantModel):
    KIND_PRACTICE = 'practice'
    KIND_ASSESSMENT = 'assessment'
    KIND_CHOICES = [
        (KIND_PRACTICE, 'Practice'),
        (KIND_ASSESSMENT, 'Final assessment'),
    ]
    FEEDBACK_END = 'end'
    FEEDBACK_PER_QUESTION = 'per_question'
    FEEDBACK_CHOICES = [
        (FEEDBACK_END, 'After submit'),
        (FEEDBACK_PER_QUESTION, 'After each question'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_ASSESSMENT)
    feedback_mode = models.CharField(
        max_length=20,
        choices=FEEDBACK_CHOICES,
        default=FEEDBACK_END,
    )
    max_attempts = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Blank means unlimited attempts.',
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='quizzes_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quizzes'
        verbose_name_plural = 'quizzes'
        ordering = ['-created_at']

    @property
    def issues_certificate(self):
        return self.kind == self.KIND_ASSESSMENT

    def __str__(self):
        return self.title


class Question(models.Model):
    MCQ = 'mcq'
    TRUE_FALSE = 'true_false'
    SCENARIO = 'scenario'
    TYPE_CHOICES = [
        (MCQ, 'Multiple Choice'),
        (TRUE_FALSE, 'True/False'),
        (SCENARIO, 'Scenario'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_text_ar = models.TextField(blank=True)
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=MCQ)
    options = models.JSONField(default=list, blank=True)
    options_ar = models.JSONField(default=list, blank=True)
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)
    explanation_ar = models.TextField(blank=True)
    option_feedback = models.JSONField(
        default=list,
        blank=True,
        help_text='Per-option teaching notes: list of {en, ar} aligned with options.',
    )
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'questions'
        ordering = ['order']

    def __str__(self):
        return self.question_text[:50]


class QuizAttempt(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
    )
    answers = models.JSONField(default=dict)
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-attempted_at']

    def __str__(self):
        return f'{self.user.email} - {self.quiz.title} ({self.score})'


class Certificate(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_number = models.CharField(max_length=50, unique=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='certificates')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    attempt = models.OneToOneField(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='certificate',
        null=True,
        blank=True,
    )
    issue_date = models.DateField(auto_now_add=True)
    pdf_url = models.URLField(blank=True)

    class Meta:
        db_table = 'certificates'
        ordering = ['-issue_date']

    def __str__(self):
        return self.certificate_number
