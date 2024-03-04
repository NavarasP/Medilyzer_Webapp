from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
# from django.contrib.auth.tokens import account_activation_token
from .tokens import account_activation_token  # Assuming your tokens module is named tokens
from django.core.exceptions import ValidationError
from django.core.validators import validate_email




def activate(request, uidb64, token):
    # return redirect('index')
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your email has been verified. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification link. Please try again.')
            return redirect('index')  # Replace 'index' with the appropriate URL name

# from .models import Profile
def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."

    # Validate email address
    try:
        validate_email(to_email)
    except ValidationError:
        messages.error(request, f"Invalid email address: {to_email}")
        return

    message = render_to_string("verification_email.html",{
        'user' : user.username,
        'domain' : get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol' : 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[to_email])

    # Try sending the email
    try:
        email.send()
        messages.success(request, f'Dear <strong>{user}</strong>, please go to your email <strong>{to_email}</strong> inbox and click on \
            received activation link to confirm and complete the registration. <strong>Note:</strong> Check your spam folder.')
    except Exception as e:
        messages.error(request, f"Problem sending email to {to_email}. Error: {str(e)}")

def register(request):
    user = None
    error_message = None

    if request.POST:
        
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST.get('password1','')
        first_name = request.POST.get('first_name','')
        last_name = request.POST.get('last_name','')
        email = request.POST.get('email','')
        # password1 = request.POST.get('password1')

        if len(password)<8:
            error_message = "Please enter minimum 8 characters as password."
         # Check if password and confirm_password match
            if password != confirm_password:
                error_message = "Passwords do not match. Please enter matching passwords."
                # return render(request, 'register.html')

        else:

            try:
                # Create the user
                user = User.objects.create_user(username=username,password=password,first_name=first_name,last_name=last_name,email=email)
                if user is not None:
                    # form = user.save(commit=False)
                    user.is_active = False
                    user.save()
                    # send_verification_email(user)
                    activateEmail(request, user, email)
                    return redirect('index')
            except IntegrityError:
                error_message = "Username is already taken. Please choose a different one."
                # profile = Profile.objects.create(user=user,first_name=first_name,last_name=last_name,email=email)
            except Exception as e:
                error_message=str(e)
                # messages.success(request, 'Account created successfully.')
                # return redirect('login_user')
            if user:
                return redirect('login')

    return render(request, 'register.html', {'user': user, 'error_message': error_message})


def verify_email(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid verification link. Please try again.')
        return redirect('index')


# --------------------login--------------------------

def login(request):
    error_message = None
    if request.user.is_authenticated:
        return redirect('index')
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        if not username or not password:
            messages.error(request, 'Please fill out both username and password.')
            return render(request, 'login.html')

        user=authenticate(username=username,password=password)
        if user:
            auth_login(request,user)
            return redirect('index')
        else:
            # error_message='invalid credentials'
            messages.error(request,'Invalid username or password.')
        
            # Create the user

            # messages.success(request, 'Account created successfully.')
            # return redirect('list')


    return render(request, 'login.html')

# ---------------------------logout---------------------------
def logout(request):
    # Deactivate the user upon logout
    if request.user.is_authenticated and not request.user.is_superuser:
        request.user.is_active = False
        request.user.save()

    # Perform the actual logout
    auth_logout(request)
    return redirect('index')