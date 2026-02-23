from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone

from django.db import transaction, IntegrityError

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from accounts.throttles import RegisterThrottle, RecruiterThrottle

from accounts.models import User, Code, ROLE_RECRUITER
from accounts.tokens import account_activation_token
from convention.models import Convention, ConventionRegistration
from .models import (
    BoothPackage, MealOption, Organization, RecruiterProfile,
    RecruiterRegistration, Invoice
)
from .serializers import (
    RecruiterRegistrationSerializer, RecruiterProfileSerializer,
    BoothPackageSerializer, MealOptionSerializer,
    RecruiterConventionRegistrationSerializer,
    AdminRecruiterRegistrationSerializer,
    AttendeeSerializer, InvoiceSerializer, RecruiterInvoiceSerializer,
    OrganizationSerializer
)

FRONTEND_URL = settings.FRONTEND_URL
DOMAIN = settings.DOMAIN


# ============================================================
# Helper: Check recruiter role
# ============================================================

def is_recruiter(user):
    return user.user_type == 'recruiter'


def is_approved_recruiter(user):
    return (
        is_recruiter(user) and
        hasattr(user, 'recruiter_profile') and
        user.recruiter_profile.is_approved
    )


def is_staff_or_admin(user):
    return user.has_role('hq_staff') or user.has_role('hq_admin')


def is_staff_or_finance(user):
    return user.has_role('hq_staff') or user.has_role('hq_finance') or user.has_role('hq_admin')


def get_active_convention():
    return Convention.objects.filter(is_active=True).first()


# ============================================================
# Recruiter Self-Registration
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterThrottle])
def recruiter_register(request):
    """Register a new recruiter with organization info."""
    serializer = RecruiterRegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Check for existing inactive user
    existing_user = User.objects.filter(email=data['email'], is_active=False).first()
    if existing_user:
        user = existing_user
        user.set_password(data['password1'])
        user.user_type = 'recruiter'
        user.is_active = False
        user.last_login = timezone.now()
        user.save()
        # Update or create Code
        if hasattr(user, 'code'):
            user.code.save()
        else:
            Code.objects.create(user=user)
    else:
        user = User(email=data['email'], is_active=False, user_type='recruiter')
        user.set_password(data['password1'])
        user.save()

    # Create or link organization
    org, created = Organization.objects.get_or_create(
        name=data['org_name'],
        defaults={
            'org_type': data['org_type'],
            'website': data.get('org_website', ''),
            'address_line1': data['org_address_line1'],
            'address_line2': data.get('org_address_line2', ''),
            'city': data['org_city'],
            'state': data.get('org_state', ''),
            'zip_code': data.get('org_zip_code', ''),
            'country': data.get('org_country', 'United States'),
            'phone': data.get('org_phone', ''),
            'billing_email': data['org_billing_email'],
            'billing_contact_first_name': data['org_billing_contact_first_name'],
            'billing_contact_last_name': data['org_billing_contact_last_name'],
            'num_recruiters': data.get('org_num_recruiters', 1),
        }
    )

    # If org already existed, block self-registration if it has approved recruiters
    # from other users. Prevents unauthorized org association.
    if not created:
        other_approved = RecruiterProfile.objects.filter(
            organization=org,
            is_approved=True,
        ).exclude(user=user).exists()
        if other_approved:
            return Response(
                {'error': 'This organization already has registered recruiters. '
                          'Please contact us to be added to an existing organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Create RecruiterProfile
    RecruiterProfile.objects.update_or_create(
        user=user,
        defaults={
            'organization': org,
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'cell_phone': data.get('cell_phone', ''),
            'is_approved': False,
        }
    )

    # Assign recruiter role
    user.add_role(ROLE_RECRUITER)

    # Send activation email
    try:
        mail_subject = 'Activate Your Recruiter Account'
        message = render_to_string('registration/account_activation_email.html', {
            'member': None,
            'domain': DOMAIN,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })
        email_msg = EmailMultiAlternatives(
            subject=mail_subject,
            body='',
            to=[user.email]
        )
        email_msg.attach_alternative(message, "text/html")
        email_msg.send()
    except Exception as e:
        print(f"Failed to send recruiter activation email: {e}")

    return Response(
        {'success': 'Recruiter account created. Please check your email to activate.'},
        status=status.HTTP_201_CREATED
    )


# ============================================================
# Recruiter Profile
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recruiter_profile_view(request):
    """Get the current recruiter's profile."""
    if not is_recruiter(request.user):
        return Response({'error': 'Not a recruiter account.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Recruiter profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RecruiterProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_organization(request):
    """Update the current recruiter's organization info."""
    if not is_recruiter(request.user):
        return Response({'error': 'Not a recruiter account.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Recruiter profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    org = profile.organization
    serializer = OrganizationSerializer(org, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data)


# ============================================================
# Admin: Approve Recruiters
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_pending_recruiters(request):
    """List unapproved recruiter profiles."""
    if not is_staff_or_admin(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    profiles = RecruiterProfile.objects.filter(
        is_approved=False, user__is_active=True
    ).select_related('organization', 'user')

    paginator = AdminPagination()
    page = paginator.paginate_queryset(profiles, request)
    serializer = RecruiterProfileSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_approve_recruiter(request, pk):
    """Approve a recruiter profile."""
    if not is_staff_or_admin(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = RecruiterProfile.objects.select_related('user').get(pk=pk)
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    profile.is_approved = True
    profile.save()

    # Send approval notification email
    try:
        mail_subject = 'Your Recruiter Account Has Been Approved'
        message = render_to_string('recruiters/approval_email.html', {
            'profile': profile,
            'frontend_url': FRONTEND_URL,
        })
        email_msg = EmailMultiAlternatives(
            subject=mail_subject,
            body='',
            to=[profile.email]
        )
        email_msg.attach_alternative(message, "text/html")
        email_msg.send()
    except Exception as e:
        print(f"Failed to send approval email: {e}")

    return Response({'success': 'Recruiter approved.'})


# ============================================================
# Booth Packages & Meal Options
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booth_packages(request):
    """List active booth packages for current convention."""
    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_404_NOT_FOUND)

    packages = BoothPackage.objects.filter(convention=convention, is_active=True)
    serializer = BoothPackageSerializer(packages, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meal_options(request):
    """List active meal options for current convention."""
    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_404_NOT_FOUND)

    options = MealOption.objects.filter(convention=convention, is_active=True)
    serializer = MealOptionSerializer(options, many=True)
    return Response(serializer.data)


# ============================================================
# Recruiter Convention Registration
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recruiter_convention_register(request):
    """Register recruiter for the current convention."""
    if not is_approved_recruiter(request.user):
        return Response(
            {'error': 'You must be an approved recruiter to register.'},
            status=status.HTTP_403_FORBIDDEN
        )

    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RecruiterConventionRegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # Lock the profile row to prevent race conditions on approval status
            profile = RecruiterProfile.objects.select_for_update().get(user=request.user)

            # Re-check approval inside the lock in case it was revoked concurrently
            if not profile.is_approved:
                return Response(
                    {'error': 'You must be an approved recruiter to register.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if RecruiterRegistration.objects.filter(recruiter=profile, convention=convention).exists():
                return Response(
                    {'error': 'You are already registered for this convention.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(recruiter=profile, convention=convention, status='pending')
    except IntegrityError:
        return Response(
            {'error': 'You are already registered for this convention.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def recruiter_my_registration(request):
    """View or update own convention registration."""
    if not is_recruiter(request.user):
        return Response({'error': 'Not a recruiter.'}, status=status.HTTP_403_FORBIDDEN)

    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = request.user.recruiter_profile
        registration = RecruiterRegistration.objects.select_related(
            'booth_package', 'meal_option'
        ).get(recruiter=profile, convention=convention)
    except (RecruiterProfile.DoesNotExist, RecruiterRegistration.DoesNotExist):
        return Response({'has_registration': False})

    if request.method == 'GET':
        serializer = RecruiterConventionRegistrationSerializer(registration)
        return Response(serializer.data)

    # PUT: only allow updates before approval
    if registration.status not in ('pending',):
        return Response(
            {'error': 'Cannot modify registration after approval.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = RecruiterConventionRegistrationSerializer(
        registration, data=request.data, partial=True
    )
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data)


# ============================================================
# Admin: Manage Recruiter Registrations
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_registrations(request):
    """List all recruiter registrations for active convention."""
    if not is_staff_or_admin(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_404_NOT_FOUND)

    registrations = RecruiterRegistration.objects.filter(
        convention=convention
    ).select_related(
        'recruiter__organization', 'recruiter__user',
        'booth_package', 'meal_option'
    )

    paginator = AdminPagination()
    page = paginator.paginate_queryset(registrations, request)
    serializer = AdminRecruiterRegistrationSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_update_registration(request, pk):
    """Admin: approve registration and assign booth_id."""
    if not is_staff_or_admin(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        registration = RecruiterRegistration.objects.select_related(
            'recruiter__organization', 'booth_package', 'meal_option'
        ).get(pk=pk)
    except RecruiterRegistration.DoesNotExist:
        return Response({'error': 'Registration not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AdminRecruiterRegistrationSerializer(
        registration, data=request.data, partial=True
    )
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data)


# ============================================================
# Attendee List (for recruiters)
# ============================================================

class AttendeePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class AdminPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([RecruiterThrottle])
def recruiter_attendees(request):
    """List members attending the convention (visible to recruiters)."""
    if not is_approved_recruiter(request.user):
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)

    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Recruiter profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check for active convention registration
    try:
        reg = RecruiterRegistration.objects.select_related('booth_package').get(
            recruiter=profile, convention=convention,
            status__in=['pending', 'approved', 'confirmed']
        )
    except RecruiterRegistration.DoesNotExist:
        return Response(
            {'error': 'You must be registered for the convention to view attendees.'},
            status=status.HTTP_403_FORBIDDEN
        )

    includes_resume = reg.booth_package.includes_resume_access

    attendees = ConventionRegistration.objects.filter(
        convention=convention,
        visible_to_recruiters=True,
        status_code__in=['registered', 'confirmed', 'checked_in']
    ).select_related('member')

    # Search filter — require at least 2 characters to prevent enumeration
    search = request.query_params.get('search', '').strip()
    if search:
        if len(search) < 2:
            return Response(
                {'error': 'Search query must be at least 2 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from django.db.models import Q
        attendees = attendees.filter(
            Q(member__first_name__icontains=search) |
            Q(member__last_name__icontains=search) |
            Q(member__preferred_first_name__icontains=search) |
            Q(member__chapter__icontains=search)
        )

    paginator = AttendeePagination()
    page = paginator.paginate_queryset(attendees, request)

    serializer = AttendeeSerializer(
        page, many=True,
        context={'request': request, 'includes_resume_access': includes_resume}
    )
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([RecruiterThrottle])
def recruiter_attendee_resume(request, member_id):
    """Download a member's resume PDF."""
    if not is_approved_recruiter(request.user):
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)

    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_404_NOT_FOUND)

    profile = request.user.recruiter_profile

    # Verify resume access
    try:
        reg = RecruiterRegistration.objects.select_related('booth_package').get(
            recruiter=profile, convention=convention,
            status__in=['pending', 'approved', 'confirmed']
        )
    except RecruiterRegistration.DoesNotExist:
        return Response({'error': 'No active registration.'}, status=status.HTTP_403_FORBIDDEN)

    if not reg.booth_package.includes_resume_access:
        return Response(
            {'error': 'Your booth package does not include resume access.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check member is attending and visible
    from accounts.models import Member
    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        return Response({'error': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)

    reg_exists = ConventionRegistration.objects.filter(
        convention=convention,
        member=member,
        visible_to_recruiters=True,
        status_code__in=['registered', 'confirmed', 'checked_in']
    ).exists()

    if not reg_exists:
        return Response({'error': 'Member not available.'}, status=status.HTTP_404_NOT_FOUND)

    if not member.resume:
        return Response({'error': 'No resume on file.'}, status=status.HTTP_404_NOT_FOUND)

    from django.http import FileResponse
    return FileResponse(member.resume.open('rb'), content_type='application/pdf')


# ============================================================
# Member Resume Upload
# ============================================================

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def member_resume(request):
    """Upload or delete member resume."""
    user = request.user
    if not hasattr(user, 'member') or not user.member:
        return Response({'error': 'No member profile.'}, status=status.HTTP_400_BAD_REQUEST)

    member = user.member

    if request.method == 'DELETE':
        if member.resume:
            member.resume.delete()
            member.resume_uploaded_at = None
            member.save()
        return Response({'success': 'Resume removed.'})

    # POST: upload
    file = request.FILES.get('resume')
    if not file:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate PDF extension
    if not file.name.lower().endswith('.pdf'):
        return Response({'error': 'Only PDF files are accepted.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate PDF content type
    if file.content_type != 'application/pdf':
        return Response({'error': 'Only PDF files are accepted.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate PDF magic bytes
    header = file.read(5)
    file.seek(0)
    if header[:5] != b'%PDF-':
        return Response({'error': 'File does not appear to be a valid PDF.'}, status=status.HTTP_400_BAD_REQUEST)

    # Max 5MB
    if file.size > 5 * 1024 * 1024:
        return Response({'error': 'File size must be under 5MB.'}, status=status.HTTP_400_BAD_REQUEST)

    # Delete old resume if exists
    if member.resume:
        member.resume.delete(save=False)

    member.resume = file
    member.resume_uploaded_at = timezone.now()
    member.save()

    return Response({
        'success': 'Resume uploaded.',
        'resume_url': request.build_absolute_uri(member.resume.url),
        'uploaded_at': member.resume_uploaded_at.isoformat()
    })


# ============================================================
# Invoice Management
# ============================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_invoices(request):
    """Staff: list or create invoices."""
    if not is_staff_or_finance(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        invoices = Invoice.objects.select_related('organization', 'convention', 'created_by')

        # Filters
        org_id = request.query_params.get('organization')
        convention_id = request.query_params.get('convention')
        invoice_status = request.query_params.get('status')

        if org_id:
            invoices = invoices.filter(organization_id=org_id)
        if convention_id:
            invoices = invoices.filter(convention_id=convention_id)
        if invoice_status:
            invoices = invoices.filter(status=invoice_status)

        paginator = AdminPagination()
        page = paginator.paginate_queryset(invoices, request)
        serializer = InvoiceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # POST: create invoice
    serializer = InvoiceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    invoice = serializer.save(created_by=request.user)

    # Send email if created directly as 'sent'
    if invoice.status == 'sent':
        try:
            mail_subject = f'Invoice {invoice.invoice_number} from Tau Beta Pi'
            message = render_to_string('recruiters/invoice_email.html', {
                'invoice': invoice,
                'frontend_url': FRONTEND_URL,
            })
            email_msg = EmailMultiAlternatives(
                subject=mail_subject,
                body='',
                to=[invoice.organization.billing_email]
            )
            email_msg.attach_alternative(message, "text/html")
            email_msg.send()
        except Exception as e:
            print(f"Failed to send invoice email: {e}")

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_update_invoice(request, pk):
    """Staff: update invoice status."""
    if not is_staff_or_finance(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        invoice = Invoice.objects.select_related('organization').get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({'error': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)

    old_status = invoice.status
    serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    # Send email when status changes to 'sent'
    if old_status != 'sent' and invoice.status == 'sent':
        try:
            mail_subject = f'Invoice {invoice.invoice_number} from Tau Beta Pi'
            message = render_to_string('recruiters/invoice_email.html', {
                'invoice': invoice,
                'frontend_url': FRONTEND_URL,
            })
            email_msg = EmailMultiAlternatives(
                subject=mail_subject,
                body='',
                to=[invoice.organization.billing_email]
            )
            email_msg.attach_alternative(message, "text/html")
            email_msg.send()
        except Exception as e:
            print(f"Failed to send invoice email: {e}")

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recruiter_invoices(request):
    """Recruiter: view own organization's invoices."""
    if not is_recruiter(request.user):
        return Response({'error': 'Not a recruiter.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    invoices = Invoice.objects.filter(
        organization=profile.organization
    ).select_related('organization', 'convention')

    serializer = RecruiterInvoiceSerializer(invoices, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_organizations(request):
    """Staff: list all organizations."""
    if not is_staff_or_admin(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    orgs = Organization.objects.all().order_by('name')
    paginator = AdminPagination()
    page = paginator.paginate_queryset(orgs, request)
    serializer = OrganizationSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
