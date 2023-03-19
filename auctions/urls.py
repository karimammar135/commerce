from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path('accounts/login/', views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("active_listings", views.active_listings, name="active_listings"),
    path("error", views.error, name="error"),
    path("listing_details/<int:id>", views.listing_details, name="listing_details"),
    path("watchlist", views.watchlist, name="watchlist")
]
