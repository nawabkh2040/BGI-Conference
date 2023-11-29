from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model 


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',
        related_query_name='user'
    )

    name = models.CharField(max_length=25,default="None")
    email = models.EmailField(unique=True)
    number = models.CharField(max_length=15,default="None")
    password = models.CharField(max_length=500)
    date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_auth = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)
    is_conference_admin = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'number']

    def __str__(self):
        return self.email

    username = models.CharField(max_length=70, null=True, blank=True)


class ReviewerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, limit_choices_to={'is_reviewer': True})
    reviewer_id = models.IntegerField(default=1)
    highest_qualifications = models.CharField(max_length=100)
    experience = models.CharField(max_length=50)
    designations = models.CharField(max_length=50)
    organization = models.CharField(max_length=100)
    whatsapp_number = models.CharField(max_length=15)
    email_address = models.EmailField()
    profile_photo = models.ImageField(upload_to='reviewer/profile_photos/', null=True, blank=True)
    resume = models.FileField(upload_to='reviewer/resumes/', null=True, blank=True)
    is_ok = models.BooleanField(default=False)
    is_mail_verify = models.BooleanField(default=False)


class Conference(models.Model):
    CONFERENCE_MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ]

    conference_id = models.AutoField(primary_key=True)
    conference_name = models.CharField(max_length=50)
    conference_description = models.CharField(max_length=225,blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,limit_choices_to={'is_conference_admin': True})
    venue = models.CharField(max_length=255)  # Assuming a simple venue field
    mode = models.CharField(max_length=10, choices=CONFERENCE_MODE_CHOICES)

    def __str__(self):
        return self.conference_name


class Paper(models.Model):
    PAPER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    title = models.CharField(max_length=255)
    paper_description = models.TextField()
    paper_start_date = models.DateTimeField(default=timezone.now)
#     end_date = models.DateTimeField()
    paper_upload = models.FileField(upload_to='papers/')
    status = models.CharField(max_length=10, choices=PAPER_STATUS_CHOICES, default='pending')
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='papers')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_auth': True})
    author_name = models.CharField(max_length=70)
    Auth_email = models.EmailField(default='example@example.com')
    Auth_affiliation = models.CharField(max_length=100, default='No affiliation')
    Auth_mobile = models.CharField(max_length=20, default='N/A')
    corresponding_auth_name = models.CharField(max_length=100, default='Unknown')
    corresponding_auth_email = models.EmailField(default='corresponding@example.com')
    corresponding_auth_affiliation = models.CharField(max_length=100, default='No affiliation')
    corresponding_auth_mobile = models.CharField(max_length=20, default='N/A')
    other_auth_name = models.CharField(max_length=100, default='Unknown')
    other_auth_email = models.CharField(max_length=150,default='other@example.com')
    other_auth_affiliation = models.CharField(max_length=100, default='No affiliation')
    other_auth_mobile = models.CharField(max_length=20, default='N/A')
    paper_keyword = models.CharField(max_length=100, default='No keywords')
    reviewer_comments = models.JSONField(default=dict, blank=True)

    def add_review(self, reviewer_name, comment, reviewer_status):
        review_data = {
            'user': reviewer_name,
            'comment': comment,
            'reviewer_status': reviewer_status,
        }
        existing_reviews = self.reviewer_comments or {}
        existing_reviews[reviewer_name] = review_data
        self.reviewer_comments = existing_reviews
        self.save()
    version = models.PositiveIntegerField(default=0)
    assigned_reviewers = models.ManyToManyField(
        CustomUser,
        limit_choices_to={'is_reviewer': True},
        related_name='assigned_papers'
    )


    def __str__(self):
        return self.title
    

class Resubmite_Paper(models.Model):
    PAPER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE, related_name='resubmissions')
    def __str__(self):
        return f"Resubmission for Paper ID: {self.paper.id} - Version {self.version}"
    title = models.CharField(max_length=255)
    paper_description = models.TextField()
    paper_start_date = models.DateTimeField(default=timezone.now)
#     end_date = models.DateTimeField()
    paper_upload = models.FileField(upload_to='Resubmited_papers/')
    status = models.CharField(max_length=10, choices=PAPER_STATUS_CHOICES, default='pending')
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='resubmissions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_auth': True})
    author_name = models.CharField(max_length=70)
    Auth_email = models.EmailField(default='example@example.com')
    Auth_affiliation = models.CharField(max_length=100, default='No affiliation')
    Auth_mobile = models.CharField(max_length=20, default='N/A')
    corresponding_auth_name = models.CharField(max_length=100, default='Unknown')
    corresponding_auth_email = models.EmailField(default='corresponding@example.com')
    corresponding_auth_affiliation = models.CharField(max_length=100, default='No affiliation')
    corresponding_auth_mobile = models.CharField(max_length=20, default='N/A')
    other_auth_name = models.CharField(max_length=100, default='Unknown')
    other_auth_email = models.CharField(max_length=150,default='other@example.com')
    other_auth_affiliation = models.CharField(max_length=100, default='No affiliation')
    other_auth_mobile = models.CharField(max_length=20, default='N/A')
    paper_keyword = models.CharField(max_length=100, default='No keywords')
    reviewer_comments = models.JSONField(default=dict, blank=True)

    def add_review(self, reviewer_name, comment, reviewer_status):
        review_data = {
            'user': reviewer_name,
            'comment': comment,
            'reviewer_status': reviewer_status,
        }
        existing_reviews = self.reviewer_comments or {}
        existing_reviews[reviewer_name] = review_data
        self.reviewer_comments = existing_reviews
        self.save()
    version = models.PositiveIntegerField(default=0)
    assigned_reviewers = models.ManyToManyField(
        CustomUser,
        limit_choices_to={'is_reviewer': True},
        related_name='re_assigned_papers'
    )

    def __str__(self):
        return self.title