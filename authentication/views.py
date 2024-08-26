from django.shortcuts import render , redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse

from django.contrib.auth import login , logout , authenticate

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes , force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .utils import account_activation_token
# Create your views here.
class UsernameValidation(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})
    


class EmailValidation(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Please enter valid email address '}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Email is already in use '}, status=409)

        return JsonResponse({'email_valid': True})


class RegistrationView(View):
    
    def get(self, request):
        return render(request,'authentication/register.html')
    def post(self, request):

        username=request.POST['username']
        email  =request.POST['email']
        passwd =request.POST['passwd']
        repasswd =request.POST['repasswd']

        context={
            'fieldValues':request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(passwd)< 8 and passwd !="":
                    messages.error(request ,"Mininum length of password must be 8")
                    return render(request, 'authentication/register.html' , context)
                else:
                    if passwd != repasswd:
                        messages.error(request ,"re-typed password doesn't matched with choosed password")
                        return render(request, 'authentication/register.html'  , context)
                    user=User.objects.create_user(username=username , email=email )
                    user.set_password(passwd)
                    user.is_active=False
                    user.save()
                    
                    uidb64=urlsafe_base64_encode(force_bytes(user.pk))
                    domain=get_current_site(request).domain
                    link=reverse('activate',kwargs={'uidb64':uidb64 , 'token':account_activation_token.make_token(user)})
                    activate_url = 'http://'+domain+link
                    msg=f"Hi {user.username},\nPlease activate your account using given link\n{activate_url}."
                    message = send_mail(
                    subject = "Account Confirmation Mail", 
                    message = msg,
                    from_email = settings.EMAIL_HOST_USER  ,
                    recipient_list= [email]
                         )
                    
                    messages.success(request ,"User has been registered successfully.Activation mail has been sent to your email address.")
                    return render(request, 'authentication/register.html')
            else:
                    messages.warning(request ,"Please fill complete information before  proceeding")
                    return render(request, 'authentication/register.html')
        return render(request, 'authentication/register.html')
    


class VerificationView(View):
    def get(self, request , uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                messages.warning(request, 'Account is already activated')
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully,Now you can login with your credientals')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')
      


class LoginView(View):

    def get(self , request):
        return render(request, 'authentication/login.html')
    
    def post(self , request):


        userid=request.POST['username']
        pwd=request.POST['passwd']
        print(pwd)

        if userid and pwd:
            usr=authenticate(username=userid , password=pwd)
            if  usr is not   None:
                if usr.is_active:
                    login(request,usr)
                    messages.success(request,f"Welcome back , {usr.get_username()}")
                    return redirect('home')
                else:
                    messages.error(request, "This account is not activated . Please check your mail.")
                    return render(request,'authentication/login.html')
            messages.error(request, "Invalid credientals,check and try again")
            return render(request,'authentication/login.html')
        messages.error(request, "PLease fill all information")
        return render(request,'authentication/login.html')



def LogoutView(request):
    logout(request)
    messages.success(request, "You have been logged out succesfully")
    return redirect('login')