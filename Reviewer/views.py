from django.shortcuts import render, redirect, HttpResponse
from Author.models import CustomUser, ReviewerProfile, Paper, Resubmite_Paper
from django.contrib.auth import authenticate, login, logout
from conference import settings
from django.contrib import messages

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



def signup(request):
     if request.method == "POST":
         name = request.POST.get('name')
         qualification = request.POST.get('qualification')
         experience = request.POST.get('experience')
         designations = request.POST.get('designations')
         organization = request.POST.get('organization')
         number = request.POST.get('number')
         whats_app_number = request.POST.get('whats_app_number')
         email_reviewer = request.POST.get('email_reviewer')
         password_reviewer = request.POST.get('password_reviewer')
         photo_upload = request.FILES.get('photo_upload')
         resume_upload = request.FILES.get('resume_upload')
         if CustomUser.objects.filter(email=email_reviewer).exists():
               context = {'error_message': 'This email is already registered.'}
               return render(request,'Reviewer/sign-up.html',context)
         new_reviewer=CustomUser.objects.create_user(
              name=name,
              number=number,
              email=email_reviewer,
              password=password_reviewer,
         )
         new_reviewer.is_reviewer=True
         new_reviewer.save()
         add_reviewer=ReviewerProfile.objects.create(
              highest_qualifications=qualification,
              experience=experience,
              designations=designations,
              organization=organization,
              whatsapp_number=whats_app_number,
              profile_photo=photo_upload,
              resume=resume_upload,
              email_address=email_reviewer,
              user=new_reviewer
         )
         add_reviewer.reviewer_id = new_reviewer.id
         add_reviewer.save()
         subject="Email Verification Conference to Reviewer"
         from_email=settings.EMAIL_HOST_USER
         to_list = [email_reviewer]
         current_site = get_current_site(request)
         uidb64 = urlsafe_base64_encode(force_bytes(new_reviewer.id))
         token = default_token_generator.make_token(new_reviewer)
         context_email={
              'name':new_reviewer.name,
              'domain':current_site.domain,
              'uidb64':uidb64,
              'token':token,
         }
         messages=render_to_string('Reviewer/email_confirmation.html',context_email)
         try:
              send_mail(subject,messages,from_email,to_list,fail_silently=True)
              context_success = {
                   'success_message': 'Your Account Create Successfully. Please Check Your Email and Verify'
                   }
              return render(request, 'Reviewer/sign-up.html',context_success)
         except Exception as e:
              print(e)
              context_failed={
                   'error_message':"There is a problem to send the email please contact us to verify  "
              }
              return render(request, 'Reviewer/sign-up.html',context_failed)
     else:    
          return render(request, 'Reviewer/sign-up.html')




def signin(request):
     if request.user.is_authenticated and request.user.is_reviewer:
          user=request.user
          login(request, user)
          return redirect('Reviewer-dashboard')
     if request.method == "POST":
          email = request.POST.get('email')
          password = request.POST.get('password')
          user = authenticate(request,email=email,password=password)
          if user is not None:
               if user.is_reviewer:
                    login(request, user)
                    return redirect('Reviewer-dashboard')
               else:
                    context={
                         'error_message':"You are not a Reviewer "
                    }
                    return render(request, 'Reviewer/sign-in.html',context)
          else:
               context={
                    'error_message':"Please Enter the valid Email and Password"
               }
               return render(request, 'Reviewer/sign-in.html',context)
     else:
          return render(request, 'Reviewer/sign-in.html')
     

def dashboard(request):
     if request.user.is_authenticated and request.user.is_reviewer:
          user=request.user
          try:
               reviewer = ReviewerProfile.objects.get(email_address=user.email)
          except Exception as e:
               print(e)
               return redirect('sign-out')
          if reviewer.is_mail_verify:
               if reviewer.is_ok:
                    context={
                         'reviewer':reviewer,
                         'user':user,
                    }
                    return render(request,'Reviewer/dashboard.html',context)
               else:
                    return HttpResponse("Admin Deactivated Your Account please wait")
          else:
               return HttpResponse("Please Verify your Email")
     else:
          return redirect('sign-in')
     
def signout(request):
     logout(request)
     return redirect('sign-in')


def activate_reviewer(request, uidb64, token):
     try:
        uidb64 = force_str(urlsafe_base64_decode(uidb64))
        my_user = CustomUser.objects.get(id=uidb64)
     except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        my_user = None
     if my_user is not None and default_token_generator.check_token(my_user,token):
        email=my_user.email
        reviewer = ReviewerProfile.objects.get(email_address=email)
        reviewer.is_mail_verify=True
        reviewer.save()
        login(request,my_user)
        return redirect('Reviewer-dashboard')
     else:
        return render(request,'Reviewer/activation-failed.html')
     
def list_of_submitted_paper(request):
     if request.user.is_authenticated and request.user.is_reviewer:
          user = request.user
          reviewer = ReviewerProfile.objects.get(email_address=user.email)
          if reviewer.is_mail_verify:
               if reviewer.is_ok:
                    paper = Paper.objects.filter(assigned_reviewers=reviewer.user)
                    context={
                         'reviewer':reviewer,
                         'papers':paper,
                    }
                    return render(request,'Reviewer/submitted_paper.html',context)
               else:
                    return HttpResponse("Admin Deactivated Your Account please wait")
          else:
               return HttpResponse("please Verify Your Email First")
     else:
          return redirect('sign-in')


def list_of_resubmitted_paper(request):
     if request.user.is_authenticated and request.user.is_reviewer:
          user = request.user
          reviewer = ReviewerProfile.objects.get(email_address=user.email)
          if reviewer.is_mail_verify:
               if reviewer.is_ok:
                    paper = Resubmite_Paper.objects.filter(assigned_reviewers=reviewer.user)
                    context={
                         'reviewer':reviewer,
                         'paper':paper,
                    }
                    return render(request,'Reviewer/resubmitted_paper.html',context)
               else:
                   return HttpResponse("Admin Deactivated Your Account please wait") 
          else:
               return HttpResponse("please Verify Your Email First")
     else:
          return redirect('sign-in')
     
def paper_reviewer(request, paper_id):
     if request.user.is_authenticated and request.user.is_reviewer:
          user = request.user
          reviewer = ReviewerProfile.objects.get(email_address=user.email)
          if reviewer.is_ok:
               paper = get_object_or_404(Paper, id=paper_id)
               if request.method == "POST":
                    comment = request.POST.get('comment')
                    reviewer_status = request.POST.get('reviewer_status')
                    print(reviewer_status)
                    paper.add_review(request.user.name, comment, reviewer_status)
                    paper.save()
                    messages.success(request,"Comment Successfully Submit")
                    context = {
                         'reviewer':reviewer,
                         'paper':paper,
                         'success_message':"Comment Successfully Submit",
                    }
                    return render(request,'Reviewer/paper_review.html',context)
               paper = Paper.objects.get(id=paper_id)
               context={
                    'reviewer':reviewer,
                    'paper':paper,
                    'paper_id':paper_id,
               }
               return render(request,'Reviewer/paper_review.html',context)
          else:
               return HttpResponse("please Verify Your Email First")
     else:
          return redirect('sign-in')
     
def paper_re_reviewer(request, paper_id):
     if request.user.is_authenticated and request.user.is_reviewer:
          user = request.user
          reviewer = ReviewerProfile.objects.get(email_address=user.email)
          if reviewer.is_ok:
               re_paper = get_object_or_404(Resubmite_Paper, id=paper_id)
               if request.method == "POST":
                    comment = request.POST.get('comment')
                    reviewer_status = request.POST.get('reviewer_status')
                    re_paper.add_review(request.user.name, comment, reviewer_status)
                    re_paper.save()
                    # messages.success(request,"Comment Successfully Submit")
                    context = {
                         'reviewer':reviewer,
                         'paper':re_paper,
                         'success_message':"Comment Successfully Submit",

                    }
                    return render(request,'Reviewer/paper_re_review.html',context)
               context={
                    'reviewer':reviewer,
                    'paper':re_paper,
                    'paper_id':paper_id,
               }
               return render(request,'Reviewer/paper_re_review.html',context)
          else:
               return HttpResponse("please Verify Your Email First")
     else:
          return redirect('sign-in')
def reviewer_profile(request):
     if request.user.is_authenticated and request.user.is_reviewer:
          user = request.user
          reviewer = ReviewerProfile.objects.get(email_address=user.email)
          if reviewer.is_ok:
               context={
                    'reviewer':reviewer,
                    'user':user,
               }
               return render(request, 'Reviewer/reviewer_profile.html',context)
          else:
               return HttpResponse("please Verify Your Email First")
     else:
          return redirect('sign-in')