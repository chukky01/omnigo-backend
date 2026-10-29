from django.contrib import admin
from .models import Location, Order, Profile, NewsletterSubscriber, SupportArticle

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'timestamp')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'amount', 'status', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    
@admin.register(SupportArticle)
class SupportArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')