from django.db import models
from adminpanel.models import User, Services, ServiceProvider
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime


# Create your models here.
class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(default='', max_length=256)
    referral_code = models.CharField(default='', max_length=20, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    device_token = models.CharField(default='', max_length=3000)
    device_type = models.CharField(default='', max_length=3000)
    lat = models.CharField(default='', max_length=3000)
    lang = models.CharField(default='', max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)


class UserPromoCode(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    code = models.CharField(default='', max_length=200)


class Settings(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    notification = models.BooleanField(default=False)
    language = models.CharField(default='', max_length=200)


class UserSearch(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    searched_value = models.CharField(default='', max_length=256)


class Booking(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(default='', max_length=200)
    requirement = models.CharField(default='', max_length=200)
    address = models.CharField(default='', max_length=2000)
    building = models.CharField(default='', max_length=2000)
    city = models.CharField(default='', max_length=2000)
    landmark = models.CharField(default='', max_length=2000)
    status = models.CharField(default='Started', max_length=256)
    quote = models.CharField(default='', max_length=2560)
    sub_total = models.FloatField(null=True, blank=True)
    fees = models.FloatField(null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    default_address = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ContactUs(models.Model):
    phone_number = models.CharField(default='', max_length=200)
    email = models.CharField(default='', max_length=200)


class PrivacyPolicy(models.Model):
    policy = models.CharField(default='', max_length=3000)
    policy_arabic = models.CharField(default='', max_length=3000)


class TermsAndCondition(models.Model):
    terms = models.CharField(default='', max_length=3000)
    terms_arabic = models.CharField(default='', max_length=3000)


class AboutUs(models.Model):
    content = models.CharField(default='', max_length=3000)
    content_arabic = models.CharField(default='', max_length=3000)


class GeneralInquiry(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Booking, on_delete=models.CASCADE)
    subject = models.CharField(default='', max_length=3000)
    message = models.CharField(default='', max_length=3000)
    image_1 = models.ImageField(upload_to='media', null=True, blank=True)
    image_2 = models.ImageField(upload_to='media', null=True, blank=True)


class RatingReview(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Booking, on_delete=models.CASCADE)
    reviews = models.CharField(default='', max_length=256)
    rating = models.IntegerField()


class OffersAndDiscount(models.Model):
    coupon_code = models.CharField(default='', max_length=256)
    percent = models.CharField(default='', max_length=20)


class UserNotification(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    title = models.CharField(default='', max_length=2000)
    title_arabic = models.CharField(default='', max_length=2000)
    body = models.CharField(default='', max_length=2000)
    body_arabic = models.CharField(default='', max_length=2000)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=AppUser)
def promocode(sender, instance, created, **kwargs):
    if created:
        user_id = instance.id
        x = str(user_id).zfill(2)
        user = AppUser.objects.get(id=user_id)
        first_name = user.full_name
        first_name = first_name.split(' ')
        print(first_name[0])
        today = str(timezone.now().date())
        Date = today.split('-')
        current_year = Date[0]
        promo_code = first_name[0].upper() + x + current_year
        UserPromoCode.objects.create(
            user=user,
            code=promo_code,
        )
        Settings.objects.create(
            user=user,
            notification=True,
            language='English'
        )
        return promo_code
