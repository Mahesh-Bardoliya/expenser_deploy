from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
import re   
from django.shortcuts import redirect,render
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
from django.contrib import auth
# Create your views here.

class EmailValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        email=data.get('email','')
        if not re.match(r'^\S+@\S+\.\S+$', email):
            return JsonResponse({'email_error':'Email is invalid.'},status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Sorry email already exist. Try another one.'},status=409)
        return JsonResponse({'email_valid':True})


class UsernameValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        username=data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'Username should be alphabetic only.'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Sorry username already exist. Try another one.'},status=409)
        return JsonResponse({'username_valid':True})

class RegistraionView(View):
    def get(self, request):
        return render(request,'authentication/register.html')
    def post(self, request):
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        context={
            'fieldValues':request.POST
        }
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,'Password must be at least 6 characters')
                    return render(request,'authentication/register.html',context)

                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active=False
                user.save()
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain=get_current_site(request).domain
                link=reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
                activate_link = 'http://'+domain+link
                emailsubject = 'Activate your account.'
                emailbody = 'hi '+user.username+'. please activate your account\n'+activate_link
                email = EmailMessage(
                    emailsubject,
                    emailbody,
                    'noreply@semycolon.com',
                    [email],
                )
                email.send(fail_silently=False)
                
                messages.success(request,'Account was successfully registered.')
                return render(request,'authentication/register.html')
        return render(request,'authentication/register.html')   
    

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id=force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()
            messages.success(request,"account activated successfully")
            return redirect('login')


        except Exception as ex:
            pass

        return redirect('login')
        

class LoginView(View):
    def get(self, request):
        return render(request,'authentication/login.html')   
    def post(self, request):
        username=request.POST["username"]
        password=request.POST["password"]

        if username and password:
            user=auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request,user)
                   
                    return redirect('dashboard')
                messages.error(request,"Account is not active. Please check your mail box.")
                return render(request,'authentication/login.html')
            messages.error(request,"Invalid user candidates. Please try again.")
            return render(request,'authentication/login.html')
        messages.error(request,"Looks like your forgot to add your candidates. Try again.") 
        return render(request,'authentication/login.html')
    
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request,"Your have been logged out")
        return redirect('login')