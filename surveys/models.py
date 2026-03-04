from django.db import models
from django.conf import settings


SURVEY_TYPE_CHOICES = [
    ('survey', 'Survey'),
    ('questionnaire', 'Questionnaire'),
    ('test', 'Test'),
    ('quiz', 'Quiz'),
    ('assessment', 'Assessment'),
]

AUDIENCE_TYPE_CHOICES = [
    ('open', 'Open'),
    ('role', 'Role'),
    ('user', 'User'),
]

QUESTION_TYPE_CHOICES = [
    ('multiple_choice', 'Multiple Choice'),
    ('checkbox', 'Checkbox'),
    ('true_false', 'True / False'),
    ('yes_no', 'Yes / No'),
    ('short_answer', 'Short Answer'),
    ('essay', 'Essay'),
    ('rating', 'Rating'),
    ('number', 'Number'),
    ('date', 'Date'),
    ('dropdown', 'Dropdown'),
]

CHOICE_QUESTION_TYPES = {'multiple_choice', 'checkbox', 'true_false', 'yes_no', 'dropdown'}


class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    survey_type = models.CharField(max_length=20, choices=SURVEY_TYPE_CHOICES, default='survey')
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    allow_multiple_submissions = models.BooleanField(default=False)
    is_graded = models.BooleanField(default=False)
    passing_score = models.IntegerField(
        null=True, blank=True,
        help_text="Passing percentage (0–100). Only used when is_graded=True."
    )
    open_date = models.DateTimeField(null=True, blank=True, help_text="Null = always open")
    close_date = models.DateTimeField(null=True, blank=True, help_text="Null = no end date")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_surveys'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title


class SurveyAudience(models.Model):
    """
    Defines who can access a survey.
    A survey is accessible to a user when at least one audience row matches them:
    - audience_type='open'  → any authenticated user
    - audience_type='role'  → users with the specified role
    - audience_type='user'  → a specific user
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='audience')
    audience_type = models.CharField(max_length=10, choices=AUDIENCE_TYPE_CHOICES)
    role = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='survey_audience_entries'
    )

    class Meta:
        db_table = 'survey_audience'

    def __str__(self):
        if self.audience_type == 'open':
            return f"{self.survey.title} — open"
        if self.audience_type == 'role':
            return f"{self.survey.title} — role:{self.role}"
        return f"{self.survey.title} — user:{self.user_id}"


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField(default=0)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    is_required = models.BooleanField(default=True)
    help_text = models.CharField(max_length=500, blank=True)
    # Rating scale configuration
    rating_min = models.IntegerField(null=True, blank=True, default=1)
    rating_max = models.IntegerField(null=True, blank=True, default=5)
    rating_min_label = models.CharField(max_length=100, blank=True)
    rating_max_label = models.CharField(max_length=100, blank=True)
    # Grading
    has_correct_answer = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'survey_question'
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:60]}"


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    order = models.PositiveIntegerField(default=0)
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'survey_question_choice'
        ordering = ['order']

    def __str__(self):
        return self.choice_text


class SurveyResponse(models.Model):
    """
    One response session per user per survey (unless allow_multiple_submissions).
    submitted_at=None means the response is still a draft.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='survey_responses'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)
    total_possible_points = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'survey_response'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['survey', 'user']),
            models.Index(fields=['is_complete']),
        ]

    def __str__(self):
        user_label = self.user.email if self.user else 'anonymous'
        return f"Response to '{self.survey.title}' by {user_label}"


class Answer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text_answer = models.TextField(blank=True)
    number_answer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_answer = models.DateField(null=True, blank=True)
    selected_choices = models.ManyToManyField(QuestionChoice, blank=True, related_name='answers')

    class Meta:
        db_table = 'survey_answer'
        unique_together = [('response', 'question')]

    def __str__(self):
        return f"Answer to Q{self.question_id} in response {self.response_id}"
