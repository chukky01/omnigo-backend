from accounts.views import register_user, login_user, logout_user, get_users, add_employee, delete_employee, update_location, get_locations, get_orders, add_order, clock_in, get_attendance, delete_order, change_password, subscribe_newsletter, get_articles 
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register_user, name='register'),
    path('api/login/', login_user, name='login'),
    path('api/logout/', logout_user, name='logout'),
    path('api/users/', get_users, name='get_users'),
    path('api/add-employee/', add_employee, name='add_employee'),
    path('api/delete-employee/', delete_employee, name='delete_employee'),
    path('api/update-location/', update_location, name='update_location'),
    path('api/locations/', get_locations, name='get_locations'),
    path('api/orders/', get_orders, name='get_orders'),
    path('api/add-order/', add_order, name='add_order'),
    path('api/clock-in/', clock_in, name='clock_in'),
    path('api/attendance/', get_attendance, name='get_attendance'),
    path('api/delete-order/', delete_order, name='delete_order'),
    path('api/change-password/', change_password, name='change_password'),
    path('api/subscribe/', subscribe_newsletter, name='subscribe'),
    path('api/articles/', get_articles, name='get_articles'),
]