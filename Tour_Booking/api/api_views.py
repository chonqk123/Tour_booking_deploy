from rest_framework import generics, permissions
from rest_framework.response import Response
from tour_booking.models import Tour, FavoriteTour
from .serializers import TourSerializer, UserSerializer
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import  login
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework import status
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken

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


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView

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


### Chưa được
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from tour_booking.models import Tour, Rating, Reply
from tour_booking.forms import RatingForm, ReplyForm
from .serializers import RatingSerializer

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
