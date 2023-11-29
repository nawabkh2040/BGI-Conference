from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from Author.models import CustomUser, Conference, Paper, Resubmite_Paper, ReviewerProfile
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

def signin(request):
     if request.user.is_authenticated and request.user.is_conference_admin:
          login(request,request.user)
          return redirect('conference-dashboard')
     if request.method == "POST":
          email = request.POST.get('email')
          password = request.POST.get('password')
          user = authenticate(request,email=email,password=password)
          if user is not None:
               if user.is_conference_admin:
                    login(request, user)
                    return redirect('conference-dashboard')
               else:
                    context={
                         'error_message':"You are not Conference Admin"
                    }
                    return render(request, 'conferenceadmin/sign-in.html',context)
          else:
               context={
                    'error_message':"Please Enter Valid Email And Password"
               }
               return render(request, 'conferenceadmin/sign-in.html',context)
     else:
          return render(request,'conferenceadmin/sign-in.html')


def signup(request):
     if request.method == "POST":
          name = request.POST.get('name')
          email= request.POST.get('email')
          number = request.POST.get('number')
          password = request.POST.get('password')
          if CustomUser.objects.filter(email=email).exists():
               context = {'error_message': 'This email is already registered.'}
               return render(request,'conferenceadmin/sign-up.html',context)
          new_admin = CustomUser.objects.create_user(
               name=name,
               email=email,
               number=number,
               password=password,
          )
          new_admin.save()
          subject="Email Verification Conference to Conference Admin"
          from_email=settings.EMAIL_HOST_USER
          to_list = [email]
          current_site = get_current_site(request)
          uidb64 = urlsafe_base64_encode(force_bytes(new_admin.id))
          token = default_token_generator.make_token(new_admin)
          context_email={
              'name':name,
              'domain':current_site.domain,
              'uidb64':uidb64,
              'token':token,
          }
          messages=render_to_string('conferenceadmin/email_confirmation.html',context_email)
          try:
              send_mail(subject,messages,from_email,to_list,fail_silently=True)
              context_success = {
                   'success_message': 'Your Account Create Successfully. Please Check Your Email and Verify'
                   }
              return render(request, 'conferenceadmin/sign-up.html',context_success)
          except Exception as e:
              print(e)
              context_failed={
                   'error_message':"There is a problem to send the email please contact us to verify  "
              }
              return render(request, 'conferenceadmin/sign-up.html',context_failed)
     return render(request, 'conferenceadmin/sign-up.html')


def activate_conference_admin(request, uidb64, token):
     try:
        uidb64 = force_str(urlsafe_base64_decode(uidb64))
        my_user = CustomUser.objects.get(id=uidb64)
     except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        my_user = None
     if my_user is not None and default_token_generator.check_token(my_user,token):
        email=my_user.email
        new_admin = CustomUser.objects.get(email=email)
        new_admin.is_conference_admin = True
        login(request,my_user)
        return redirect('conference-dashboard')
     else:
        return render(request,'conferenceadmin/activation-failed.html')



def conference_dashboard(request):
     if request.user.is_authenticated and request.user.is_conference_admin:
          user = request.user
          context = {
               'user':user,
          }
          return render(request,'conferenceadmin\dashboard_conf.html',context)
     else:
          return redirect('sign-out')
     
     
def signout(request):
     logout(request)
     return redirect('sign-in')

def create_conference(request):
     if request.user.is_authenticated and request.user.is_conference_admin:
          user=request.user
          if request.method == "POST":
               conference_name = request.POST.get('conference_name')
               conference_description = request.POST.get('conference_description')
               conference_mode = request.POST.get('conference_mode')
               conference_venue = request.POST.get('conference_venue')
               conference_end_date = request.POST.get('conference_end_date')
               new_conference = Conference.objects.create(
                    conference_name=conference_name,
                    conference_description=conference_description,
                    end_date=conference_end_date,
                    user=user,
                    venue=conference_venue,
                    mode=conference_mode,
               )
               new_conference.save()
               context={
                    'success_message':"Conference Created Successfully",
                    'user':user,
                    'conference':Conference.objects.all()
               }
               return render(request,"conferenceadmin\create-conference.html",context)
          else:
               context={
                    'user':user,
                    'conference':Conference.objects.all()
               }
               return render(request,"conferenceadmin\create-conference.html",context)
     else:
          return redirect('sign-out')

def list_of_conferences(request):
     if request.user.is_authenticated and request.user.is_conference_admin:
          user = request.user
          # conference = get_object_or_404(Conference, user=user)
          conference = Conference.objects.filter(user=user)
          print(conference)
          context = {
               'conference':conference,
               'user':user,
          }
          return render(request,"conferenceadmin\list-of-conference.html",context)
     else:
          return redirect("sign-out")

def list_of_reviewer(request):
     if request.user.is_authenticated and request.user.is_conference_admin:
          if request.method == "POST":
               user_id = request.POST.get('user_id')
               is_ok = request.POST.get('is_ok') == 'true'
               try:
                    reviewer = ReviewerProfile.objects.get(reviewer_id=user_id)
                    reviewer.is_ok = is_ok
                    reviewer.save()
                    return JsonResponse({'status': 'success'})
               except ReviewerProfile.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Reviewer not found'})

          reviewer = ReviewerProfile.objects.all()
          context = {
               'reviewer':reviewer,
          }
          return render(request,"conferenceadmin\list-of-reviewer.html",context)
     else:
          return redirect("sign-out")

def Assign_paper(request):
     if request.user.is_authenticated and request.user.is_conference_admin:
          reviewer = ReviewerProfile.objects.all()
          context = {
               'reviewer':reviewer,
          }
          return render(request,"conferenceadmin/assign-paper-reviewer.html",context)
     else:
          return redirect("sign-out")

def Assign_reviewer_paper(request, reviewer_id):
     if request.user.is_authenticated and request.user.is_conference_admin:
          reviewer = ReviewerProfile.objects.get(reviewer_id=reviewer_id)
          paper = Paper.objects.all()
          resubmit_paper = Resubmite_Paper.objects.all()
          if request.method == "POST":
               selected_paper_ids = request.POST.getlist('papers_to_assign')
               for id in selected_paper_ids:
                    papers1 = Paper.objects.get(id=id)
                    papers1.assigned_reviewers.add(reviewer.user)
                    papers1.save()
               return redirect('Assign-paper')
          context = {
               'papers':paper,
               'reviewer':reviewer,
               'resubmit_paper':resubmit_paper,
          }
          return render(request,"conferenceadmin/list-of-paper-sign.html",context)

     else:
          return redirect("sign-out")

def Assign_reviewer_paper_re(request, reviewer_id):
     if request.user.is_authenticated and request.user.is_conference_admin:
          reviewer = ReviewerProfile.objects.get(reviewer_id=reviewer_id)
          paper = Paper.objects.all()
          resubmit_paper = Resubmite_Paper.objects.all()
          if request.method == "POST":
               selected_paper_ids = request.POST.getlist('papers_to_assign')
               for id in selected_paper_ids:
                    papers1 = Resubmite_Paper.objects.get(id=id)
                    papers1.assigned_reviewers.add(reviewer.user)
                    papers1.save()
               return redirect('Assign-paper')
          context = {
               'papers':paper,
               'reviewer':reviewer,
               'resubmit_paper':resubmit_paper,
          }
          return render(request,"conferenceadmin/list-of-paper-sign.html",context)

     else:
          return redirect("sign-out")


def list_of_paper(request, conference_id):
     if request.user.is_authenticated and request.user.is_conference_admin:
          user=request.user
          conference = get_object_or_404(Conference, conference_id=conference_id)
          paper = Paper.objects.filter(conference=conference)
          resubmite_Paper = Resubmite_Paper.objects.filter(conference=conference)
          context={
               'user':user,
               'paper':paper,
               'reviewer':ReviewerProfile.objects.all(),
               'reupload_paper':resubmite_Paper,
          }
          return render(request, "conferenceadmin\list-of-paper.html",context)
     else:
          return redirect("sign-out")

def update_paper_status(request, paper_id):
    if request.user.is_authenticated and request.user.is_conference_admin and request.method == 'POST':
        new_status = request.POST.get('status')
        papers = get_object_or_404(Paper, id=paper_id)
        papers.status = new_status
        papers.save()
        return redirect('list-of-conferences')
    else:
     return redirect("sign-out")

def resubmit_paper_status(request, paper_id):
    if request.user.is_authenticated and request.user.is_conference_admin and request.method == 'POST':
        new_status = request.POST.get('status')
        papers = get_object_or_404(Resubmite_Paper, id=paper_id)
        papers.status = new_status
        papers.save()
        return redirect('list-of-conferences')
    else:
     return redirect("sign-out")
        
def reviewer_profile(request, reviewer_id):
     if request.user.is_authenticated and request.user.is_conference_admin:
          account = get_object_or_404(CustomUser, id = reviewer_id)
          reviewer = get_object_or_404(ReviewerProfile, user=account)
          context={
               'reviewer':reviewer,
          }
          return render(request, "conferenceadmin/reviewer-profile.html",context)
     else:
          return redirect("sign-out")


     