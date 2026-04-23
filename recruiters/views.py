import logging
import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone

from django.db import transaction, IntegrityError

logger = logging.getLogger(__name__)

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

_LOGO_ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
_LOGO_ALLOWED_CONTENT_TYPES = {'image/png', 'image/jpeg'}
_LOGO_MAX_SIZE = 5 * 1024 * 1024  # 5MB
_LOGO_PNG_SIG = b'\x89PNG'
_LOGO_JPEG_SIG = b'\xff\xd8\xff'


def _validate_org_logo(file):
    """
    Validate an organization logo file. Returns an error string or None if valid.
    Accepts PNG and JPG only. Checks extension, content-type, magic bytes, and size.
    """
    if file.size > _LOGO_MAX_SIZE:
        return 'Logo file size must be under 5MB.'

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in _LOGO_ALLOWED_EXTENSIONS:
        return 'Logo must be a PNG or JPG file.'

    if file.content_type not in _LOGO_ALLOWED_CONTENT_TYPES:
        return 'Logo must be a PNG or JPG file.'

    header = file.read(8)
    file.seek(0)
    if not (header.startswith(_LOGO_PNG_SIG) or header.startswith(_LOGO_JPEG_SIG)):
        return 'Logo does not appear to be a valid PNG or JPG image.'

    return None


# ============================================================
# Helper: Check recruiter role
# ============================================================

def is_recruiter(user):
    return user.has_role(ROLE_RECRUITER)


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
@transaction.atomic
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
        user.is_active = False
        user.last_login = timezone.now()
        user.save()
        # Update or create Code
        if hasattr(user, 'code'):
            user.code.save()
        else:
            Code.objects.create(user=user)
    else:
        user = User(email=data['email'], is_active=False)
        user.set_password(data['password1'])
        user.save()

    # Validate logo before creating any DB records (fail fast)
    logo_file = request.FILES.get('org_logo')
    if logo_file:
        logo_error = _validate_org_logo(logo_file)
        if logo_error:
            return Response({'errors': {'org_logo': logo_error}}, status=status.HTTP_400_BAD_REQUEST)

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
        }
    )

    # Save logo to the org if provided (only set on newly created orgs to avoid
    # overwriting an existing org's logo when a second recruiter joins the same org)
    if logo_file and created:
        org.logo = logo_file
        org.save(update_fields=['logo'])

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
        logger.error("Failed to send recruiter activation email to %s: %s", data['email'], e)

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


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def organization_logo(request):
    """Upload or delete the current recruiter's organization logo."""
    if not is_recruiter(request.user):
        return Response({'error': 'Not a recruiter account.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Recruiter profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    org = profile.organization

    if request.method == 'DELETE':
        if org.logo:
            org.logo.delete(save=False)
            org.logo = None
            org.save(update_fields=['logo'])
        return Response({'success': 'Logo removed.'})

    # POST: upload new logo
    file = request.FILES.get('logo')
    if not file:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    logo_error = _validate_org_logo(file)
    if logo_error:
        return Response({'error': logo_error}, status=status.HTTP_400_BAD_REQUEST)

    # Delete old logo before saving new one
    if org.logo:
        org.logo.delete(save=False)

    org.logo = file
    org.save(update_fields=['logo'])

    serializer = OrganizationSerializer(org)
    return Response({'success': 'Logo uploaded.', 'logo_url': serializer.data['logo_url']})


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
def admin_deny_recruiter(request, pk):
    """Deny a recruiter profile by deactivating their account."""
    if not is_staff_or_admin(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = RecruiterProfile.objects.select_related('user').get(pk=pk)
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    profile.user.is_active = False
    profile.user.save()
    return Response({'success': 'Recruiter denied.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_recruiter(request, pk):
    """Delete a recruiter profile and associated user account."""
    if not is_staff_or_admin(request.user):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = RecruiterProfile.objects.select_related('user').get(pk=pk)
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    user = profile.user
    profile.delete()
    user.delete()
    return Response({'success': 'Recruiter deleted.'})


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
            'domain': DOMAIN,
        })
        email_msg = EmailMultiAlternatives(
            subject=mail_subject,
            body='',
            to=[profile.email]
        )
        email_msg.attach_alternative(message, "text/html")
        email_msg.send()
    except Exception as e:
        logger.error("Failed to send recruiter approval email to %s: %s", profile.email, e)

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
        ).prefetch_related('attendees').get(recruiter=profile, convention=convention)
    except (RecruiterProfile.DoesNotExist, RecruiterRegistration.DoesNotExist):
        return Response({'has_registration': False})

    if request.method == 'GET':
        serializer = RecruiterConventionRegistrationSerializer(registration)
        return Response(serializer.data)

    if registration.status not in ('pending', 'approved', 'confirmed'):
        return Response(
            {'error': 'Cannot modify a cancelled registration.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data.copy()
    if registration.status != 'pending':
        data.pop('booth_package', None)

    serializer = RecruiterConventionRegistrationSerializer(
        registration, data=data, partial=True
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

    old_status = registration.status

    serializer = AdminRecruiterRegistrationSerializer(
        registration, data=request.data, partial=True
    )
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    updated = serializer.save()

    if old_status != 'approved' and updated.status == 'approved':
        try:
            message = render_to_string('recruiters/registration_approved_email.html', {
                'registration': updated,
                'frontend_url': FRONTEND_URL,
                'domain': DOMAIN,
            })
            email_msg = EmailMultiAlternatives(
                subject='Your Convention Registration Has Been Approved',
                body='',
                to=[updated.recruiter.email],
            )
            email_msg.attach_alternative(message, 'text/html')
            email_msg.send()
        except Exception as e:
            logger.error("Failed to send recruiter registration approval email to %s: %s", updated.recruiter.email, e)

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

    # Determine which visibility values the recruiter's org type can see
    org_type = profile.organization.org_type if profile.organization else None
    if org_type == 'business':
        visibility_filter = ['business', 'both']
    elif org_type == 'graduate_school':
        visibility_filter = ['graduate_school', 'both']
    else:
        visibility_filter = ['both']

    attendees = ConventionRegistration.objects.filter(
        convention=convention,
        visible_to_recruiters__in=visibility_filter,
        status_code__in=['registered', 'confirmed', 'checked_in']
    ).select_related('person').order_by('person__last_name', 'person__first_name')

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
            Q(person__first_name__icontains=search) |
            Q(person__last_name__icontains=search) |
            Q(person__preferred_first_name__icontains=search) |
            Q(person__member__chapter__icontains=search)
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

    # Check person is attending and visible
    from accounts.models import Person
    try:
        person = Person.objects.get(pk=member_id)
    except Person.DoesNotExist:
        return Response({'error': 'Person not found.'}, status=status.HTTP_404_NOT_FOUND)

    org_type = profile.organization.org_type if profile.organization else None
    if org_type == 'business':
        resume_visibility_filter = ['business', 'both']
    elif org_type == 'graduate_school':
        resume_visibility_filter = ['graduate_school', 'both']
    else:
        resume_visibility_filter = ['both']

    member_reg = ConventionRegistration.objects.filter(
        convention=convention,
        person=person,
        visible_to_recruiters__in=resume_visibility_filter,
        status_code__in=['registered', 'confirmed', 'checked_in']
    ).first()

    if not member_reg:
        return Response({'error': 'Member not available.'}, status=status.HTTP_404_NOT_FOUND)

    if not member_reg.resume:
        return Response({'error': 'No resume on file.'}, status=status.HTTP_404_NOT_FOUND)

    from django.http import FileResponse
    return FileResponse(member_reg.resume.open('rb'), content_type='application/pdf')


# ============================================================
# Member Resume Upload
# ============================================================

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def member_resume(request):
    """Upload or delete member resume for the active convention."""
    user = request.user
    if not (hasattr(user, 'person') and user.person):
        return Response({'error': 'No member profile.'}, status=status.HTTP_400_BAD_REQUEST)

    convention = get_active_convention()
    if not convention:
        return Response({'error': 'No active convention.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reg = ConventionRegistration.objects.get(
            convention=convention,
            person=user.person,
        )
    except ConventionRegistration.DoesNotExist:
        return Response({'error': 'No convention registration found.'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if reg.resume:
            reg.resume.delete()
            reg.resume_uploaded_at = None
            reg.save(update_fields=['resume_uploaded_at'])
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
    if reg.resume:
        reg.resume.delete(save=False)

    reg.resume = file
    reg.resume_uploaded_at = timezone.now()
    reg.save()

    return Response({
        'success': 'Resume uploaded.',
        'resume_url': request.build_absolute_uri(reg.resume.url),
        'uploaded_at': reg.resume_uploaded_at.isoformat()
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
                'domain': DOMAIN,
            })
            email_msg = EmailMultiAlternatives(
                subject=mail_subject,
                body='',
                to=[invoice.organization.billing_email]
            )
            email_msg.attach_alternative(message, "text/html")
            email_msg.send()
        except Exception as e:
            logger.error("Failed to send invoice email for invoice %s: %s", invoice.invoice_number, e)

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
                'domain': DOMAIN,
            })
            email_msg = EmailMultiAlternatives(
                subject=mail_subject,
                body='',
                to=[invoice.organization.billing_email]
            )
            email_msg.attach_alternative(message, "text/html")
            email_msg.send()
        except Exception as e:
            logger.error("Failed to send invoice email for invoice %s: %s", invoice.invoice_number, e)

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
