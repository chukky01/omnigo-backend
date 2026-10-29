from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - ({self.latitude}, {self.longitude})"

class Order(models.Model):
    # EVERYTHING BELOW MUST BE INDENTED 4 SPACES
    customer_name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sales_rep = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.customer_name} - ₦{self.amount}"
    
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.user.email} checked in at {self.check_in_time.strftime('%H:%M')}"
    
class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin Manager'),
        ('rep', 'Field Rep'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='rep')

    def __str__(self):
        return f"{self.user.email} - {self.role}"

# Automatically create a Profile for every new User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    
class SupportArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
        
