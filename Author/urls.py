from django.contrib import admin
from django.urls import path , include
from conference import settings
from Author import views
from django.conf.urls.static import static


urlpatterns = [
    path('',views.Author,name='Author'),
    path('sign-up/',views.signup,name='sign-up'),
    path('sign-in/',views.signin,name='sign-in'),
    path('sign-out/',views.signout,name='sign-out'),
    path('activate/<str:uidb64>/<str:token>/',views.activate,name="activate"),
    path('dashboard/',views.Author_dashboard,name='Author_dashboard'),
    path('conference_details/<int:conf_id>/', views.conference_details, name='conference_details'),
    path('list-of-Papers/<int:conf_id>/',views.list_of_paper,name="list_of_paper"),
    path('submit/<int:conf_id>/',views.paper_submit,name="submit"),
    path('resubmit/<int:paper_id>/',views.paper_resubmit,name="resubmit"),
    path('list-of-conference/',views.list_of_conference,name="list_of_conference"), 

  
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)