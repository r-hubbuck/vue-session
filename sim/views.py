import os
import pymssql

from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout, get_user_model

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import get_object_or_404

from .tokens import account_activation_token
from .utils import send_sms
from .models import CustomUser, Member, Address
from .serializers import (
    CodeValidationSerializer,
    LoginSerializer,
    CreateUserSerializer,
    VerifyMemberSerializer,
    AddressSerializer
)

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

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def code_check(request):
    """
    Handle SMS code verification for user login.
    GET: Send SMS code to user (if needed)
    POST: Verify the SMS code and login user
    """
    
    pk = request.session.get('pk')
    print("PK is", pk)
    
    if not pk:
        return Response(
            {'success': False, 'message': 'No user session found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(pk=pk)
        code = user.code
        code_user = f"{user.code}"
        print(code, code_user)
        # send_sms(code_user, user.phone)

        if request.method == 'GET':
            # send_sms(code_user, user.phone)
            print(code_user)
            return Response(
                {'success': True, 'message': 'Code check view ready'}, 
                status=status.HTTP_200_OK
            )
        
        elif request.method == 'POST':
            print('checking code...')
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
                    # 
                    return Response(
                        {'success': False, 'message': 'Invalid code'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'success': False, 'errors': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
    except CustomUser.DoesNotExist:
        return Response(
            {'success': False, 'message': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user with email and password.
    Sets session PK and redirects to code_check for SMS verification.
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
            return redirect('code_check')  
        else:
            if not CustomUser.objects.filter(email=email).exists():
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
        return Response({
            'email': request.user.email
            # 'email': request.user.email
        }, status=status.HTTP_200_OK)
    
    return Response(
        {'message': 'Not logged in'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create Member instance from session variables
        member_first_name = request.session.get('member_first_name', '')
        member_middle_name = request.session.get('member_middle_name', '')
        member_last_name = request.session.get('member_last_name', '')
        member_chapter = request.session.get('member_chapter', '')
        member = None
        if member_first_name and member_last_name and member_chapter:
            member = Member.objects.create(
                first_name=member_first_name,
                middle_name=member_middle_name,
                last_name=member_last_name,
                chapter=member_chapter,
                phone=user.phone,
                email=user.email
            )
            user.member = member
            user.save()
        # Create address instance from session variables
        member_add1 = request.session.get('member_add1', '')
        member_add2 = request.session.get('member_add2', '')
        member_city = request.session.get('member_city', '')
        member_state = request.session.get('member_state', '')
        member_zip = request.session.get('member_zip', '')
        member_add_type = request.session.get('member_add_type', '')
        current_site = get_current_site(request)
        mail_subject = 'Activate Your Account'
        message = render_to_string('registration/account_activation_email.html', {
            'member': member,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })
        to_email = user.email
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        return Response({'success': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_PROD_HOST = os.getenv('SQL_PROD_HOST')
SQL_USER = r'tbp\bdickson'

class ChapterListAPIView(APIView):
    permission_classes = []

    def get(self, request):
        print('connecting...')
        conn = pymssql.connect(
            host=SQL_PROD_HOST,
            tds_version=r'7.0',
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='Member'
        )
        cursor = conn.cursor(as_dict=True)
        cursor.execute(''' SELECT Chapters.chp_id
                    ,Chapters.chp_code
                    ,Chapters.Chp_Name_Short
                    ,Chapters.PrimaryChapter
                    ,Schools.sch_ConversationalName
                    ,Schools.sch_school
                    FROM Chapters
                    INNER JOIN Schools
                    ON Chapters.chp_id = Schools.sch_id
                    where chp_name_greek != ''
                    and PrimaryChapter = 'Y'
                    and sch_ConversationalName != '' ''')
        chapters = cursor.fetchall()
        chap_list = {}
        for i, c in enumerate(chapters):
            chap_list[i] = {"id": str(c['chp_code']),"title": c['sch_school'] + " (" + c['Chp_Name_Short'].strip() + ")"}
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
                host=SQL_PROD_HOST,
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
                    'member_first_name': users[0]['mem_fname'],
                    'member_middle_name': users[0]['mem_mname'],
                    'member_last_name': users[0]['mem_lname'],
                    'member_chapter': users[0]['Chp_Name_Short']                                
                }
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
        user.is_active = True
        user.save()

        return redirect('http://localhost:5173/login?activate=true')
    else:
        return Response(
            {'message': 'Invalid activation link or user not found. Please try again or contact tbp hq.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

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
    http_method_names = ['get', 'post', 'put', 'delete']  # Exclude 'patch'
    
    def get_queryset(self):
        # Only return addresses for the authenticated user's member
        user = self.request.user
        if hasattr(user, 'member'):
            return Address.objects.filter(member=user.member).select_related('member')
        return Address.objects.none()
    
    def perform_create(self, serializer):
        # Automatically set the member to the authenticated user's member
        if hasattr(self.request.user, 'member'):
            serializer.save(member=self.request.user.member)
        else:
            raise PermissionDenied("User must have an associated member to create addresses")
    
    def perform_update(self, serializer):
        # Ensure the member field cannot be changed during update
        if hasattr(self.request.user, 'member'):
            serializer.save(member=self.request.user.member)
        else:
            raise PermissionDenied("User must have an associated member")