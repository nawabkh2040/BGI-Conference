from django.shortcuts import render , redirect , HttpResponse
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from Author.models import CustomUser, Paper, Conference, Resubmite_Paper
from conference.settings import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import * 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
import smtplib
from django.shortcuts import render, get_object_or_404, redirect


# Create your views here.
def Author(request):
     return redirect('sign-up')

def signup(request):
     if request.method == "POST":
          email = request.POST.get('email')
          password = request.POST.get('password')
          name = request.POST.get('name')
          number = request.POST.get('number')
          if CustomUser.objects.filter(email=email).exists():
               context = {'error_message': 'This email is already registered.'}
               return render(request,'Author/sign-up.html',context)
          else:
               new_user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    name=name,
                    number=number,
               )
               new_user.is_active=True
               new_user.is_auth=False
               subject="Email Verification to Conference"
               from_email=settings.EMAIL_HOST_USER
               to_list = [new_user.email]
               current_site = get_current_site(request)
               uidb64 = urlsafe_base64_encode(force_bytes(new_user.id))
               token = default_token_generator.make_token(new_user)
               context_email={
                    'name':new_user.name,
                    'domain':current_site.domain,
                    'uidb64': uidb64,
                    'token': token,
               }
               messages=render_to_string('Author/email_confirmation.html',context_email)
               try:
                    send_mail(subject,messages,from_email,to_list,fail_silently=True)
                    context_success = {'success_message': 'Your Account Create Successfully. Please Check Your Email and Verify It  :-) '}
                    return render(request,'Author/sign-up.html',context_success)
               except Exception as e:
                     print("SMTP Email Send Error Occurs ",e)
                     context_failed = {'error_message': 'Your Account Create Successfully. There is a problem to sending mail But You Can login  :-) '}
                     return render(request,'Author/sign-up.html',context_failed)
     else:
          return render(request,'Author/sign-up.html')

def signin(request):
     if request.user.is_authenticated:
          return redirect('Author_dashboard')
     if request.method == "POST":
          email=request.POST.get('email')
          password=request.POST.get('password')
          user = authenticate(request,email=email,password=password)
          if user is not None:
            if user.is_auth:
               login(request,user)
               return redirect('Author_dashboard')
            else:
                 context={
                      'error_message':"You are not a Author"
                 }
                 return render(request,'Author/sign-in.html', context)
          else:
               context = {'error_message': 'Invalid email or password'}
               return render(request,'Author/sign-in.html', context)
     else:
          return render(request,'Author/sign-in.html')
     
def Author_dashboard(request):
     if request.user.is_authenticated:
          author=request.user
          if author.is_auth:
               context={
                    'uname':author.name,
                    'conference':Conference.objects.all()
               }
               return render(request,'Author/Dashboard.html',context)
          else:
               return HttpResponse("Please Verify Your Account.We sended You a mail please verify yourself for Again Send the mail please contact us ")
     else:
          return redirect('sign-in')
def signout(request):
     logout(request)
     return redirect('home')

def activate(request, uidb64, token):
    try:
        uidb64 = force_str(urlsafe_base64_decode(uidb64))
        my_user = CustomUser.objects.get(id=uidb64)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        my_user = None
    if my_user is not None and default_token_generator.check_token(my_user,token):
        my_user.is_active = True
        my_user.is_auth = True
        my_user.save()
        login(request,my_user)
        return redirect('Author_dashboard')
    else:
         return render(request,'Author/email_activation_failed.html')
    
def conference_details(request, conf_id):
     if request.user.is_authenticated and request.user.is_auth:
          conf_instance = get_object_or_404(Conference, conference_id=conf_id)
          user = request.user
          context={
               'user':user,
               'conf_instance':conf_instance,
               'paper_uploaded':Paper.objects.filter(user=user,conference=conf_instance)
          }
          return render(request,'Author/conference_details.html',context)
     else:
          return redirect('sign-in')
     
def list_of_paper(request, conf_id):
     if request.user.is_authenticated and request.user.is_auth:
          user = request.user
          conference=Conference.objects.get(conference_id=conf_id)
          context={
               'paper':Paper.objects.filter(user=user,conference=conference),
               'Resubmited_paper':Resubmite_Paper.objects.filter(user=user,conference=conference)
          }
          return render(request,'Author/list-of-paper.html',context)
     else:
          return redirect('sign-in')
     
def list_of_conference(request):
     if request.user.is_authenticated and request.user.is_auth:
          user = request.user
          context={
               'conference':Conference.objects.all()
          }
          return render(request,'Author/list-of-conference.html',context)
          
     else:
          return redirect('sign-in')
     

def paper_submit(request, conf_id):
     if request.user.is_authenticated and request.user.is_auth:
          user = request.user
          conf_instance = get_object_or_404(Conference, conference_id=conf_id)
          if request.method == "POST":
               title_paper = request.POST.get('title_paper')
               Auth_email = request.POST.get('Auth_email')
               Auth_name = request.POST.get('Auth_name')
               Auth_affiliation = request.POST.get('Auth_affiliation')
               Auth_mobile = request.POST.get('Auth_mobile')
               corresponding_auth_name = request.POST.get('corresponding_auth_name')
               corresponding_auth_email = request.POST.get('corresponding_auth_email')
               corresponding_auth_affiliation = request.POST.get('corresponding_auth_affiliation')
               corresponding_auth_mobile = request.POST.get('corresponding_auth_mobile')
               other_auth_name = request.POST.get('other_auth_name')
               other_auth_email = request.POST.get('other_auth_email')
               other_auth_affiliation = request.POST.get('other_auth_affiliation')
               other_auth_mobile = request.POST.get('other_auth_mobile')
               paper_keyword = request.POST.get('paper_keyword')
               paper_description = request.POST.get('paper_description')
               pdf_upload = request.FILES.get('pdf_upload')
               new_paper=Paper.objects.create(
                    user=user,
                    title=title_paper,
                    paper_description=paper_description,
                    Auth_mobile=Auth_mobile,
                    Auth_affiliation=Auth_affiliation,
                    Auth_email=Auth_email,
                    author_name=Auth_name,
                    corresponding_auth_affiliation=corresponding_auth_affiliation,
                    corresponding_auth_email=corresponding_auth_email,
                    corresponding_auth_mobile=corresponding_auth_mobile,
                    corresponding_auth_name=corresponding_auth_name,
                    other_auth_name=other_auth_name,
                    other_auth_affiliation=other_auth_affiliation,
                    other_auth_email=other_auth_email,
                    other_auth_mobile=other_auth_mobile,
                    paper_keyword=paper_keyword,
                    paper_upload=pdf_upload,
                    status='pending',
                    conference=conf_instance,
               )
               new_paper.save()
               subject="Paper id From Conference"
               from_email=settings.EMAIL_HOST_USER
               to_list = [Auth_email]
               context_mail_to = {
                    'name':Auth_name,
                    'id':new_paper.id
               }
               messages=render_to_string('Author/email_paper.html',context_mail_to)
               try:
                    send_mail(subject,messages,from_email,to_list,fail_silently=True)
                    context={
                    'success_message':"Paper uploaded Successfully. Please Check You mail",
                    'conf_instance':conf_instance
                    }
                    return render(request,'Author/paper_submit.html',context)
               except Exception as e:
                    print("SMTP Email Send Error Occurs ",e)
                    context={
                         'success_message':"Paper uploaded Successfully",
                         'conf_instance':conf_instance
                         }
                    return render(request,'Author/paper_submit.html',context)
          else:     
               context={
                    'conf_instance':conf_instance
               }
               return render(request,'Author/paper_submit.html',context)
     else:
          return redirect('sign-in')
     
def paper_resubmit(request, paper_id):
     if request.user.is_authenticated and request.user.is_auth:
          user=request.user
          paper_instance = get_object_or_404(Paper, id=paper_id)
          conference=paper_instance.conference
          if request.method =="POST":
               title_paper = request.POST.get('title_paper')
               Auth_name = request.POST.get('Auth_name')
               paper_keyword = request.POST.get('paper_keyword')
               paper_description = request.POST.get('paper_description')
               pdf_upload = request.FILES.get('pdf_upload')
               resubmite_Paper = Resubmite_Paper.objects.create(
                    user=user,
                    conference=conference,
                    paper=paper_instance,
                    title=title_paper,
                    author_name=Auth_name,
                    paper_description=paper_description,
                    paper_keyword=paper_keyword,
                    paper_upload=pdf_upload,
                    Auth_mobile=paper_instance.Auth_mobile,
                    Auth_affiliation=paper_instance.Auth_affiliation,
                    Auth_email=paper_instance.Auth_email,
                    corresponding_auth_affiliation=paper_instance.corresponding_auth_affiliation,
                    corresponding_auth_email=paper_instance.corresponding_auth_email,
                    corresponding_auth_mobile=paper_instance.corresponding_auth_mobile,
                    corresponding_auth_name=paper_instance.corresponding_auth_name,
                    other_auth_name=paper_instance.other_auth_name,
                    other_auth_affiliation=paper_instance.other_auth_affiliation,
                    other_auth_email=paper_instance.other_auth_email,
                    other_auth_mobile=paper_instance.other_auth_mobile,
                    version= paper_instance.version +1

               )
               # resubmite_Paper.version + 1
               paper_instance.version += 1
               paper_instance.save()
               resubmite_Paper.save()
               context={
                    'original_paper':paper_instance,
                    'name':user.name,
                    'conference':conference,
                    'success_message':"Paper Resubmited SuccessFully"
               }
               return render(request, 'Author/paper_resubmit.html',context)


          else:
               context={
                    'original_paper':paper_instance,
                    'name':user.name,
                    'conference':conference,
               }
               return render(request, 'Author/paper_resubmit.html',context)

     else:
          return redirect('sign-in')
