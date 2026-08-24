from rest_framework import serializers

from apps.core.utils import get_preferred_language

from .models import Certificate, Question, Quiz, QuizAttempt


HIDDEN_LEARNER_FIELDS = ('correct_answer', 'explanation', 'explanation_ar', 'option_feedback')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_text_ar', 'question_type',
            'options', 'options_ar', 'correct_answer', 'explanation',
            'explanation_ar', 'option_feedback', 'points', 'order',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        hide_answers = self.context.get('hide_answers', True)
        if request and get_preferred_language(request) == 'ar' and data.get('question_text_ar'):
            data['question_text'] = data['question_text_ar']
        if hide_answers:
            for field in HIDDEN_LEARNER_FIELDS:
                data.pop(field, None)
        return data


class QuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_text_ar', 'question_type',
            'options', 'options_ar', 'correct_answer', 'explanation',
            'explanation_ar', 'option_feedback', 'points', 'order',
        ]


QUIZ_PUBLIC_FIELDS = [
    'id', 'title', 'title_ar', 'description', 'description_ar',
    'passing_score', 'kind', 'feedback_mode', 'max_attempts',
    'issues_certificate', 'is_active', 'question_count', 'created_at',
]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    issues_certificate = serializers.BooleanField(read_only=True)

    class Meta:
        model = Quiz
        fields = QUIZ_PUBLIC_FIELDS + ['questions']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        if data.get('question_count') is None:
            data['question_count'] = instance.questions.count()
        return data


class QuizListSerializer(QuizSerializer):
    """Public catalog card — titles and counts, not question bodies."""

    class Meta(QuizSerializer.Meta):
        fields = QUIZ_PUBLIC_FIELDS


class QuizWriteSerializer(serializers.ModelSerializer):
    questions = QuestionWriteSerializer(many=True, required=False)
    max_attempts = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'passing_score', 'kind', 'feedback_mode', 'max_attempts', 'is_active',
            'questions',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        kind = attrs.get('kind', getattr(self.instance, 'kind', Quiz.KIND_ASSESSMENT))
        feedback_mode = attrs.get(
            'feedback_mode',
            getattr(self.instance, 'feedback_mode', Quiz.FEEDBACK_END),
        )
        if kind == Quiz.KIND_ASSESSMENT and feedback_mode == Quiz.FEEDBACK_PER_QUESTION:
            attrs['feedback_mode'] = Quiz.FEEDBACK_END
        return attrs

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        validated_data['created_by'] = self.context['request'].user
        quiz = Quiz.objects.create(**validated_data)
        for q_data in questions_data:
            Question.objects.create(quiz=quiz, **q_data)
        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions_data is not None:
            instance.questions.all().delete()
            for q_data in questions_data:
                Question.objects.create(quiz=instance, **q_data)
        return instance


class QuizAttemptSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(child=serializers.CharField(allow_blank=True))


class QuizCheckAnswerSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    answer = serializers.CharField(allow_blank=True)


class QuizReviewItemSerializer(serializers.Serializer):
    question_id = serializers.CharField()
    question_type = serializers.CharField()
    question_text = serializers.CharField()
    learner_answer = serializers.CharField(allow_blank=True)
    correct_answer = serializers.CharField()
    is_correct = serializers.BooleanField()
    points = serializers.IntegerField()
    points_awarded = serializers.IntegerField()
    explanation = serializers.CharField(allow_blank=True)


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'score', 'max_score',
            'passed', 'attempted_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            quiz = instance.quiz
            if quiz.title_ar:
                data['quiz_title'] = quiz.title_ar
        return data


class CertificateSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'quiz', 'quiz_title',
            'issue_date', 'pdf_url',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            quiz = instance.quiz
            if quiz.title_ar:
                data['quiz_title'] = quiz.title_ar
        return data
