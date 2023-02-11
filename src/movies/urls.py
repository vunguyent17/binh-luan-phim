from django.urls import path
from django.contrib.auth import views as auth_views
from .views import moviesViews, movielistViews, reviewViews, userViews

app_name = 'movies'
urlpatterns = [
    path('', moviesViews.IndexView.as_view(), name='index'),
    path('movie/<int:pk>/', moviesViews.DetailView.as_view(), name='detail'),
    path('browse/', moviesViews.browse_view, name='browse'),

    path('movie/<int:pk>/review/', reviewViews.send_review, name='send_review'),
    path('review/<int:pk>/edit/', reviewViews.ReviewUpdateView.as_view(), name='update_review'),
    path('review/<int:pk>/delete/', reviewViews.delete_review, name='delete_review'),

    path('movielist/new/', movielistViews.MovielistCreateView.as_view(), name='create_movielist'),
    path('movielist/<int:pk>/edit/', movielistViews.MovielistUpdateView.as_view(), name='edit_movielist'),
    path('movielist/<int:pk>/', movielistViews.MovielistDetailView.as_view(), name='detail_movielist'),

    path('user/<str:user_username>/', userViews.profile_view, name='profile'),
    path("accounts/signup/", userViews.signup_request, name="signup"),
    path("accounts/login/", userViews.login_request, name="login"),
    path("accounts/logout/", userViews.logout_request, name="logout"),
    path("accounts/password-change/", userViews.password_change, name="password_change"),
    path('accounts/password-reset/', userViews.password_reset_request, name='password_reset'),
    path('accounts/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         userViews.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
