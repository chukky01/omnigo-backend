from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Max
from datetime import timedelta
import json

# Combine all model imports into one clean line
from .models import Attendance, Location, Order, NewsletterSubscriber, SupportArticle

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        company = request.POST.get('company')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password')

        if not all([full_name, email, company, password]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'An account with this email already exists'}, status=400)

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name
            )
            user.save()
            return JsonResponse({'success': True, 'message': 'User created'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(username=email, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Logged in'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logged out successfully'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_users(request):
    if request.method == 'GET':
        users = User.objects.all().select_related('profile').values(
            'id', 'first_name', 'email', 'date_joined', 'profile__role'
        )
        
        user_list = list(users)
        for u in user_list:
            u['date_joined'] = u['date_joined'].strftime("%b %d, %Y")
            u['role'] = u.get('profile__role') or 'rep'
            
        return JsonResponse({'users': user_list}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=405)


@csrf_exempt
def add_employee(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([full_name, email, password]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'A user with this email already exists'}, status=400)

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name
            )
            user.save()
            return JsonResponse({'success': True, 'message': 'Employee added'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_employee(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        
        if not user_id:
            return JsonResponse({'error': 'No user ID provided'}, status=400)
            
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'success': True, 'message': 'Employee deleted'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def update_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            lat = data.get('latitude')
            lng = data.get('longitude')

            user = User.objects.get(username=email)
            Location.objects.create(user=user, latitude=lat, longitude=lng)
            
            return JsonResponse({'success': True, 'message': 'Location updated'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=405)


def get_locations(request):
    if request.method == 'GET':
        latest_locations = Location.objects.values('user').annotate(latest_id=Max('id'))
        location_ids = [loc['latest_id'] for loc in latest_locations]
        locations = Location.objects.filter(id__in=location_ids).select_related('user')
        
        data = []
        for loc in locations:
            data.append({
                'user': loc.user.first_name or loc.user.email,
                'lat': loc.latitude,
                'lng': loc.longitude,
                'time': loc.timestamp.strftime("%H:%M:%S")
            })
        return JsonResponse({'locations': data}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=405)


def get_orders(request):
    if request.method == 'GET':
        orders = Order.objects.all().order_by('-created_at')
        data = []
        for order in orders:
            data.append({
                'id': order.id,
                'customer_name': order.customer_name,
                'amount': float(order.amount),
                'status': order.status,
                'date': order.created_at.strftime("%b %d, %Y"),
                'rep': order.sales_rep.first_name if order.sales_rep else 'Unknown'
            })
        return JsonResponse({'orders': data}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=405)


@csrf_exempt
def add_order(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        amount = request.POST.get('amount')
        
        if not all([customer_name, amount]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        try:
            Order.objects.create(
                customer_name=customer_name,
                amount=amount,
                status='Pending'
            )
            return JsonResponse({'success': True, 'message': 'Order created'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=405)


@csrf_exempt
def delete_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('id')
        if not order_id:
            return JsonResponse({'error': 'No order ID provided'}, status=400)
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            return JsonResponse({'success': True, 'message': 'Order deleted'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def clock_in(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            lat = data.get('latitude')
            lng = data.get('longitude')

            user = User.objects.get(username=email)
            
            today = timezone.now().date()
            already_checked_in = Attendance.objects.filter(
                user=user, 
                check_in_time__date=today
            ).exists()

            if already_checked_in:
                return JsonResponse({'error': 'You are already clocked in for today.'}, status=400)

            Attendance.objects.create(user=user, latitude=lat, longitude=lng)
            return JsonResponse({'success': True, 'message': 'Clocked in successfully'}, status=201)
        except User.DoesNotExist:
             return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=405)


def get_attendance(request):
    if request.method == 'GET':
        today = timezone.now().date()
        records = Attendance.objects.filter(check_in_time__date=today).order_by('-check_in_time')
        
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'user': record.user.first_name or record.user.email,
                'time': record.check_in_time.strftime("%I:%M %p"),
                'lat': record.latitude,
                'lng': record.longitude
            })
        return JsonResponse({'attendance': data, 'total_today': records.count()}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=405)


@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        user = authenticate(username=email, password=old_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Password updated'}, status=200)
        else:
            return JsonResponse({'error': 'Incorrect current password'}, status=401)
    return JsonResponse({'error': 'Invalid request'}, status=405)


@csrf_exempt
def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        try:
            if NewsletterSubscriber.objects.filter(email=email).exists():
                return JsonResponse({'success': True, 'message': 'You are already subscribed!'}, status=200)
            
            NewsletterSubscriber.objects.create(email=email)
            return JsonResponse({'success': True, 'message': 'Subscribed successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=405)

def get_articles(request):
    if request.method == 'GET':
        articles = SupportArticle.objects.all().order_by('-created_at')
        data = []
        for article in articles:
            data.append({
                'id': article.id,
                'title': article.title,
                'content': article.content, # In production, you'd render Markdown or HTML here
                'date': article.created_at.strftime("%b %d, %Y")
            })
        return JsonResponse({'articles': data}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=405)