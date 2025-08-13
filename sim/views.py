import os
from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
import json
import pymssql
from django.core.validators import validate_email
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .utils import send_sms
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import CreateUserForm, CodeForm
from .models import CustomUser

@ensure_csrf_cookie
@require_http_methods(['GET'])
def set_csrf_token(request):
    """
    We set the CSRF cookie on the frontend.
    """
    return JsonResponse({'message': 'CSRF cookie set'})

def code_check(request):
    form = CodeForm(request.POST or None)
    pk = request.session.get('pk')
    print("PK is", pk)
    if pk:
        user = CustomUser.objects.get(pk=pk)
        code = user.code
        code_user = f"{user.code}"
        print(code, code_user)
        # send_sms(code_user, user.phone)

        if not request.POST:
            # send_sms(code_user, user.phone)
            print(code_user)
        # if form.is_valid():
        if request.method == 'POST':
            print('checking code...')
            data = json.loads(request.body.decode('utf-8'))
            num = data['code']
            if str(code) == num:
                code.save()
                # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                login(request, user)
                # return redirect('http://localhost:5173/')
                return JsonResponse({'success': True, 'message': 'logged in'})

            else:
                return redirect('http://localhost:5173/login')
    # return redirect('http://localhost:5173/code-check')
    return JsonResponse({'success': True, 'message': 'Code check view ran'})

# @require_http_methods(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data['email']
        password = data['password']
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'message': 'Invalid JSON'}, status=400
        )
    print(email, password)
    user = authenticate(request, username=email, password=password)

    if user:
        request.session['pk'] = user.pk
        print(user.pk)
        return redirect('code_check')  
    else:
        if not CustomUser.objects.filter(username=email).exists():
             return JsonResponse(
                {'success': False, 'message': 'There is no account registered for the provided email.'}, status=401
            )
        else:
            return JsonResponse(
                {'success': False, 'message': 'Incorrect password.'}, status=401
            )
        # return JsonResponse(
        #     {'success': False, 'message': 'Invalid credentials'}, status=401
        # )

def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out'})

@require_http_methods(['GET'])
def user(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {'username': request.user.username, 'email': request.user.email}
        )
    return JsonResponse(
        {'message': 'Not logged in'}, status=401
    )

@require_http_methods(['POST'])
def register(request):
    data = json.loads(request.body.decode('utf-8'))
    form = CreateUserForm(data)
    if form.is_valid():
        # form.save()
        user = form.save(commit=False)
        user.is_active = False
        user.username = form.cleaned_data.get('email')
        user.save()
        current_site = get_current_site(request)
        mail_subject = 'Activate Your Account'
        message = render_to_string('registration/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })

        to_email = form.cleaned_data.get('email')

        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )

        email.send()
        return JsonResponse({'success': 'User registered successfully'}, status=201)
    else:
        errors = form.errors.as_json()
        return JsonResponse({'error': errors}, status=400)
    

SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_PROD_HOST = os.getenv('SQL_PROD_HOST')
SQL_USER = r'tbp\bdickson'

@require_http_methods(['GET'])
def chapter_list(request):
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
        # chap_list[str(c['chp_code'])] = c['sch_school'] + "   (" + c['Chp_Name_Short'].strip() + ")"
        chap_list[i] = {"id": str(c['chp_code']),"title": c['sch_school'] + " (" + c['Chp_Name_Short'].strip() + ")"}

    return JsonResponse({'chapters': chap_list}, status=201)

@require_http_methods(['POST'])
def verify_member(request):
    # try:
         # Decode the request body from bytes to string
        data_str = request.body.decode('utf-8')
        # Parse the JSON string into a Python dictionary
        data = json.loads(data_str)
        
        # Access the data as needed, for example:
        email = data.get('email')
        chapter = data.get('selectedChapter')
        year  = data.get('selectedYear')

        print(email, chapter, year)
        # Process the data
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

        try:
            validate_email(email)
        except ValidationError as e:
            print("bad email, details:", e)
        else:
            clean_email = email
            print(clean_email)
  
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
                                FROM Memblist
                                INNER JOIN Chapters
                                ON Memblist.mem_chpcd = Chapters.chp_code
                                INNER JOIN Address
                                ON Address.add_memid = Memblist.mem_id
                                WHERE Memblist.mem_classy = %s 
                                AND Memblist.mem_chpcd = %s 
                                AND (add_email = %s OR add_email_alt = %s) ''', [year, chapter, clean_email, clean_email])
            users = cursor.fetchall()
            # print(users)
            # print(len(users))
            # data = {'key': 'value'}
            # message = "User found."
            # response_data = {
            #     'status': 'success',
            #     'message': message,
            #     'data': data
            # }
            if len(users) > 0:
                return JsonResponse({'message': 'OK'}, status=200)
            else:
                return JsonResponse({'message': 'No member record could be found. Please try again or contact tbp hq.'}, status=200)
        
def activate(request, uidb64, token):
    User = get_user_model()

    try: 
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # messages.success(request, 'Your account has been successfully activated.')
        # return JsonResponse({'message': 'OK'}, status=200)
        return redirect('http://localhost:5173/login?activate=true')
    else:
        # messages.error(request, 'Activation link is invalid or expired. Please create your account again and check your email for account verification.')
        return JsonResponse({'message': 'No member record could be found. Please try again or contact tbp hq.'}, status=200)
        