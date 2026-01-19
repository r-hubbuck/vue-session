"""
Django signals for expense report email notifications.
Sends automated emails when expense report status changes.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

from .models import ExpenseReport

logger = logging.getLogger(__name__)


def send_expense_report_email(report, email_type):
    """
    Send email notification for expense report status changes.
    
    Args:
        report: ExpenseReport instance
        email_type: 'rejected', 'approved', or 'paid'
    """
    try:
        # Get member's email
        member = report.member
        if not hasattr(member, 'user') or not member.user or not member.user.email:
            logger.warning(f"Cannot send email for report {report.id}: No email address found")
            return
        
        recipient_email = member.user.email
        
        # Prepare common context
        context = {
            'member': member,
            'report_id': report.id,
            'report_type_name': report.report_type.report_name,
            'total_amount': f"{report.total_amount:.2f}",
            'submitted_date': report.created_at.strftime('%B %d, %Y'),
            'domain': getattr(settings, 'SITE_DOMAIN', 'localhost:8000'),
        }
        
        # Set email subject and template based on type
        if email_type == 'rejected':
            subject = f'Expense Report #{report.id} - Rejected'
            template = 'expense_reports/expense_report_rejected_email.html'
            context['rejection_reason'] = report.rejection_reason or 'No reason provided'
            
        elif email_type == 'approved':
            subject = f'Expense Report #{report.id} - Approved'
            template = 'expense_reports/expense_report_approved_email.html'
            context['approval_date'] = report.approval_date.strftime('%B %d, %Y') if report.approval_date else 'N/A'
            
        elif email_type == 'paid':
            subject = f'Expense Report #{report.id} - Payment Issued'
            template = 'expense_reports/expense_report_paid_email.html'
            context['payment_method'] = report.payment_method
            context['payment_method_display'] = report.get_payment_method_display()
            context['payment_check_number'] = report.payment_check_number
            context['payment_payer'] = report.payment_payer
            context['payment_date'] = report.paid_date.strftime('%B %d, %Y') if report.paid_date else 'N/A'
        else:
            logger.error(f"Invalid email type: {email_type}")
            return
        
        # Render HTML email
        html_message = render_to_string(template, context)
        
        # Send email
        send_mail(
            subject=subject,
            message='',  # Plain text version (optional)
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tbp.org'),
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Sent {email_type} email for report {report.id} to {recipient_email}")
        
    except Exception as e:
        logger.error(f"Failed to send {email_type} email for report {report.id}: {str(e)}")


@receiver(pre_save, sender=ExpenseReport)
def store_original_status(sender, instance, **kwargs):
    """
    Store the original status before saving.
    This allows the post_save signal to detect changes.
    """
    if instance.pk:
        try:
            original = ExpenseReport.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except ExpenseReport.DoesNotExist:
            pass


@receiver(post_save, sender=ExpenseReport)
def expense_report_status_changed(sender, instance, created, **kwargs):
    """
    Send email when expense report status changes.
    
    Triggered after every save of an ExpenseReport.
    Tracks the original status using a custom attribute set in pre_save.
    """
    # Don't send emails for newly created reports
    if created:
        return
    
    # Check if we have the original status (set by pre_save signal)
    if not hasattr(instance, '_original_status'):
        return
    
    old_status = instance._original_status
    new_status = instance.status
    
    # Check if status changed
    if old_status != new_status:
        # Send appropriate email based on new status
        if new_status == 'rejected':
            send_expense_report_email(instance, 'rejected')
        elif new_status == 'approved':
            send_expense_report_email(instance, 'approved')
        elif new_status == 'paid':
            send_expense_report_email(instance, 'paid')
