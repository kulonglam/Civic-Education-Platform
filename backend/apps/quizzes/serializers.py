from rest_framework import serializers

from apps.core.utils import get_preferred_language

from .models import Certificate, Question, Quiz, QuizAttempt


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_text_ar', 'question_type',
            'options', 'options_ar', 'points', 'order',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        hide_answers = self.context.get('hide_answers', True)
        if request and get_preferred_language(request) == 'ar' and data.get('question_text_ar'):
            data['question_text'] = data['question_text_ar']
        if hide_answers:
            data.pop('correct_answer', None)
        return data


class QuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_text_ar', 'question_type',
            'options', 'options_ar', 'correct_answer', 'points', 'order',
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'passing_score', 'is_active', 'questions', 'created_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        return data


class QuizWriteSerializer(serializers.ModelSerializer):
    questions = QuestionWriteSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'passing_score', 'is_active', 'questions',
        ]
        read_only_fields = ['id']

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
    answers = serializers.DictField(child=serializers.CharField())


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
