from django.contrib import admin
from Author.models import CustomUser, Conference, Paper, Resubmite_Paper, ReviewerProfile


class CustomUserAdmin_by(admin.ModelAdmin):
    list_display=('name','id','email','number','date','is_active','is_staff','is_conference_admin','is_reviewer','is_auth','password')
admin.site.register(CustomUser,CustomUserAdmin_by)

class conference_admin(admin.ModelAdmin):
    list_display=('conference_id','conference_name','conference_description','start_date','end_date','user','venue','mode')
admin.site.register(Conference,conference_admin)

class ReviewerProfileAdmin(admin.ModelAdmin):
    list_display=('user','reviewer_id','highest_qualifications','experience','designations','organization','whatsapp_number','email_address','is_mail_verify','is_ok','profile_photo','resume')
admin.site.register(ReviewerProfile,ReviewerProfileAdmin)


class paper_admin(admin.ModelAdmin):
    list_display=('title','id','author_name','paper_description','version','paper_upload','user','conference','status','Auth_email','Auth_affiliation','Auth_mobile','corresponding_auth_name','corresponding_auth_email','corresponding_auth_affiliation','corresponding_auth_mobile','other_auth_name','other_auth_email','other_auth_affiliation','other_auth_mobile','paper_keyword','reviewer_comments','status','paper_start_date')
admin.site.register(Paper,paper_admin)



class Resubmite_Paper_Admin(admin.ModelAdmin):
    list_display=('title','id','paper_id','version','author_name','paper_description','paper_upload','user','Auth_email','Auth_affiliation','Auth_mobile','corresponding_auth_name','corresponding_auth_email','corresponding_auth_affiliation','corresponding_auth_mobile','other_auth_name','other_auth_email','other_auth_affiliation','other_auth_mobile','paper_keyword','reviewer_comments','status','paper_start_date')
admin.site.register(Resubmite_Paper,Resubmite_Paper_Admin)