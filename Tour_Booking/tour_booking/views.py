import uuid
import pandas as pd
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.views import generic
from .models import Tour, Booking, FavoriteTour, Rating, Reply
from .forms import TourSearchForm, BookingForm, CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
#from django.utils.encoding import force_text
from django.contrib import messages
from django.utils.translation import gettext
from django.utils import timezone
from django.urls import reverse,reverse_lazy
from .mail import send_mail_custom
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from datetime import datetime
# Create your views here.
def index(request):
    context = {"title": gettext("Home Page")}
    return render(request, "index.html", context=context)

# TourListView 

class TourListView(generic.ListView):
    model = Tour

# Login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  
        else:
            return render(request, 'login.html', {'error_message': _('Đăng nhập không thành công. Vui lòng thử lại.')})
    else:
        return render(request, 'login.html')

#Log Out

def logout_view(request):
    logout(request)
    return redirect('index')

# Tour Detail & Book Tour
from django.views import View

class BookTourView(View):
    template_name = 'tour_booking/book_tour.html'

    def get(self, request, *args, **kwargs):
        tour = Tour.objects.get(pk=self.kwargs['tour_id'])
        form = BookingForm()
        context = {'tour': tour, 'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        tour = Tour.objects.get(pk=self.kwargs['tour_id'])
        form = BookingForm(request.POST)
        if form.is_valid():
            current_date = timezone.now().date()
            departure_date = form.cleaned_data['departure_date'].date()
            if departure_date > current_date:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.tour = tour
                booking.status = 'Pending'
                booking.price = tour.price * int(form.cleaned_data['number_of_people'])
                booking.save()
                return redirect(reverse('tour-detail', args=[str(tour.pk)]))
            else:
                error_message = _('Bạn chỉ được đặt tour cho tương lai.')
                context = {'tour': tour, 'form': form, 'error_message': error_message}
                return render(request, self.template_name, context)
        else:
            context = {'tour': tour, 'form': form}
            return render(request, self.template_name, context)

#List Booking

@login_required
def list_bookings(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')

        if booking_id:
            booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

            if booking.status == 'Pending':
                # Lưu trạng thái hủy đơn và gửi email thông báo
                booking.status = 'Cancelled'
                booking.save()

                # Gửi email thông báo hủy đơn thành công
                context = {'user': booking.user, 'tour': booking.tour}
                message = render_to_string('email/email_notification_cancelled.html', context)
                subject = 'Hủy đơn đặt tour'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [booking.user.email]
                send_mail(subject, message, from_email, recipient_list, html_message=message)


    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'tour_booking/list_bookings.html', {'bookings': bookings})

#Search List

def search_view(request):
    form = TourSearchForm(request.GET)
    tour_list = Tour.objects.all()
    tour_list = tour_list.order_by('-average_rating', 'created_at')

    # Xử lý tìm kiếm theo từ khóa
    query = request.GET.get('query')
    if query:
        tour_list = tour_list.filter(name__icontains=query)

    # Xử lý lọc theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        tour_list = tour_list.filter(price__range=(min_price, max_price))
    # Xử lý lọc theo ngày
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        tour_list = tour_list.filter(start_date__gte=start_date)
    if end_date:
        tour_list = tour_list.filter(end_date__lte=end_date)

    # Sử dụng prefetch_related để tải hình ảnh liên quan cho tất cả các tour trong queryset
    tour_list = tour_list.prefetch_related('image_set')

    context = {
        'tour_list': tour_list,
        'form': form,
    }
    return render(request, 'tour_booking/tour_list.html', context)

# Sign Up

def sign_up(request):
    context = {}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            token = uuid.uuid4()
            user = get_user_model().objects.create_user(username, email, password)
            user.is_active = True
            user.save()
            HOST = "http://localhost:8000"
            link =  HOST + reverse_lazy("login")
            send_mail_custom(
                gettext("You have successfully registered an account at Tour Booking"),
                email,
                None,
                "email/activation_email.html",
                link=link,
                username = username,
            )
            return redirect("send-mail-success")
            
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})


def activate_account(request, uidb64):
    try:
        uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    print("uidb64:", uidb64)
    print("uid:", uid)
    print("user:", user)

    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, _("Your account has been activated. You can now log in."))
        return redirect("login")
    else:
        messages.error(request, _("Invalid activation link."))
        return render(request, "email/send_mail_success.html")

# Send Mail

def send_mail_success(request):
    context={}
    return render(request, "email/send_mail_success.html", context=context)

#Comment
from .forms import RatingForm, ReplyForm

from django.contrib.auth.decorators import login_required

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)

    if request.method == 'POST':
        rating_form = RatingForm(request.POST)
        reply_form = ReplyForm(request.POST)

        if rating_form.is_valid():
            return submit_rating(request, tour_id)

    else:
        rating_form = RatingForm()
        reply_form = ReplyForm()

    context = {
        'tour': tour,
        'rating_comment_form': rating_form,
        'reply_form': reply_form, 
    }
    return render(request, 'tour_booking/tour_detail.html', context)


from django.http import HttpResponseRedirect

def submit_rating(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    booking = tour.booking_set.filter(user=request.user, status='Confirmed').first()

    if not booking:
        return HttpResponse("Bạn chưa được xác nhận đặt tour, không thể bình luận.")
        
    if request.method == 'POST':
        rating_form = RatingForm(request.POST)

        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.user = request.user
            rating.tour = tour
            rating.save()

    return redirect('tour-detail', tour_id=tour_id)

@login_required
def submit_reply_comment(request, pk):
    parent_comment_id = request.POST.get('parent_comment_id')
    parent_comment = get_object_or_404(Rating, pk=parent_comment_id)

    if parent_comment.tour.booking_set.filter(user=request.user, status='Confirmed').exists():
        if request.method == 'POST':
            replies_comment_form = ReplyForm(request.POST)
            
            if replies_comment_form.is_valid():
                reply_content = replies_comment_form.cleaned_data.get('content')
                reply = Reply(user=request.user, content=reply_content, parent_comment=parent_comment)
                reply.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse("Bạn chưa được xác nhận đặt tour, không thể bình luận.")




# Admin Approve

def approve_tours(request):
    if request.method == 'POST':
        selected_bookings = request.POST.getlist('selected_bookings')
        action = request.POST.get('action')

        if action == 'approve':
            bookings_to_approve = Booking.objects.filter(pk__in=selected_bookings, status='Pending')
            for booking in bookings_to_approve:
                booking.is_approved = True
                booking.status = 'Confirmed'
                booking.save()

                # Gửi email thông báo phê duyệt
                context = {'user': booking.user, 'tour': booking.tour}
                message = render_to_string('email/email_notification_approved.html', context)
                subject = 'Xác nhận đơn đặt tour'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [booking.user.email]
                send_mail(subject, message, from_email, recipient_list, html_message=message)

        elif action == 'cancel':
            bookings_to_cancel = Booking.objects.filter(pk__in=selected_bookings, status='Pending')
            for booking in bookings_to_cancel:
                booking.is_cancelled = True
                booking.status = 'Cancelled'
                booking.save()

                # Gửi email thông báo hủy
                context = {'user': booking.user, 'tour': booking.tour}
                message = render_to_string('email/email_notification_cancelled.html', context)
                subject = 'Hủy đơn đặt tour'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [booking.user.email]
                send_mail(subject, message, from_email, recipient_list, html_message=message)

        elif action == 'delete':
            bookings_to_delete = Booking.objects.filter(pk__in=selected_bookings)
            confirmed_or_pending_bookings = bookings_to_delete.filter(status__in=['Pending', 'Confirmed'])
            if confirmed_or_pending_bookings.exists():
                messages.error(request, "Không thể xóa các đơn đặt đang chờ xử lý hoặc được xác nhận.")
            else:
                bookings_to_delete.filter(status='Cancelled').delete()

    bookings = Booking.objects.all()
    return render(request, 'admin/approve_tours.html', {'bookings': bookings})


#Like

@login_required
def toggle_favorite_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    favorite, created = FavoriteTour.objects.get_or_create(user=request.user, tour=tour)

    if not created:
        favorite.delete()

    return redirect('tour-detail', tour_id=tour_id) 



def favorite_tours_list(request):
    user = request.user
    favorite_tours = FavoriteTour.objects.filter(user=user)
    
    context = {
        'favorite_tours': favorite_tours,
    }
    
    return render(request, 'tour_booking/favorite_tours_list.html', context)



def parse_date(date_str):
    match = re.search(r'(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)', date_str)
    if match:
        day = match.group(1)
        month = match.group(2)
        year = match.group(3)
        formatted_date = f'{day}/{month}/{year}'
        return datetime.strptime(formatted_date, '%d/%m/%Y')
    return None

@staff_member_required
def upload_tour_data(request):
    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        if excel_file.name.endswith('.xlsx'):
            df = pd.read_excel(excel_file)

            success_count = 0
            failed_count = 0
            failed_details = []

            for index, row in df.iterrows():
                try:
                    tour = Tour(
                        name=row['Title'],
                        location=row['Location'],
                        price=row['Price'],
                        average_rating=row['Rating'],
                        start_date=row['Start Date'],
                        end_date=row['End Date'],
                        description=row['Description'],
                    )
                    tour.save()
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_details.append(f"Row {index+2}: {str(e)}")

            messages.success(request, f'Successfully imported {success_count} tours.')
            if failed_count > 0:
                failed_message = f'Failed to import {failed_count} tours. Errors:\n'
                failed_message += '\n'.join(failed_details)
                messages.error(request, failed_message)

            return redirect('admin:tour_booking_tour_changelist')
        else:
            messages.error(request, 'Please upload a valid Excel file.')

    return render(request, 'admin/upload_tour_data.html')
