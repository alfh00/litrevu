"""
URL configuration for litrevu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView

import authentication.views
import feed.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', authentication.views.LoginPageView.as_view(), name='login'),
    path('logout/', authentication.views.logout_user, name='logout'),
    path('signup/', authentication.views.SignupPageView.as_view(), name='signup'),
    path('home/', feed.views.feed, name='home'),
    path('ticket/new/', feed.views.create_new_ticket, name = 'new_ticket'),
    path('ticket_review/new/', feed.views.create_new_ticket_review, name = 'new_ticket_review'),
    path('ticket/all/', feed.views.get_all_tickets, name='all_tickets'),
    path('ticket/<int:ticket_id>/', feed.views.get_single_ticket, name='ticket_detail'),
    path('ticket/<int:ticket_id>/edit/', feed.views.edit_ticket, name='edit_ticket'),
    path('ticket/<int:ticket_id>/delete/', feed.views.delete_ticket, name='delete_ticket'),
    path('discover/', feed.views.discover, name='discover'),
    path('following_followers_lists/', feed.views.following_followers_lists, name='following_followers_lists'),
    path('follow/<int:user_id>/', feed.views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', feed.views.unfollow_user, name='unfollow_user'),
    path('tickets/<int:ticket_id>/add_review/', feed.views.add_review, name='add_review'),
    path('tickets/<int:ticket_id>/edit_or_delete_review/', feed.views.edit_or_delete_review, name='edit_or_delete_review'),
    path('tickets/<int:review_id>/delete_review/', feed.views.delete_review, name='delete_review'),
    # path('urlrate/', feed.views.reviews_data),
]

if settings.DEBUG:
 urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)