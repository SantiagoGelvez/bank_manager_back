from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    # Authentication URLs
    path('signup', views.SignUpView.as_view()),
    path('login', views.LoginView.as_view()),
    path('user', views.UserView.as_view()),
    path('logout', views.LogoutView.as_view()),

    # Account URLs
    path('accounts/types', views.get_account_types),
    path('accounts/register', views.register_bank_account),
    path('accounts', views.get_bank_account_list),
    path('accounts/<uuid:uuid>/deposit', views.deposit_to_account),
    path('accounts/<uuid:uuid>/withdraw', views.withdraw_from_account),
]
