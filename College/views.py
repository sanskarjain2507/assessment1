from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from .models import College
import base64
import traceback
from cryptography.fernet import Fernet
from django.conf import settings
import logging
from django.http import JsonResponse

def encrypt(txt):
    try:
        # convert integer etc to string first
        txt = str(txt)
        # get the key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY) # key should be byte
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_text
    except Exception as e:
        # log the error if any
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def decrypt(txt):
    try:
        # base64 decode
        txt = base64.urlsafe_b64decode(txt)
        cipher_suite = Fernet(settings.ENCRYPT_KEY)
        decoded_text = cipher_suite.decrypt(txt).decode("ascii")
        return decoded_text
    except Exception as e:
        # log the error
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


@csrf_exempt
def login_page(request):
    return render(request,'College/login_page.html')

def register_college(request):
    courses = ['B.tech', 'B.E.', 'MBA', 'LAW', 'ARTS', 'MEDICAL']
    depts = ['CSE', 'IT', 'CIVIL', 'MECH', 'ETC']
    param={'courses':courses,'department':depts}
    return render(request,'College/signup.html',param)

def register_college_success(request):
    if request.method == 'POST':
        clgname = request.POST.get('clgname')
        mobno = request.POST.get('mobno')
        email = request.POST.get('email')
        password = request.POST.get('password')
        en_password = encrypt(password)
        clgtype = request.POST.get('coltype')
        clgid = request.POST.get('colid')
        depts = "!".join(request.POST.getlist('depts'))
        yoe = request.POST.get('yoe')
        crs = "!".join(request.POST.getlist('courses'))
        unv = request.POST.get('unv')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        principle = request.POST.get('principle')
        file1 = request.FILES['filed']
        fs = FileSystemStorage()
        filename = fs.save(file1.name, file1)
        image_url = fs.url(filename)
        form = College(collegeName=clgname, collegeType=clgtype, collegeId=clgid, coursesOffered=crs, departments=depts,
                       mobileNo=mobno, password=en_password, emailAdd=email, address=address, pincode=pincode,
                       university=unv, yearOfEstablishment=yoe, principleName=principle,image=image_url)
        form.save()
        print('valid')
    else:
        print('invalid')
    clg=College.objects.filter(emailAdd=email)[0]
    courses = clg.coursesOffered.split("!")
    departments = clg.departments.split("!")
    return render(request, 'College/homepage.html', {'username': email,'college':clg,'departments': departments, 'courses': courses})

@csrf_exempt
def college_login_success(request):
    username = request.POST.get('username')
    password1 = request.POST.get('password1')
    print(encrypt(password1))
    isUser = College.objects.filter(emailAdd=username).exists()
    if isUser != False:
            users = College.objects.all()
            for u in users:
                if u.emailAdd == username:
                    if decrypt(u.password) == password1:
                        user = authenticate(request, username=username, password=password1)
                        print(user)
                        if user == None:
                            User.objects.create_user(username=username, password=password1)
                            user = authenticate(request, username=username, password=password1)
                            print(user)
                        if user is not None:
                            request.session['logged_user'] = username
                            login(request, user)
                        clg=College.objects.filter(emailAdd=username)[0]
                        courses = clg.coursesOffered.split("!")
                        departments = clg.departments.split("!")
                        params = {'username': username, 'college': clg,'departments': departments, 'courses': courses}
                        return render(request, 'College/homepage.html', params)
                    else:
                        print(password1)
                        return render(request, 'College/login.html', {'pass_error': 'Incorrect Password'})

    else:
        return render(request, 'College/login.html', {'email_error': 'Invalid Email'})

def validate_college_id(request):
    clgid = request.POST.get('clgid', None)

    print(clgid)
    data = {
        'is_taken': College.objects.filter(collegeId=clgid).exists()

    }
    return JsonResponse(data)

def validate_email(request):
    email = request.POST.get('email', None)

    data = {
        'is_taken': College.objects.filter(emailAdd=email).exists()

    }
    return JsonResponse(data)