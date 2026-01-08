from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import ExpenseReportType, ExpenseReport, ExpenseReportDetail
from .serializers import (
    ExpenseReportTypeSerializer,
    ExpenseReportListSerializer,
    ExpenseReportDetailedSerializer,
    ExpenseReportCreateSerializer,
    ExpenseReportUpdateSerializer,
    ExpenseReportStaffUpdateSerializer,
)
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_report_types_list(request):
    """
    Get list of available expense report types.
    Only returns implemented types.
    """
    report_types = ExpenseReportType.objects.filter(implemented=True)
    serializer = ExpenseReportTypeSerializer(report_types, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_expense_reports(request):
    """
    GET: List all expense reports for the current user.
    POST: Create a new expense report.
    """
    member = request.user.member
    
    if not member:
        return Response(
            {'error': 'User does not have an associated member record'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'GET':
        # Get user's expense reports
        reports = ExpenseReport.objects.filter(member=member).select_related(
            'report_type',
            'reviewer',
            'approver'
        ).prefetch_related('details')
        
        serializer = ExpenseReportListSerializer(reports, many=True)
        
        logger.info(
            f"User {request.user.email} retrieved their expense reports",
            extra={
                'user_id': request.user.id,
                'member_id': member.id,
                'report_count': reports.count()
            }
        )
        
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create new expense report
        serializer = ExpenseReportCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save with current member
            expense_report = serializer.save(
                member=member,
                status='draft'
            )
            
            logger.info(
                f"User {request.user.email} created expense report",
                extra={
                    'user_id': request.user.id,
                    'member_id': member.id,
                    'report_id': expense_report.id,
                    'report_type': expense_report.report_type.report_code,
                    'total_amount': str(expense_report.total_amount)
                }
            )
            
            # Return detailed view
            detail_serializer = ExpenseReportDetailedSerializer(expense_report)
            return Response(
                detail_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def expense_report_detail(request, report_id):
    """
    GET: Retrieve a specific expense report.
    PUT: Update an expense report (member can only update their own drafts).
    DELETE: Delete an expense report (member can only delete their own drafts).
    """
    member = request.user.member
    
    if not member:
        return Response(
            {'error': 'User does not have an associated member record'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the report
    expense_report = get_object_or_404(ExpenseReport, id=report_id)
    
    # Check ownership
    if expense_report.member != member:
        return Response(
            {'error': 'You do not have permission to access this report'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        serializer = ExpenseReportDetailedSerializer(expense_report)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Can only edit drafts
        if expense_report.status != 'draft':
            return Response(
                {'error': 'Only draft reports can be edited'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ExpenseReportUpdateSerializer(
            expense_report,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            updated_report = serializer.save()
            
            logger.info(
                f"User {request.user.email} updated expense report {report_id}",
                extra={
                    'user_id': request.user.id,
                    'member_id': member.id,
                    'report_id': report_id
                }
            )
            
            detail_serializer = ExpenseReportDetailedSerializer(updated_report)
            return Response(detail_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Can only delete drafts
        if expense_report.status != 'draft':
            return Response(
                {'error': 'Only draft reports can be deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(
            f"User {request.user.email} deleted expense report {report_id}",
            extra={
                'user_id': request.user.id,
                'member_id': member.id,
                'report_id': report_id
            }
        )
        
        expense_report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_expense_report(request, report_id):
    """
    Submit an expense report (change status from draft to submitted).
    """
    member = request.user.member
    
    if not member:
        return Response(
            {'error': 'User does not have an associated member record'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    expense_report = get_object_or_404(ExpenseReport, id=report_id)
    
    # Check ownership
    if expense_report.member != member:
        return Response(
            {'error': 'You do not have permission to submit this report'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Can only submit drafts
    if expense_report.status != 'draft':
        return Response(
            {'error': 'Only draft reports can be submitted'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Change status to submitted
    expense_report.status = 'submitted'
    expense_report.save()
    
    logger.info(
        f"User {request.user.email} submitted expense report {report_id}",
        extra={
            'user_id': request.user.id,
            'member_id': member.id,
            'report_id': report_id,
            'total_amount': str(expense_report.total_amount)
        }
    )
    
    serializer = ExpenseReportDetailedSerializer(expense_report)
    return Response(serializer.data)


# Staff/Admin endpoints (no authorization yet, but structured for future)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_expense_reports(request):
    """
    Get all expense reports (for staff review).
    In the future, this should be restricted to staff only.
    """
    # Filter by status if provided
    status_filter = request.query_params.get('status')
    
    reports = ExpenseReport.objects.select_related(
        'member',
        'report_type',
        'reviewer',
        'approver'
    ).prefetch_related('details')
    
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    serializer = ExpenseReportListSerializer(reports, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def staff_expense_report_detail(request, report_id):
    """
    Staff view/update of expense report.
    GET: View any expense report.
    PUT: Update status, review, payment information.
    """
    expense_report = get_object_or_404(
        ExpenseReport.objects.select_related(
            'member',
            'report_type',
            'reviewer',
            'approver'
        ).prefetch_related('details'),
        id=report_id
    )
    
    if request.method == 'GET':
        serializer = ExpenseReportDetailedSerializer(expense_report)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ExpenseReportStaffUpdateSerializer(
            expense_report,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            updated_report = serializer.save()
            
            logger.info(
                f"Staff {request.user.email} updated expense report {report_id}",
                extra={
                    'user_id': request.user.id,
                    'report_id': report_id,
                    'new_status': updated_report.status
                }
            )
            
            detail_serializer = ExpenseReportDetailedSerializer(updated_report)
            return Response(detail_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
