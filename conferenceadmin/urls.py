from django.contrib import admin
from django.urls import path , include
from conference import settings
from conferenceadmin import views
from django.conf.urls.static import static


urlpatterns = [
    path('sign-in/',views.signin,name='sign-in'),
    path('sign-up/',views.signup,name='sign-up'),
    path('sign-out/',views.signout,name='sign-out'),
    path('dashboard/',views.conference_dashboard,name='conference-dashboard'),
    path('Activate-Conference-Admin/<str:uidb64>/<str:token>/',views.activate_conference_admin,name='Activate-Conference-Admin'),
    path('create-conference/',views.create_conference,name='create-conference'),
    path('list-of-conferences/',views.list_of_conferences,name='list-of-conferences'),
    path('list-of-reviewers/',views.list_of_reviewer,name='list-of-reviewer'),
    path('reviewer-profile/<int:reviewer_id>/',views.reviewer_profile,name='reviewer-profile'),
    path('list-of-paper/<int:conference_id>/',views.list_of_paper,name='list-of-paper'),
    path('update-paper-status/<int:paper_id>/',views.update_paper_status,name='update-paper-status'),
    path('resubmit-paper-status/<int:paper_id>/',views.resubmit_paper_status,name='resubmit-paper-status'),
    path('Assign-paper/',views.Assign_paper,name='Assign-paper'),
    path('Assign-reviewer-paper/<int:reviewer_id>/',views.Assign_reviewer_paper,name='Assign-reviewer-paper'),
    path('Assign-reviewer-paper-re/<int:reviewer_id>/',views.Assign_reviewer_paper_re,name='Assign-reviewer-paper-re'),







]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)