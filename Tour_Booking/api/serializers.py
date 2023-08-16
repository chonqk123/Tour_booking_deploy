from rest_framework.serializers import ModelSerializer
from tour_booking.models import Tour, FavoriteTour, Rating, Reply
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "is_active", "is_staff", "date_joined"]

class TourSerializer(ModelSerializer):
    class Meta:
        model = Tour
        fields = '__all__'

class FavoriteTourSerializer(ModelSerializer):
    class Meta:
        model = FavoriteTour
        fields = '__all__'

class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'  # Bạn có thể chỉ định các trường cụ thể ở đây nếu cần

class ReplySerializer(ModelSerializer):
    class Meta:
        model = Reply
        fields = '__all__'  # Bạn có thể chỉ định các trường cụ thể ở đây nếu cần