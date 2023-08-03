from django.urls import include, path
from . import views
from django.conf.urls.static import static

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
]
