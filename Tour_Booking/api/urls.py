from django.urls import path
from . import api_views
from .api_views import ChangeUserInfoAPIView

urlpatterns = [
    path('login/', api_views.login_view, name='api-login'),
    path('toggle-favorite/<int:tour_id>/', api_views.toggle_favorite_tour, name='toggle-favorite-tour'),
    path('favorite-tours/', api_views.FavoriteToursListView.as_view(), name='favorite-tours-list'),
    path('<int:tour_id>/submit-rating/', api_views.submit_rating_api, name='submit-rating-api'),
    path('submit-reply-comment/<int:pk>/', api_views.submit_reply_comment_api, name='submit-reply-comment-api'),
    path('change-user-info/', api_views.ChangeUserInfoAPIView.as_view(), name='api-change-user-info'),
]
