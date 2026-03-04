from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Survey, SurveyResponse, Answer, Question, CHOICE_QUESTION_TYPES
from .serializers import (
    SurveyListSerializer,
    SurveyDetailPublicSerializer,
    SurveyDetailStaffSerializer,
    SurveyCreateUpdateSerializer,
    SurveyResponseSerializer,
    SaveAnswersSerializer,
    SurveyResultsResponseSerializer,
)

SURVEY_CREATOR_ROLES = ['hq_staff', 'hq_it', 'hq_admin', 'hq_finance', 'executive_council']


def _is_survey_creator(user):
    return any(user.has_role(r) for r in SURVEY_CREATOR_ROLES)


def _user_can_see_survey(user, survey):
    """Return True if the user meets at least one audience rule for this survey."""
    if not survey.is_active:
        return False
    now = timezone.now()
    if survey.open_date and now < survey.open_date:
        return False
    if survey.close_date and now > survey.close_date:
        return False
    for a in survey.audience.all():
        if a.audience_type == 'open':
            return True
        if a.audience_type == 'role' and a.role and user.has_role(a.role):
            return True
        if a.audience_type == 'user' and a.user_id == user.pk:
            return True
    return False


def _save_answers(response, answers_data):
    """
    Upsert answers for a response.
    For each item in answers_data, create or update the Answer row,
    then set the M2M selected_choices.
    """
    for ans in answers_data:
        question = ans['question']
        choices = ans.pop('selected_choices', [])
        answer_obj, _ = Answer.objects.update_or_create(
            response=response,
            question=question,
            defaults={
                'text_answer': ans.get('text_answer', ''),
                'number_answer': ans.get('number_answer'),
                'date_answer': ans.get('date_answer'),
            }
        )
        answer_obj.selected_choices.set(choices)


# ---------------------------------------------------------------------------
# User-facing views
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def survey_list(request):
    """List all surveys the current user is allowed to see."""
    surveys = Survey.objects.prefetch_related('audience', 'responses').filter(is_active=True)
    visible = [s for s in surveys if _user_can_see_survey(request.user, s)]
    serializer = SurveyListSerializer(visible, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def survey_detail(request, survey_id):
    """Get full survey with questions (no correct answers) for a respondent."""
    survey = get_object_or_404(Survey, pk=survey_id)
    if not _user_can_see_survey(request.user, survey):
        return Response({'error': 'You do not have access to this survey.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = SurveyDetailPublicSerializer(survey)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_response(request, survey_id):
    """Get the current user's most recent response for this survey (draft or submitted)."""
    survey = get_object_or_404(Survey, pk=survey_id)
    if not _user_can_see_survey(request.user, survey):
        return Response({'error': 'You do not have access to this survey.'}, status=status.HTTP_403_FORBIDDEN)
    response = (
        SurveyResponse.objects
        .filter(survey=survey, user=request.user)
        .prefetch_related('answers__selected_choices')
        .order_by('-started_at')
        .first()
    )
    if not response:
        return Response({'response': None})
    return Response({'response': SurveyResponseSerializer(response).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def start_survey(request, survey_id):
    """Create a new SurveyResponse (draft). Enforces single-submission rule."""
    survey = get_object_or_404(Survey, pk=survey_id)
    if not _user_can_see_survey(request.user, survey):
        return Response({'error': 'You do not have access to this survey.'}, status=status.HTTP_403_FORBIDDEN)

    if not survey.allow_multiple_submissions:
        existing = SurveyResponse.objects.filter(survey=survey, user=request.user, is_complete=True).first()
        if existing:
            return Response(
                {'error': 'You have already submitted this survey.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    user = None if survey.is_anonymous else request.user
    survey_response = SurveyResponse.objects.create(survey=survey, user=user)
    return Response({'response_id': survey_response.id}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def save_draft(request, survey_id, response_id):
    """Save partial answers to an in-progress response."""
    survey = get_object_or_404(Survey, pk=survey_id)
    survey_response = get_object_or_404(SurveyResponse, pk=response_id, survey=survey)

    if survey_response.user != request.user and not survey.is_anonymous:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    if survey_response.is_complete:
        return Response({'error': 'Survey already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SaveAnswersSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    _save_answers(survey_response, serializer.validated_data['answers'])
    survey_response.refresh_from_db()
    return Response(
        SurveyResponseSerializer(
            SurveyResponse.objects.prefetch_related('answers__selected_choices').get(pk=survey_response.pk)
        ).data
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_survey(request, survey_id, response_id):
    """
    Finalize a response:
    1. Save any last answers from the request body.
    2. Validate all required questions are answered.
    3. Score the submission if the survey is graded.
    4. Mark the response as complete.
    """
    survey = get_object_or_404(Survey, pk=survey_id)
    survey_response = get_object_or_404(SurveyResponse, pk=response_id, survey=survey)

    if survey_response.user != request.user and not survey.is_anonymous:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    if survey_response.is_complete:
        return Response({'error': 'Survey already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

    # Save any final answers included in the request
    if request.data.get('answers'):
        serializer = SaveAnswersSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        _save_answers(survey_response, serializer.validated_data['answers'])

    # Validate required questions
    required_question_ids = set(
        survey.questions.filter(is_required=True).values_list('id', flat=True)
    )
    answered_question_ids = set(
        survey_response.answers.values_list('question_id', flat=True)
    )
    missing = required_question_ids - answered_question_ids
    if missing:
        return Response(
            {'error': 'Please answer all required questions.', 'missing_question_ids': list(missing)},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Score if graded
    score = None
    total_possible = None
    if survey.is_graded:
        score = 0
        total_possible = 0
        for question in survey.questions.prefetch_related('choices').filter(has_correct_answer=True):
            total_possible += question.points
            try:
                answer = survey_response.answers.prefetch_related('selected_choices').get(question=question)
            except Answer.DoesNotExist:
                continue

            q_type = question.question_type
            if q_type in ('multiple_choice', 'true_false', 'yes_no', 'dropdown'):
                selected = list(answer.selected_choices.all())
                if len(selected) == 1 and selected[0].is_correct:
                    score += question.points
            elif q_type == 'checkbox':
                selected_ids = set(answer.selected_choices.values_list('id', flat=True))
                correct_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
                if selected_ids == correct_ids:
                    score += question.points
            # short_answer, essay, number, date, rating: not auto-scored

    survey_response.score = score
    survey_response.total_possible_points = total_possible
    survey_response.submitted_at = timezone.now()
    survey_response.is_complete = True
    survey_response.save()

    return Response(
        SurveyResponseSerializer(
            SurveyResponse.objects.prefetch_related('answers__selected_choices').get(pk=survey_response.pk)
        ).data
    )


# ---------------------------------------------------------------------------
# Staff views
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_survey_list(request):
    """
    GET  — list all surveys (active and inactive) with response counts.
    POST — create a new survey with nested questions and audience.
    """
    if not _is_survey_creator(request.user):
        return Response({'error': 'You do not have permission to manage surveys.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        surveys = Survey.objects.prefetch_related('audience', 'responses').all()
        serializer = SurveyListSerializer(
            surveys, many=True, context={'request': request, 'is_staff': True}
        )
        return Response(serializer.data)

    # POST — create
    serializer = SurveyCreateUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    survey = serializer.save(created_by=request.user)
    return Response(
        SurveyDetailStaffSerializer(survey).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_survey_detail(request, survey_id):
    """
    GET    — full survey detail with correct answers and audience.
    PUT    — replace survey metadata, questions, and/or audience.
    DELETE — soft-delete (is_active=False) to preserve response data.
    """
    if not _is_survey_creator(request.user):
        return Response({'error': 'You do not have permission to manage surveys.'}, status=status.HTTP_403_FORBIDDEN)

    survey = get_object_or_404(Survey, pk=survey_id)

    if request.method == 'GET':
        serializer = SurveyDetailStaffSerializer(survey)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = SurveyCreateUpdateSerializer(survey, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated_survey = serializer.save()
        return Response(SurveyDetailStaffSerializer(updated_survey).data)

    # DELETE — soft delete
    survey.is_active = False
    survey.save(update_fields=['is_active'])
    return Response({'message': 'Survey deactivated.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_survey_results(request, survey_id):
    """
    Return aggregated per-question stats and individual response data for staff.
    """
    if not _is_survey_creator(request.user):
        return Response({'error': 'You do not have permission to view survey results.'}, status=status.HTTP_403_FORBIDDEN)

    survey = get_object_or_404(Survey, pk=survey_id)
    responses = (
        SurveyResponse.objects
        .filter(survey=survey)
        .prefetch_related('answers__selected_choices', 'answers__question')
        .select_related('user')
    )

    # Build per-question stats
    question_stats = []
    for question in survey.questions.prefetch_related('choices').all():
        q_type = question.question_type
        stat = {
            'question_id': question.id,
            'question_text': question.question_text,
            'question_type': q_type,
            'stats': {},
        }

        if q_type in CHOICE_QUESTION_TYPES:
            # Count responses per choice
            choice_counts = {}
            for choice in question.choices.all():
                choice_counts[choice.id] = {
                    'choice_text': choice.choice_text,
                    'count': 0,
                    'is_correct': choice.is_correct,
                }
            for resp in responses:
                for ans in resp.answers.all():
                    if ans.question_id == question.id:
                        for choice in ans.selected_choices.all():
                            if choice.id in choice_counts:
                                choice_counts[choice.id]['count'] += 1
            total_answers = sum(c['count'] for c in choice_counts.values())
            for c in choice_counts.values():
                c['percentage'] = round(c['count'] / total_answers * 100, 1) if total_answers else 0
            stat['stats'] = {'choices': list(choice_counts.values()), 'total_answers': total_answers}

        elif q_type in ('short_answer', 'essay'):
            texts = []
            for resp in responses:
                for ans in resp.answers.all():
                    if ans.question_id == question.id and ans.text_answer:
                        texts.append(ans.text_answer)
            stat['stats'] = {'responses': texts, 'count': len(texts)}

        elif q_type in ('number', 'rating'):
            numbers = []
            for resp in responses:
                for ans in resp.answers.all():
                    if ans.question_id == question.id and ans.number_answer is not None:
                        numbers.append(float(ans.number_answer))
            if numbers:
                stat['stats'] = {
                    'min': min(numbers),
                    'max': max(numbers),
                    'avg': round(sum(numbers) / len(numbers), 2),
                    'count': len(numbers),
                }
            else:
                stat['stats'] = {'min': None, 'max': None, 'avg': None, 'count': 0}

        elif q_type == 'date':
            dates = []
            for resp in responses:
                for ans in resp.answers.all():
                    if ans.question_id == question.id and ans.date_answer:
                        dates.append(str(ans.date_answer))
            stat['stats'] = {'dates': sorted(dates), 'count': len(dates)}

        question_stats.append(stat)

    # Score summary for graded surveys
    score_summary = None
    if survey.is_graded:
        scored_responses = [r for r in responses if r.is_complete and r.score is not None]
        if scored_responses:
            scores = [r.score for r in scored_responses]
            passing = [
                r for r in scored_responses
                if survey.passing_score is not None
                and r.total_possible_points
                and (r.score / r.total_possible_points * 100) >= survey.passing_score
            ]
            score_summary = {
                'avg_score': round(sum(scores) / len(scores), 2),
                'min_score': min(scores),
                'max_score': max(scores),
                'pass_count': len(passing),
                'total_graded': len(scored_responses),
                'pass_rate': round(len(passing) / len(scored_responses) * 100, 1) if scored_responses else 0,
            }

    survey_data = SurveyListSerializer(survey, context={'request': request, 'is_staff': True}).data
    individual_data = SurveyResultsResponseSerializer(responses, many=True).data

    return Response({
        'survey': survey_data,
        'question_stats': question_stats,
        'individual_responses': individual_data,
        'score_summary': score_summary,
    })
