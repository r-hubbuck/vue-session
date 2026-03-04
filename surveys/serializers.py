import bleach
from django.utils import timezone
from rest_framework import serializers
from django.db import transaction

from .models import (
    Survey, SurveyAudience, Question, QuestionChoice,
    SurveyResponse, Answer, CHOICE_QUESTION_TYPES
)


# ---------------------------------------------------------------------------
# Choice serializers
# ---------------------------------------------------------------------------

class QuestionChoiceSerializer(serializers.ModelSerializer):
    """Staff-facing: includes is_correct for graded surveys."""

    class Meta:
        model = QuestionChoice
        fields = ['id', 'order', 'choice_text', 'is_correct']
        read_only_fields = ['id']

    def validate_choice_text(self, value):
        return bleach.clean(value, tags=[], strip=True)


class QuestionChoicePublicSerializer(serializers.ModelSerializer):
    """Respondent-facing: omits is_correct so answers are not leaked."""

    class Meta:
        model = QuestionChoice
        fields = ['id', 'order', 'choice_text']


# ---------------------------------------------------------------------------
# Question serializers
# ---------------------------------------------------------------------------

class QuestionSerializer(serializers.ModelSerializer):
    """Staff-facing: full question data including correct answer flags."""
    choices = QuestionChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            'id', 'order', 'question_text', 'question_type',
            'is_required', 'help_text',
            'rating_min', 'rating_max', 'rating_min_label', 'rating_max_label',
            'has_correct_answer', 'points', 'choices',
        ]
        read_only_fields = ['id']

    def validate_question_text(self, value):
        return bleach.clean(value, tags=[], strip=True)

    def validate_help_text(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Respondent-facing: hides has_correct_answer and correct choice flags."""
    choices = QuestionChoicePublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'order', 'question_text', 'question_type',
            'is_required', 'help_text',
            'rating_min', 'rating_max', 'rating_min_label', 'rating_max_label',
            'choices',
        ]


# ---------------------------------------------------------------------------
# Audience serializer
# ---------------------------------------------------------------------------

class SurveyAudienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyAudience
        fields = ['id', 'audience_type', 'role', 'user']
        read_only_fields = ['id']


# ---------------------------------------------------------------------------
# Survey list serializer
# ---------------------------------------------------------------------------

class SurveyListSerializer(serializers.ModelSerializer):
    survey_type_display = serializers.CharField(source='get_survey_type_display', read_only=True)
    response_status = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'survey_type', 'survey_type_display',
            'is_active', 'is_graded', 'open_date', 'close_date',
            'is_open_now', 'response_status', 'response_count',
        ]

    def _is_open(self, obj):
        now = timezone.now()
        if obj.open_date and now < obj.open_date:
            return False
        if obj.close_date and now > obj.close_date:
            return False
        return True

    def get_is_open_now(self, obj):
        return self._is_open(obj)

    def get_response_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 'not_started'
        response = obj.responses.filter(user=request.user).order_by('-started_at').first()
        if not response:
            return 'not_started'
        return 'completed' if response.is_complete else 'in_progress'

    def get_response_count(self, obj):
        if self.context.get('is_staff'):
            return obj.responses.count()
        return None


# ---------------------------------------------------------------------------
# Survey detail serializers
# ---------------------------------------------------------------------------

class SurveyDetailPublicSerializer(serializers.ModelSerializer):
    """Respondent-facing detail: full question list without correct answers."""
    questions = QuestionPublicSerializer(many=True, read_only=True)
    survey_type_display = serializers.CharField(source='get_survey_type_display', read_only=True)
    is_open_now = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'survey_type', 'survey_type_display',
            'is_active', 'is_graded', 'is_anonymous', 'allow_multiple_submissions',
            'open_date', 'close_date', 'is_open_now', 'questions',
        ]

    def get_is_open_now(self, obj):
        now = timezone.now()
        if obj.open_date and now < obj.open_date:
            return False
        if obj.close_date and now > obj.close_date:
            return False
        return True


class SurveyDetailStaffSerializer(serializers.ModelSerializer):
    """Staff-facing detail: full question list including correct answers and audience."""
    questions = QuestionSerializer(many=True, read_only=True)
    audience = SurveyAudienceSerializer(many=True, read_only=True)
    created_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'survey_type', 'is_active',
            'is_anonymous', 'allow_multiple_submissions', 'is_graded',
            'passing_score', 'open_date', 'close_date',
            'created_by_email', 'created_at', 'updated_at',
            'questions', 'audience',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_email']

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else None


# ---------------------------------------------------------------------------
# Survey create/update serializer
# ---------------------------------------------------------------------------

class SurveyCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Handles nested write operations for questions and audience.
    Replaces all questions (and choices) and audience rows on update.
    """
    questions = QuestionSerializer(many=True, required=False)
    audience = SurveyAudienceSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'survey_type', 'is_active',
            'is_anonymous', 'allow_multiple_submissions', 'is_graded',
            'passing_score', 'open_date', 'close_date',
            'questions', 'audience',
        ]

    def validate_title(self, value):
        return bleach.clean(value, tags=[], strip=True)

    def validate_description(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value

    def validate_passing_score(self, value):
        if value is not None and not (0 <= value <= 100):
            raise serializers.ValidationError('Passing score must be between 0 and 100.')
        return value

    def _sync_questions(self, survey, questions_data):
        """Delete all existing questions and recreate from payload."""
        survey.questions.all().delete()
        for q_data in questions_data:
            choices_data = q_data.pop('choices', [])
            question = Question.objects.create(survey=survey, **q_data)
            # Auto-populate choices for true_false and yes_no if none provided
            if question.question_type == 'true_false' and not choices_data:
                choices_data = [
                    {'order': 0, 'choice_text': 'True', 'is_correct': False},
                    {'order': 1, 'choice_text': 'False', 'is_correct': False},
                ]
            elif question.question_type == 'yes_no' and not choices_data:
                choices_data = [
                    {'order': 0, 'choice_text': 'Yes', 'is_correct': False},
                    {'order': 1, 'choice_text': 'No', 'is_correct': False},
                ]
            for c_data in choices_data:
                QuestionChoice.objects.create(question=question, **c_data)

    def _sync_audience(self, survey, audience_data):
        """Delete all existing audience rows and recreate from payload."""
        survey.audience.all().delete()
        for a_data in audience_data:
            SurveyAudience.objects.create(survey=survey, **a_data)

    @transaction.atomic
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        audience_data = validated_data.pop('audience', [])
        survey = Survey.objects.create(**validated_data)
        self._sync_questions(survey, questions_data)
        self._sync_audience(survey, audience_data)
        return survey

    @transaction.atomic
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        audience_data = validated_data.pop('audience', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions_data is not None:
            self._sync_questions(instance, questions_data)
        if audience_data is not None:
            self._sync_audience(instance, audience_data)
        return instance


# ---------------------------------------------------------------------------
# Answer / response serializers
# ---------------------------------------------------------------------------

class AnswerSerializer(serializers.ModelSerializer):
    selected_choices = serializers.PrimaryKeyRelatedField(
        many=True, queryset=QuestionChoice.objects.all(), required=False
    )

    class Meta:
        model = Answer
        fields = ['id', 'question', 'text_answer', 'number_answer', 'date_answer', 'selected_choices']
        read_only_fields = ['id']

    def validate_text_answer(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value


class SurveyResponseSerializer(serializers.ModelSerializer):
    """Read-only serializer for returning a full response (draft or submitted)."""
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'survey', 'started_at', 'submitted_at',
            'is_complete', 'score', 'total_possible_points', 'answers',
        ]
        read_only_fields = [
            'id', 'survey', 'started_at', 'submitted_at',
            'is_complete', 'score', 'total_possible_points',
        ]


class SaveAnswersSerializer(serializers.Serializer):
    """Input wrapper for the draft-save and submit endpoints."""
    answers = AnswerSerializer(many=True)


# ---------------------------------------------------------------------------
# Staff results serializer
# ---------------------------------------------------------------------------

class SurveyResultsResponseSerializer(serializers.ModelSerializer):
    """Individual response row for staff results view."""
    user_email = serializers.SerializerMethodField()
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'user_email', 'started_at', 'submitted_at',
            'is_complete', 'score', 'total_possible_points', 'answers',
        ]

    def get_user_email(self, obj):
        return obj.user.email if obj.user else 'Anonymous'
