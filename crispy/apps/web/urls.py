"""crispy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.HomeView.as_view(), name="home"),

    # Auth
    path(r'accounts/login/', LoginView.as_view(template_name='auth/login.html'), name="login"),
    path(r'accounts/logout/', LogoutView.as_view(), name="logout"),
    path(r'accounts/register/', views.RegisterView.as_view(), name="register"),

    # Feeds
    path(r'feeds/new/', views.NewFeedView.as_view(), name="new_feed"),
    path(r'feeds/', views.FeedListView.as_view(), name="feed_list"),
    path(r'feeds/my/', views.MyFeedListView.as_view(), name="my_feed_list"),
    path(r'feeds/bookmarked/', views.BookmarkedFeedsView.as_view(), name="bookmarked_feed_list"),
    path(r'feeds/<int:pk>', views.FeedDetailView.as_view(), name="feed_detail"),
    path(r'feeds/<int:pk>/toggle-bookmark/', views.ToggleBookmarkView.as_view(), name="toggle_feed_bookmark"),
    path(r'feeds/<int:pk>/update/', views.FeedUpdateView.as_view(), name="feed_update"),
    path(r'feeds/<int:pk>/entry/', views.EntryDetailView.as_view(), name="entry_detail"),
]
