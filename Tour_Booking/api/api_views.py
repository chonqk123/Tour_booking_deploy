from .serializers import UserSerializer, TourSerializer, ChangeUserInfoSerializer, RatingSerializer, BookingRatioStatisticsSerializer
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from tour_booking.models import Tour, FavoriteTour, Booking, Rating, Reply
from tour_booking.forms import RatingForm, ReplyForm
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
import calendar
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum
from datetime import datetime

@api_view(["POST"])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    try:
        user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        return Response({"message": _("Account does not exist")}, status=status.HTTP_401_UNAUTHORIZED)

    if user.check_password(password):
        serializer = UserSerializer(user)
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({"user": serializer.data, "access_token": access_token, "message": _("Login successful"), "status": status.HTTP_200_OK})
    else:
        return Response({"message": _("Incorrect username or password")}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    favorite, created = FavoriteTour.objects.get_or_create(user=request.user, tour=tour)

    if not created:
        favorite.delete()

    return Response({"message": "Tour đã được thêm vào danh sách yêu thích." if created else "Tour đã được xóa khỏi danh sách yêu thích."})

class FavoriteToursListView(generics.GenericAPIView):
    serializer_class = TourSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = self.request.user
        favorite_tours = FavoriteTour.objects.filter(user=user).order_by('-created_at')
        favorite_tours_list = [fav_tour.tour for fav_tour in favorite_tours]

        if not favorite_tours_list:
            message = "Không có tour yêu thích nào."
        else:
            message = "Danh sách các tour yêu thích."

        return Response({"message": message, "favorite_tours": TourSerializer(favorite_tours_list, many=True).data})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_rating_api(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    booking = tour.booking_set.filter(user=request.user, status='Confirmed').first()

    if not booking:
        return Response({"message": "Bạn chưa được xác nhận đặt tour, không thể bình luận."}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'POST':
        rating_form = RatingForm(request.data)

        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.user = request.user
            rating.tour = tour
            rating.save()

            serializer = RatingSerializer(rating)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_reply_comment_api(request, pk):
    parent_comment_id = request.data.get('parent_comment_id')
    parent_comment = get_object_or_404(Rating, pk=parent_comment_id)

    if parent_comment.tour.booking_set.filter(user=request.user, status='Confirmed').exists():
        if request.method == 'POST':
            replies_comment_form = ReplyForm(request.data)
            
            if replies_comment_form.is_valid():
                reply_content = replies_comment_form.cleaned_data.get('content')
                reply = Reply(user=request.user, content=reply_content, parent_comment=parent_comment)
                reply.save()

                return Response({"message": "Reply comment submitted successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Bạn chưa được xác nhận đặt tour, không thể bình luận."}, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = ChangeUserInfoSerializer(data=request.data, context={'user': user})
        
        if serializer.is_valid():
            new_username = serializer.validated_data.get('username', user.username)
            if new_username != user.username and User.objects.filter(username=new_username).exists():
                return Response({'message': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)
            
            old_password = serializer.validated_data['old_password']
            if not user.check_password(old_password):
                return Response({'message': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
            
            new_password1 = serializer.validated_data['new_password1']
            new_password2 = serializer.validated_data['new_password2']
            if new_password1 != new_password2:
                return Response({'message': 'New passwords must match.'}, status=status.HTTP_400_BAD_REQUEST)
            
            new_first_name = serializer.validated_data.get('first_name', user.first_name)
            new_last_name = serializer.validated_data.get('last_name', user.last_name)
            new_email = serializer.validated_data.get('email', user.email)
            
            user.username = new_username
            user.first_name = new_first_name
            user.last_name = new_last_name
            user.email = new_email
            user.set_password(new_password1)
            user.save()
            updated_user_serializer = UserSerializer(user)
            return Response(updated_user_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Rating

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_rating_api(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    booking = tour.booking_set.filter(user=request.user, status='Confirmed').first()

    if not booking:
        return Response({"message": "Bạn chưa được xác nhận đặt tour, không thể bình luận."}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'POST':
        rating_form = RatingForm(request.data)

        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.user = request.user
            rating.tour = tour
            rating.save()

            serializer = RatingSerializer(rating)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
#Reply

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_reply_comment_api(request, pk):
    parent_comment_id = request.data.get('parent_comment_id')
    parent_comment = get_object_or_404(Rating, pk=parent_comment_id)

    if parent_comment.tour.booking_set.filter(user=request.user, status='Confirmed').exists():
        if request.method == 'POST':
            replies_comment_form = ReplyForm(request.data)
            
            if replies_comment_form.is_valid():
                reply_content = replies_comment_form.cleaned_data.get('content')
                reply = Reply(user=request.user, content=reply_content, parent_comment=parent_comment)
                reply.save()

                return Response({"message": "Reply comment submitted successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Bạn chưa được xác nhận đặt tour, không thể bình luận."}, status=status.HTTP_400_BAD_REQUEST)

#Thông kê admin

@api_view(['GET'])
@permission_classes([IsAdminUser])
def revenue_statistics(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    tour_id = request.query_params.get('tour_id')

    bookings = Booking.objects.filter(status='Confirmed')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        bookings = bookings.filter(departure_date__gte=start_date)
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        bookings = bookings.filter(departure_date__lte=end_date)
    if tour_id:
        bookings = bookings.filter(tour_id=tour_id)

    total_revenue = bookings.aggregate(total_revenue=Sum('price')).get('total_revenue', 0)

    tour_names = []

    if start_date:
        tours = bookings.filter(departure_date=start_date).values('tour__name').distinct()
        tour_names = [tour['tour__name'] for tour in tours]
    elif tour_id:
        tour = Tour.objects.filter(id=tour_id).first()
        if tour:
            tour_names.append(tour.name)

    return Response({"total_revenue": total_revenue, "tour_names": tour_names})


#Thống kê tỉ lệ đặt tour theo loại

@api_view(['GET'])
@permission_classes([IsAdminUser])
def booking_ratio_statistics(request):
    tour_id = request.query_params.get('tour_id')
    min_average_rating = request.query_params.get('min_average_rating')
    max_average_rating = request.query_params.get('max_average_rating')
    location = request.query_params.get('location')

    bookings = Booking.objects.filter(status='Confirmed')
    if tour_id:
        bookings = bookings.filter(tour_id=tour_id)

    if min_average_rating:
        bookings = bookings.filter(tour__average_rating__gte=float(min_average_rating))

    if max_average_rating:
        bookings = bookings.filter(tour__average_rating__lte=float(max_average_rating))

    if location:
        bookings = bookings.filter(tour__location=location)

    total_booking = bookings.count()
    
    tour_details = Tour.objects.filter(booking__in=bookings).distinct()

    serializer = BookingRatioStatisticsSerializer({
        "total_booking": total_booking,
        "tour_details": tour_details
    })

    return Response(serializer.data)

#Thống kê doanh thu hàng tháng bao gồm thông tin Tour, Tổng tiền, Số lượt đặt tour

@api_view(['GET'])
@permission_classes([IsAdminUser])
def monthly_revenue_statistics(request):
    year = request.query_params.get('year')

    if not year:
        current_year = datetime.now().year
    else:
        try:
            current_year = int(year)
        except ValueError:
            return Response({"error": "Year must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)

    tours = Tour.objects.all()

    result = []
    for tour in tours:
        monthly_revenues = [0] * 12
        bookings = Booking.objects.filter(tour=tour, status='Confirmed', departure_date__year=current_year)

        for booking in bookings:
            month = booking.departure_date.month - 1
            monthly_revenues[month] += booking.price

        total_bookings = bookings.count()

        month_names = [calendar.month_name[i + 1] for i in range(12)]

        result.append({
            "tour_name": tour.name,
            "monthly_revenues": [{"month": month_names[i], "revenue": monthly_revenues[i]} for i in range(12)],
            "total_bookings": total_bookings
        })
    return Response(result)

