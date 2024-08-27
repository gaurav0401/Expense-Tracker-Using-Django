from django.contrib import admin
from django.urls import path
from .views import RegistrationView , UsernameValidation ,EmailValidation , VerificationView , LoginView , LogoutView , ResetPassword , CompletePasswordReset
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('register', RegistrationView.as_view() , name="register"),
    path('validate-username', csrf_exempt( UsernameValidation.as_view()) , name="namevalidation"),
    path('validate-email', csrf_exempt( EmailValidation.as_view()) , name="emailvalidation"),
    path('login' , LoginView.as_view() , name="login"),
    path('logout' , LogoutView , name="logout"),
    path('activate/<uidb64>/<token>' , VerificationView.as_view() , name='activate'),
    path('reset-passwd' , ResetPassword.as_view() , name="reset-passwd"),
    path('set-new-pass/<uidb64>/<token>' , CompletePasswordReset.as_view() , name='reset-pass'),

]
