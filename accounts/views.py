from datetime import datetime
import os
import pymssql

from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.decorators import throttle_classes
from django.shortcuts import get_object_or_404

from .throttles import LoginThrottle, RegisterThrottle, PasswordResetThrottle

from .tokens import account_activation_token, password_reset_token
from .models import User, Member, Address, PhoneNumber, StateProvince, ROLE_MEMBER, ROLE_ALUMNI
from .serializers import (
    CodeValidationSerializer,
    LoginSerializer,
    CreateUserSerializer,
    UserAccountSerializer,
    VerifyMemberSerializer,
    AddressSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PhoneNumberSerializer,
    StateProvinceSerializer
)

FRONTEND_URL = settings.FRONTEND_URL
DOMAIN = settings.DOMAIN

@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def set_csrf_token(request):
    """
    Set the CSRF cookie on the frontend.
    """
    return Response(
        {'message': 'CSRF cookie set'}, 
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def code_check(request):
    """
    Verify the SMS code and login user
    """
    
    pk = request.session.get('pk')
    print("PK is", pk)
    
    if not pk:
        return Response(
            {'success': False, 'message': 'No user session found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(pk=pk)
        code = user.code
        
        serializer = CodeValidationSerializer(data=request.data)
        if serializer.is_valid():
            num = serializer.validated_data['code']
            if str(code) == num:
                code.save()
                login(request, user)
                return Response(
                    {'success': True, 'message': 'logged in'}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'success': False, 'message': 'Invalid code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'success': False, 'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response(
            {'success': False, 'message': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_view(request):
    """
    Authenticate user with email and password.
    Sets session PK and triggers code sending.
    """
 
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        print(email, password)
        user = authenticate(request, email=email, password=password)

        if user:
            request.session['pk'] = user.pk
            print(user.pk)
            
            # Trigger the code sending logic from code_check
            code = user.code
            code_user = f"{user.code}"
            print(code, code_user)
            
            # Try to send email
            try:
                # current_site = get_current_site(request)  # ADD THIS LINE
                mail_subject = 'TBP Portal Verification Code'
                message = render_to_string('registration/two_factor_code_email.html', {
                    'user_code': code,
                    # 'domain': current_site.domain,  # ADD THIS LINE
                    'domain': DOMAIN,
                })
                to_email = user.email
                
                email_msg = EmailMultiAlternatives(
                    subject=mail_subject,
                    body='', 
                    to=[to_email]
                )
                email_msg.attach_alternative(message, "text/html")
                email_msg.send()
                print("Email sent successfully")
            except Exception as e:
                print(f"Failed to send email: {e}")
                # Continue anyway - code is printed in console for dev testing
            
            return Response(
                {'success': True, 'message': 'Verification code sent to your email'}, 
                status=status.HTTP_200_OK
            )
        else:
            if not User.objects.filter(email=email).exists():
                return Response(
                    {'success': False, 'message': 'There is no account registered for the provided email.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return Response(
                    {'success': False, 'message': 'Incorrect password.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
    else:
        return Response(
            {'success': False, 'errors': serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout the authenticated user.
    """
    logout(request)
    return Response(
        {'message': 'Successfully logged out'}, 
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def user_view(request):
    """
    Check if user is authenticated and return user info.
    """
    if request.user.is_authenticated:
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(
        {'message': 'Not logged in'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterThrottle])
def register(request):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create Member instance from session variables
        member_id = request.session.get('member_id', '')
        member_first_name = request.session.get('member_first_name', '')
        member_middle_name = request.session.get('member_middle_name', '')
        member_last_name = request.session.get('member_last_name', '')
        member_chapter = request.session.get('member_chapter', '')
        member_class_year = request.session.get('member_class_year', '')
        member = None
        if member_first_name and member_last_name and member_chapter:
            member = Member.objects.create(
                member_id=member_id,
                first_name=member_first_name,
                middle_name=member_middle_name,
                last_name=member_last_name,
                chapter=member_chapter,
                # phone=user.phone,
                # email=user.email
            )
            user.member = member

            # Set role based on class year
            if member_class_year:
                current_year = datetime.now().year
                try:
                    class_year = int(member_class_year)
                    if class_year < current_year:
                        user.add_role(ROLE_ALUMNI)
                    else:
                        user.add_role(ROLE_MEMBER)
                except ValueError:
                    # If class year isn't a valid integer, don't assign a role yet
                    pass
            else:
                # If no class year provided, assign member role by default
                user.add_role(ROLE_MEMBER)

            user.save()

        # Create addresses from session data
        member_addresses = request.session.get('member_addresses', [])
        print(f"DEBUG: Retrieved {len(member_addresses)} addresses from session:")
        for addr in member_addresses:
            print(f"  Type: '{addr.get('add_type')}', Line1: '{addr.get('add_line1')}'")
        if member_addresses and member:
            created_types = set()
            for address_data in member_addresses:
                add_type = address_data.get('add_type', '')
                if add_type in created_types or not add_type or add_type not in ['Home', 'Work', 'School']:
                    continue
                # ADD THIS DEBUG BLOCK HERE:
                print(f"DEBUG: Attempting to create {add_type} address:")
                print(f"  add_line1: '{address_data.get('add_line1', '')}'")
                print(f"  add_line2: '{address_data.get('add_line2', '')}'")
                print(f"  add_city: '{address_data.get('add_city', '')}'")
                print(f"  add_state: '{address_data.get('add_state', '')}'")
                print(f"  add_zip: '{address_data.get('add_zip', '')}'")
                print(f"  add_country: '{address_data.get('add_country', 'United States')}'")
                try:
                    Address.objects.create(
                        member=member,
                        add_line1=address_data.get('add_line1', ''),
                        add_line2=address_data.get('add_line2', ''),
                        add_city=address_data.get('add_city', ''),
                        add_state=address_data.get('add_state', ''),
                        add_zip=address_data.get('add_zip', ''),
                        add_country=address_data.get('add_country', 'United States') or 'United States',
                        add_type=add_type
                    )
                    created_types.add(add_type)
                except Exception as e:
                    print(f"Error creating address of type {add_type}: {e}")
            del request.session['member_addresses']

        # Create phone numbers from session data
        member_phone_numbers = request.session.get('member_phone_numbers', [])
        if member_phone_numbers and member:
            import re
            created_types = set()
            has_primary = False
            
            for phone_data in member_phone_numbers:
                phone_type = phone_data.get('phone_type', '')
                phone_number = phone_data.get('phone_number', '')
                is_primary = phone_data.get('is_primary', False)
                
                # Skip if type already created or invalid
                if phone_type in created_types or not phone_type or phone_type not in ['Home', 'Mobile', 'Work']:
                    continue
                
                # Skip empty phone numbers
                if not phone_number:
                    continue
                
                try:
                    # Strip all non-digit characters from phone number
                    clean_number = re.sub(r'\D', '', phone_number)
                    
                    # Skip if no digits remain
                    if not clean_number:
                        continue
                    
                    # Ensure only one primary phone number
                    if is_primary and has_primary:
                        is_primary = False
                    
                    PhoneNumber.objects.create(
                        member=member,
                        country_code='+1',  # Default to US country code
                        phone_number=clean_number,
                        phone_type=phone_type,
                        is_primary=is_primary
                    )
                    created_types.add(phone_type)
                    if is_primary:
                        has_primary = True
                        
                except Exception as e:
                    print(f"Error creating phone number of type {phone_type}: {e}")
            
            del request.session['member_phone_numbers']

        # Sync user email to SQL Server if member has a member_id
        if member and member.member_id:
            _sync_emails_to_sql_server(
                member.member_id,
                user.email,
                user.alt_email
            )

        current_site = get_current_site(request)
        mail_subject = 'Activate Your Account'
        message = render_to_string('registration/account_activation_email.html', {
            'member': member,
            # 'domain': current_site.domain,
            'domain': DOMAIN,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })
        to_email = user.email
        email_msg = EmailMultiAlternatives(
            subject=mail_subject,
            body='', 
            to=[to_email]
        )
        email_msg.attach_alternative(message, "text/html")
        email_msg.send()
        print("Email sent successfully")
        return Response({'success': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_PROD_HOST = os.getenv('SQL_PROD_HOST')
SQL_USER = os.getenv('SQL_USER')

class ChapterListAPIView(APIView):
    permission_classes = []

    def get(self, request):
        print('connecting...')
        conn = pymssql.connect(
            server=SQL_PROD_HOST,
            tds_version=r'7.0',
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='Member'
        )
        cursor = conn.cursor(as_dict=True)
        cursor.execute(''' select chapters.chp_number,
                        chapters.chp_id,
                        chapters.chp_code,
                        chapters.chp_name,
                        chapters.chp_name_short,
                        schools.sch_name,
                        schools.sch_school
                        from chapters, schools
                        where chapters.chp_id = schools.sch_chpid
                        and chapters.CollegiateChapter = 1
                        and Len(RTrim(schools.sch_name)) > 0
                        and schools.sch_active = 1
                        order by chp_code ''')
        chapters = cursor.fetchall()
        chap_list = {}
        for i, c in enumerate(chapters):
            chap_list[i] = {"id": str(c['chp_code']),"title": c['chp_name'].strip() + " - " + c['sch_school']}
        return Response({'chapters': chap_list}, status=200)

class VerifyMemberAPIView(APIView):
    """
    API view to verify a member by email, chapter, and year using SQL Server.
    Returns success if a matching record is found, otherwise returns an error message.
    """
    permission_classes = []

    def post(self, request):
        serializer = VerifyMemberSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            chapter = serializer.validated_data['chapter']
            year = serializer.validated_data['year']

            print(email, chapter, year)
            print('connecting...')
            conn = pymssql.connect(
                server=SQL_PROD_HOST,
                tds_version=r'7.0', 
                user=SQL_USER,
                password=SQL_PASSWORD,
                database='Member'
            )
            print('success connecting to ms sqlserver')
            cursor = conn.cursor(as_dict=True)

            cursor.execute(''' SELECT Memblist.mem_id
                                ,Memblist.mem_classy
                                ,Memblist.mem_lname
                                ,Memblist.mem_fname
                                ,Memblist.mem_mname
                                ,Memblist.PreferredName  
                                ,Memblist.mem_chpcd  
                                ,Chapters.chp_name
                                ,Chapters.Chp_Name_Short
                                ,Chapters.chp_code
                                ,Chapters.PrimaryChapter
                                ,Address.add_memid
                                ,Address.add_email
                                ,Address.add_email_alt
                                ,Address.add_line1
                                ,Address.add_line2
                                ,Address.add_city
                                ,Address.add_state
                                ,Address.add_zip
                                ,Address.add_type
                                FROM Memblist
                                INNER JOIN Chapters
                                ON Memblist.mem_chpcd = Chapters.chp_code
                                INNER JOIN Address
                                ON Address.add_memid = Memblist.mem_id
                                WHERE Memblist.mem_classy = %s 
                                AND Memblist.mem_chpcd = %s 
                                AND (add_email = %s OR add_email_alt = %s) ''', [year, chapter, email, email])
            users = cursor.fetchall()

            if len(users) > 0:
                member_info = {
                    'member_id': users[0]['add_memid'],
                    'member_first_name': users[0]['mem_fname'],
                    'member_middle_name': users[0]['mem_mname'],
                    'member_last_name': users[0]['mem_lname'],
                    'member_chapter': users[0]['Chp_Name_Short'],
                    'member_class_year': users[0]['mem_classy']                                
                }

                cursor = conn.cursor(as_dict=True)

                cursor.execute(''' SELECT *
                                   FROM Address
                                   WHERE add_memid = %s  ''', [member_info['member_id']])
                addresses = cursor.fetchall()

                member_addresses = []
                member_phone_numbers = []
                
                # Mapping from SQL Server types to Django types
                SQL_TO_DJANGO_TYPE = {
                    'Business': 'Work',
                    'Home': 'Home',
                    'School': 'School'
                }
                
                for address in addresses:
                    # Map SQL Server address type to Django type
                    sql_type = address.get('add_type') or ''
                    django_type = SQL_TO_DJANGO_TYPE.get(sql_type, sql_type)
                    
                    member_addresses.append({
                        'add_line1': address.get('add_line1') or '',
                        'add_line2': address.get('add_line2') or '',
                        'add_city': address.get('add_city') or '',
                        'add_state': address.get('add_state') or '',
                        'add_zip': address.get('add_zip') or '',
                        'add_type': django_type,  # Use mapped type
                        'add_country': address.get('add_country') or 'United States'
                    })
                                    
                    # Extract phone numbers from Home address only
                    if address['add_type'] == 'Home':
                        # Helper function to strip formatting from phone numbers
                        def clean_phone(phone_str):
                            """Remove all non-digit characters from phone number"""
                            if not phone_str:
                                return ''
                            return ''.join(filter(str.isdigit, phone_str))
                        
                        # Check for home phone
                        if address.get('add_phone'):
                            member_phone_numbers.append({
                                'phone_number': clean_phone(address['add_phone']),
                                'phone_type': 'Home',
                                'is_primary': len(member_phone_numbers) == 0  # First phone is primary
                            })
                        
                        # Check for cell phone
                        if address.get('add_CellPhone'):
                            member_phone_numbers.append({
                                'phone_number': clean_phone(address['add_CellPhone']),
                                'phone_type': 'Mobile',
                                'is_primary': len(member_phone_numbers) == 0  # First phone is primary
                            })
                        
                        # Check for business phone
                        if address.get('add_business_phone'):
                            member_phone_numbers.append({
                                'phone_number': clean_phone(address['add_business_phone']),
                                'phone_type': 'Work',
                                'is_primary': len(member_phone_numbers) == 0  # First phone is primary
                            })

                request.session['member_addresses'] = member_addresses
                request.session['member_phone_numbers'] = member_phone_numbers
                request.session.update(member_info)

                print(request.session.items())
                return Response({'message': 'OK'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No member record could be found. Please try again or contact tbp hq.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API view to handle account activation via email link
@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, uidb64, token):
    """
    Activate user account via email activation link.
    """
    User = get_user_model()

    try: 
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        account_activation_token.mark_token_used(user, token)
        user.is_active = True
        user.save()
        return redirect(f'{FRONTEND_URL}/login?activate=true')
    else:
        # Token is invalid or already used - redirect to error page
        return redirect(f'{FRONTEND_URL}/email-link-error')
        # return Response(
        #     {'message': 'Invalid activation link or user not found. Please try again or contact tbp hq.'}, 
        #     status=status.HTTP_400_BAD_REQUEST
        # )

# API view to handle password reset request by sending an email to the user 
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetThrottle])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate reset link
            # current_site = get_current_site(request)
            mail_subject = 'Password Reset Request'
            message = render_to_string('registration/password_reset_confirm_email.html', {
                'user': user,
                'member': user.member if hasattr(user, 'member') else None,
                # 'domain': current_site.domain,
                'domain': DOMAIN,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': password_reset_token.make_token(user)
            })
            
            email_msg = EmailMultiAlternatives(
                subject=mail_subject,
                body='',  
                to=[email]
            )
        
            email_msg.attach_alternative(message, "text/html")
            email_msg.send()
            
            return Response({
                'message': 'Password reset email has been sent. Please check your inbox.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Return same message to prevent email enumeration
            return Response({
                'message': 'Password reset email has been sent. Please check your inbox.'
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API view to handle password reset confirmation and setting a new password
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    """
    Confirm password reset token and handle password update.
    GET: Validate token and redirect to frontend
    POST: Update password if token is valid
    """
    User = get_user_model()
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check token validity for both GET and POST
    if user is None or not password_reset_token.check_token(user, token):
        if request.method == 'GET':
            return redirect(f'{FRONTEND_URL}/email-link-error')
        else:
            return Response({
                'error': 'Invalid or expired reset link'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        # Token is valid, redirect to password reset form on frontend
        # DON'T mark as used yet - wait for POST
        return redirect(f'{FRONTEND_URL}/password-reset-confirm/{uidb64}/{token}')
    
    elif request.method == 'POST':
        # Validate token again and mark as used
        if not password_reset_token.check_token(user, token):
            return Response({
                'error': 'Invalid or expired reset link'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark token as used BEFORE processing password change
        password_reset_token.mark_token_used(user, token)
            
        # Handle password update
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password1']
            user.set_password(new_password)
            
            # Force token invalidation by updating last_login
            from django.utils import timezone
            user.last_login = timezone.now()
            user.save()
            
            return Response({
                'message': 'Password has been reset successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# API viewset to handle address CRUD operations
class AddressViewSet(viewsets.ModelViewSet):
    """
    A secure ViewSet that provides CRUD operations:
    - GET /api/addresses/ (list user's addresses only)
    - POST /api/addresses/ (create for user's member)
    - GET /api/addresses/{id}/ (retrieve if owned by user)
    - PUT /api/addresses/{id}/ (update if owned by user)
    - DELETE /api/addresses/{id}/ (delete if owned by user)
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']  
    
    # Mapping between Django and SQL Server address types
    DJANGO_TO_SQL = {
        'Work': 'Business',
        'Home': 'Home',
        'School': 'School'
    }
    
    SQL_TO_DJANGO = {
        'Business': 'Work',
        'Home': 'Home',
        'School': 'School'
    }
    
    def _map_type_to_sql(self, django_type):
        """Convert Django address type to SQL Server type"""
        return self.DJANGO_TO_SQL.get(django_type, django_type)
    
    def _map_type_from_sql(self, sql_type):
        """Convert SQL Server address type to Django type"""
        return self.SQL_TO_DJANGO.get(sql_type, sql_type)  
    
    def get_queryset(self):
        # Only return addresses for the authenticated user's member_id
        user = self.request.user
        if hasattr(user, 'member'):
            return Address.objects.filter(member=user.member).select_related('member')
        return Address.objects.none()
    
    def _sync_to_sql_server(self, action, member_id, address_data, old_address_data=None):
        """
        Sync address changes to SQL Server database.
        
        Args:
            action: 'create', 'update', or 'delete'
            member_id: The member_id to sync
            address_data: Dict with address fields (add_line1, add_line2, add_city, add_state, add_zip, add_type)
            old_address_data: For updates, the old address data to find the record
        """
        try:
            conn = pymssql.connect(
                server=SQL_PROD_HOST,
                tds_version=r'7.0',
                user=SQL_USER,
                password=SQL_PASSWORD,
                database='Member'
            )
            cursor = conn.cursor()
            
            # Map address types from Django to SQL Server format
            sql_type = self._map_type_to_sql(address_data.get('add_type', ''))
            
            if action == 'create':
                # Insert new address into SQL Server
                cursor.execute('''
                    INSERT INTO Address (add_memid, add_line1, add_line2, add_city, add_state, add_zip, add_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    member_id,
                    address_data.get('add_line1', ''),
                    address_data.get('add_line2', ''),
                    address_data.get('add_city', ''),
                    address_data.get('add_state', ''),
                    address_data.get('add_zip', ''),
                    sql_type
                ))
                print(f"SQL Server: Created address (type: {sql_type}) for member {member_id}")
                
            elif action == 'update':
                # Update existing address in SQL Server
                # Match by old add_line1 and add_memid, then update all fields
                old_line1 = old_address_data.get('add_line1', '')
                old_sql_type = self._map_type_to_sql(old_address_data.get('add_type', ''))
                
                cursor.execute('''
                    UPDATE Address
                    SET add_line1 = %s,
                        add_line2 = %s,
                        add_city = %s,
                        add_state = %s,
                        add_zip = %s,
                        add_type = %s
                    WHERE add_memid = %s AND add_line1 = %s AND add_type = %s
                ''', (
                    address_data.get('add_line1', ''),
                    address_data.get('add_line2', ''),
                    address_data.get('add_city', ''),
                    address_data.get('add_state', ''),
                    address_data.get('add_zip', ''),
                    sql_type,
                    member_id,
                    old_line1,
                    old_sql_type
                ))
                print(f"SQL Server: Updated address (type: {old_sql_type} -> {sql_type}) for member {member_id}")
                
            elif action == 'delete':
                # Delete address from SQL Server
                cursor.execute('''
                    DELETE FROM Address
                    WHERE add_memid = %s AND add_line1 = %s AND add_type = %s
                ''', (
                    member_id,
                    address_data.get('add_line1', ''),
                    sql_type
                ))
                print(f"SQL Server: Deleted address (type: {sql_type}) for member {member_id}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error syncing address to SQL Server: {e}")
            # Don't raise exception - allow Django operation to succeed even if SQL Server sync fails
    
    def perform_create(self, serializer):
        # Automatically set the member to the authenticated user's member_id
        if hasattr(self.request.user, 'member'):
            member = self.request.user.member
            address = serializer.save(member=member)
            
            # Sync to SQL Server if member has a member_id
            if member.member_id:
                address_data = {
                    'add_line1': address.add_line1,
                    'add_line2': address.add_line2,
                    'add_city': address.add_city,
                    'add_state': address.add_state,
                    'add_zip': address.add_zip,
                    'add_type': address.add_type
                }
                self._sync_to_sql_server('create', member.member_id, address_data)
        else:
            raise PermissionDenied("User must have an associated member record to create addresses")
    
    def perform_update(self, serializer):
        # Ensure the member field cannot be changed during update
        if hasattr(self.request.user, 'member'):
            member = self.request.user.member
            
            # Get old address data before update
            old_address = self.get_object()
            old_address_data = {
                'add_line1': old_address.add_line1,
                'add_line2': old_address.add_line2,
                'add_city': old_address.add_city,
                'add_state': old_address.add_state,
                'add_zip': old_address.add_zip,
                'add_type': old_address.add_type
            }
            
            # Save the updated address
            address = serializer.save(member=member)
            
            # Sync to SQL Server if member has a member_id
            if member.member_id:
                new_address_data = {
                    'add_line1': address.add_line1,
                    'add_line2': address.add_line2,
                    'add_city': address.add_city,
                    'add_state': address.add_state,
                    'add_zip': address.add_zip,
                    'add_type': address.add_type
                }
                self._sync_to_sql_server('update', member.member_id, new_address_data, old_address_data)
        else:
            raise PermissionDenied("User must have an associated member record to update addresses")
    
    def destroy(self, request, *args, **kwargs):
        # Get address data before deletion
        address = self.get_object()
        member = address.member
        
        address_data = {
            'add_line1': address.add_line1,
            'add_line2': address.add_line2,
            'add_city': address.add_city,
            'add_state': address.add_state,
            'add_zip': address.add_zip,
            'add_type': address.add_type
        }
        
        # Delete from Django database
        response = super().destroy(request, *args, **kwargs)
        
        # Sync deletion to SQL Server if member has a member_id
        if member.member_id:
            self._sync_to_sql_server('delete', member.member_id, address_data)
        
        return response

def _sync_emails_to_sql_server(member_id, email, alt_email):
    """
    Sync email and alt_email changes to SQL Server database.
    Emails are stored in the Address table where add_type='Home'.
    
    Args:
        member_id: The member_id to sync
        email: The primary email address
        alt_email: The alternate email address (can be empty)
    """
    try:
        conn = pymssql.connect(
            server=SQL_PROD_HOST,
            tds_version=r'7.0',
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='Member'
        )
        cursor = conn.cursor()
        
        # Check if a Home address exists
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM Address
            WHERE add_memid = %s AND add_type = 'Home'
        ''', (member_id,))
        result = cursor.fetchone()
        
        if result[0] == 0:
            # No Home address exists, create one with the emails
            cursor.execute('''
                INSERT INTO Address (add_memid, add_type, add_email, add_email_alt)
                VALUES (%s, 'Home', %s, %s)
            ''', (member_id, email or '', alt_email or ''))
            print(f"SQL Server: Created Home address with emails for member {member_id}")
        else:
            # Home address exists, update the email columns
            cursor.execute('''
                UPDATE Address
                SET add_email = %s,
                    add_email_alt = %s
                WHERE add_memid = %s AND add_type = 'Home'
            ''', (email or '', alt_email or '', member_id))
            print(f"SQL Server: Updated emails (primary: {email}, alt: {alt_email}) for member {member_id}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error syncing emails to SQL Server: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise exception - allow Django operation to succeed even if SQL Server sync fails
        
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_account_view(request):
    """
    Get or update user account details (email, alt_email)
    """
    user = request.user
    
    if request.method == 'GET':
        serializer = UserAccountSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = UserAccountSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            
            # Sync emails to SQL Server if user has an associated member with member_id
            if hasattr(user, 'member') and user.member and user.member.member_id:
                _sync_emails_to_sql_server(
                    user.member.member_id,
                    user.email,
                    user.alt_email
                )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Phone Numbers ViewSet
class PhoneNumberViewSet(viewsets.ModelViewSet):
    """
    A secure ViewSet that provides CRUD operations for phone numbers:
    - GET /api/phone-numbers/ (list user's phone numbers only)
    - POST /api/phone-numbers/ (create for user's member)
    - GET /api/phone-numbers/{id}/ (retrieve if owned by user)
    - PUT /api/phone-numbers/{id}/ (update if owned by user)
    - DELETE /api/phone-numbers/{id}/ (delete if owned by user)
    """
    serializer_class = PhoneNumberSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
    
    # Mapping between Django phone types and SQL Server column names
    PHONE_TYPE_TO_COLUMN = {
        'Mobile': 'add_CellPhone',
        'Home': 'add_phone',
        'Work': 'add_business_phone'
    }
    
    def _get_sql_column_for_type(self, phone_type):
        """Get the SQL Server column name for a given phone type"""
        return self.PHONE_TYPE_TO_COLUMN.get(phone_type)
    
    def _format_phone_for_sql(self, phone_number):
        """
        Format phone number for SQL Server storage.
        Converts '8655464578' to '865-546-4578'
        """
        if not phone_number:
            return ''
        
        # Remove any non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone_number))
        
        # Format as XXX-XXX-XXXX for 10-digit numbers
        if len(digits_only) == 10:
            return f"{digits_only[0:3]}-{digits_only[3:6]}-{digits_only[6:10]}"
        
        # For other lengths, return as-is (international numbers, etc.)
        return digits_only
    
    def _sync_phone_to_sql_server(self, action, member_id, phone_type, phone_number=None):
        """
        Sync phone number changes to SQL Server database.
        Phone numbers are stored in the Address table where add_type='Home'.
        
        Args:
            action: 'create', 'update', or 'delete'
            member_id: The member_id to sync
            phone_type: 'Mobile', 'Home', or 'Work'
            phone_number: The phone number (digits only) or None for delete
        """
        column_name = self._get_sql_column_for_type(phone_type)
        if not column_name:
            print(f"Warning: Unknown phone type '{phone_type}', skipping SQL Server sync")
            return
        
        # Format phone number for SQL Server (XXX-XXX-XXXX)
        formatted_phone = self._format_phone_for_sql(phone_number) if phone_number else ''
        
        try:
            conn = pymssql.connect(
                server=SQL_PROD_HOST,
                tds_version=r'7.0',
                user=SQL_USER,
                password=SQL_PASSWORD,
                database='Member'
            )
            cursor = conn.cursor()
            
            # Phone numbers are stored in the Home address record
            # First check if a Home address exists
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM Address
                WHERE add_memid = %s AND add_type = 'Home'
            ''', (member_id,))
            result = cursor.fetchone()
            
            if result[0] == 0:
                # No Home address exists, create one with just the phone number
                if action in ['create', 'update'] and formatted_phone:
                    cursor.execute(f'''
                        INSERT INTO Address (add_memid, add_type, {column_name})
                        VALUES (%s, 'Home', %s)
                    ''', (member_id, formatted_phone))
                    print(f"SQL Server: Created Home address with {phone_type} phone ({formatted_phone}) for member {member_id}")
            else:
                # Home address exists, update the phone number column
                if action == 'delete':
                    # Set phone column to empty string
                    cursor.execute(f'''
                        UPDATE Address
                        SET {column_name} = ''
                        WHERE add_memid = %s AND add_type = 'Home'
                    ''', (member_id,))
                    print(f"SQL Server: Deleted {phone_type} phone for member {member_id}")
                else:
                    # Create or update - set the phone number
                    cursor.execute(f'''
                        UPDATE Address
                        SET {column_name} = %s
                        WHERE add_memid = %s AND add_type = 'Home'
                    ''', (formatted_phone, member_id))
                    print(f"SQL Server: Updated {phone_type} phone to {formatted_phone} for member {member_id}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error syncing phone to SQL Server: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise exception - allow Django operation to succeed even if SQL Server sync fails
    
    def get_queryset(self):
        # Only return phone numbers for the authenticated user's member
        user = self.request.user
        if hasattr(user, 'member'):
            return PhoneNumber.objects.filter(member=user.member).select_related('member')
        return PhoneNumber.objects.none()
    
    def perform_create(self, serializer):
        # Automatically set the member to the authenticated user's member
        if hasattr(self.request.user, 'member'):
            # If this is the first phone number, make it primary by default
            member = self.request.user.member
            existing_phones = PhoneNumber.objects.filter(member=member)
            if not existing_phones.exists():
                phone = serializer.save(member=member, is_primary=True)
            else:
                phone = serializer.save(member=member)
            
            # Sync to SQL Server if member has a member_id
            if member.member_id:
                self._sync_phone_to_sql_server('create', member.member_id, phone.phone_type, phone.phone_number)
        else:
            raise PermissionDenied("User must have an associated member record to create phone numbers")
    
    def perform_update(self, serializer):
        # Ensure the member field cannot be changed during update
        if hasattr(self.request.user, 'member'):
            member = self.request.user.member
            
            # Get old phone data before update
            old_phone = self.get_object()
            old_phone_type = old_phone.phone_type
            
            # If this phone is being set as primary, unset all other primary phones
            if serializer.validated_data.get('is_primary', False):
                PhoneNumber.objects.filter(member=member, is_primary=True).exclude(
                    id=old_phone.id
                ).update(is_primary=False)
            
            phone = serializer.save(member=member)
            
            # Sync to SQL Server if member has a member_id
            if member.member_id:
                # If phone type changed, clear the old column and set the new one
                if old_phone_type != phone.phone_type:
                    self._sync_phone_to_sql_server('delete', member.member_id, old_phone_type)
                    self._sync_phone_to_sql_server('create', member.member_id, phone.phone_type, phone.phone_number)
                else:
                    # Just update the phone number
                    self._sync_phone_to_sql_server('update', member.member_id, phone.phone_type, phone.phone_number)
        else:
            raise PermissionDenied("User must have an associated member record to update phone numbers")
    
    def destroy(self, request, *args, **kwargs):
        # Get the phone number to be deleted
        phone_number = self.get_object()
        member = phone_number.member
        is_primary = phone_number.is_primary
        phone_type = phone_number.phone_type
        
        # Get remaining phones (excluding the one being deleted)
        remaining_phones = PhoneNumber.objects.filter(member=member).exclude(id=phone_number.id)
        
        # Delete the phone first to avoid constraint violations
        response = super().destroy(request, *args, **kwargs)
        
        # If we deleted the primary phone and there are other phones, make the first one primary
        if is_primary and remaining_phones.exists():
            first_phone = remaining_phones.first()
            first_phone.is_primary = True
            first_phone.save()
        
        # Sync deletion to SQL Server if member has a member_id
        if member.member_id:
            self._sync_phone_to_sql_server('delete', member.member_id, phone_type)
        
        return response

@api_view(['GET'])
@permission_classes([AllowAny])
def state_province_list(request):
    """
    Return all states/provinces grouped by country
    """
    states_provinces = StateProvince.objects.all().order_by('st_ctrid', 'st_name')
    
    # Group by country
    grouped_data = {}
    for sp in states_provinces:
        country = sp.country_name
        if country not in grouped_data:
            grouped_data[country] = []
        
        grouped_data[country].append({
            'id': sp.st_id,
            'name': sp.st_name,
            'abbrev': sp.st_abbrev
        })
    
    return Response(grouped_data, status=status.HTTP_200_OK)