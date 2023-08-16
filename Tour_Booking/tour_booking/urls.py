from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import  BookTourView

urlpatterns = [
    path('', views.index, name='index'),
    #path('tours/', views.TourListView.as_view(), name='tours'),
    #path('tour/<int:pk>', views.TourDetailView.as_view(), name='tour-detail'),
    path('tour/<int:tour_id>/book/', BookTourView.as_view(), name='book-tour'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour-detail'),
    path('tour/<int:pk>/submit-reply/', views.submit_reply_comment, name='submit-reply-comment'),
    path('tour/<int:tour_id>/submit-rating/', views.submit_rating, name='submit-rating'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_view, name='search'),
    path('bookings/', views.list_bookings, name='list-bookings'),
    path('bookings/<str:token>/', views.list_bookings, name='list-bookings'),
    path("signup/", views.sign_up, name="signup"),
    path("signup/send-mail-success/", views.send_mail_success, name="send-mail-success"),
    path('approve-tours/', views.approve_tours, name='approve-tours'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('toggle-favorite/<int:tour_id>/', views.toggle_favorite_tour, name='toggle-favorite-tour'),
    path('favorite-tours/', views.favorite_tours_list, name='favorite-tours-list'),
    path('upload-tour-data/', views.upload_tour_data, name='upload_tour_data'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
]
