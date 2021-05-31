from django.contrib import admin
from .models import UserSearch, Booking, ContactUs, TermsAndCondition, AboutUs, PrivacyPolicy, GeneralInquiry, \
    RatingReview, OffersAndDiscount,Inquiry,Gst

# Register your models here.

admin.site.register(UserSearch)
admin.site.register(Booking)
admin.site.register(ContactUs)
admin.site.register(TermsAndCondition)
admin.site.register(AboutUs)
admin.site.register(PrivacyPolicy)
admin.site.register(GeneralInquiry)
admin.site.register(RatingReview)
admin.site.register(OffersAndDiscount)
admin.site.register(Inquiry)
admin.site.register(Gst)
