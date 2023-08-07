from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    #path('tours/', views.TourListView.as_view(), name='tours'),
    path('tour/<int:pk>', views.TourDetailView.as_view(), name='tour-detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_view, name='search'),
    path('bookings/', views.list_bookings, name='list-bookings'),
    path('bookings/<str:token>/', views.list_bookings, name='list-bookings'),
    path("signup/", views.sign_up, name="signup"),
    path("signup/send-mail-success/", views.send_mail_success, name="send-mail-success"),
    path('tour/<int:pk>/rate-comment/', views.tour_rating_comment, name='tour-rating-comment'),
    path('approve-tours/', views.approve_tours, name='approve-tours'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
