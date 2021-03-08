from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User Model"""
    full_name = models.CharField(default='', max_length=256)
    email = models.EmailField(default='', max_length=256, unique=True)
    password = models.CharField(default='', max_length=100)
    confirm_password = models.CharField(default='', max_length=100)
    country_code = models.IntegerField(null=True, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='media', null=True, blank=True)
    is_user = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    # REQUIRED_FIELDS = ['full_name']
    class Meta:
        ordering = ('-created_at',)


class Category(models.Model):
    """Category model"""
    category_name = models.CharField(default='', max_length=300)
    category_image = models.ImageField(upload_to='media', null=True, blank=True)


class SubCategory(models.Model):
    """Sub Category Model"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category_name = models.CharField(default='', max_length=300)
    sub_category_image = models.ImageField(upload_to='media', null=True, blank=True)


class ServiceProvider(models.Model):
    """Service provider Model"""
    full_name = models.CharField(default='', max_length=256)
    email = models.EmailField(default='', max_length=256, unique=True)
    password = models.CharField(default='', max_length=100)
    confirm_password = models.CharField(default='', max_length=100)
    profile_pic = models.ImageField(upload_to='media', null=True, blank=True)
    country_code = models.IntegerField()
    phone_number = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    address = models.CharField(default='', max_length=556)
    created_at = models.DateTimeField(auto_now_add=True)
