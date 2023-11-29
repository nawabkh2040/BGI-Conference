from django.contrib import admin
from django.urls import path , include
from django.conf.urls.static import static
from Reviewer import views
# from Author import views 

urlpatterns = [
  
    path('sign-up/',views.signup,name='sign-up'),
    path('',views.signin,name='sign-in'),
    path('sign-in/',views.signin,name='sign-in'),
    path('sign-out/',views.signout,name='sign-out'),
    path('dashboard/',views.dashboard,name='Reviewer-dashboard'),
    path('activate-reviewer/<str:uidb64>/<str:token>/',views.activate_reviewer,name='activate-reviewer'),
    path('list-of-submitted-paper/',views.list_of_submitted_paper,name='list-of-submitted-paper'),
    path('list-of-resubmitted-paper/',views.list_of_resubmitted_paper,name='list-of-resubmitted-paper'),
    path('review-paper/<int:paper_id>/',views.paper_reviewer,name="paper_reviewer"),
    path('re_review-paper/<int:paper_id>/',views.paper_re_reviewer,name="paper_re_reviewer"),
    path('profile/',views.reviewer_profile,name='dashboard'),


    

]