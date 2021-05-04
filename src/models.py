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
    is_blocked = models.BooleanField(default=False)
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
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    time = models.CharField(default='', max_length=200)
    requirement = models.CharField(default='', max_length=200)
    address = models.CharField(default='', max_length=2000)
    # building = models.CharField(default='', max_length=2000)
    # city = models.CharField(default='', max_length=2000)
    # landmark = models.CharField(default='', max_length=2000)
    status = models.CharField(default='Started', max_length=256)
    quote = models.FloatField(default=0, max_length=2560)
    sub_total = models.FloatField(default=0, null=True, blank=True)
    fees = models.FloatField(default=0, null=True, blank=True)
    discount = models.FloatField(default=0, null=True, blank=True)
    total = models.FloatField(default=0, null=True, blank=True)
    additional_fees = models.FloatField(default=0, null=True, blank=True)
    default_address = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    image_1 = models.ImageField(upload_to='media', null=True, blank=True)
    image_2 = models.ImageField(upload_to='media', null=True, blank=True)
    promocode = models.CharField(default='', max_length=100)
    promocode_applied = models.BooleanField(default=False)
    is_accepted_by_provider = models.BooleanField(default=False)
    is_rejected_by_provider = models.BooleanField(default=False)
    night_booking = models.BooleanField(default=False)
    booking_lat = models.FloatField(default=0)
    booking_long = models.FloatField(default=0)


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


class Inquiry(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    subject = models.CharField(default='', max_length=1000)
    message = models.CharField(default='', max_length=2000)
    image_1 = models.ImageField(upload_to='media', null=True, blank=True)
    image_2 = models.ImageField(upload_to='media', null=True, blank=True)


class RatingReview(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Booking, on_delete=models.CASCADE)
    reviews = models.CharField(default='', max_length=256)
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


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


class ProviderRegistration(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media')
    service_provider_name = models.CharField(default='', max_length=200)
    country_code = models.IntegerField()
    phone_number = models.BigIntegerField()
    email = models.EmailField()
    password = models.CharField(default='', max_length=400)


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
