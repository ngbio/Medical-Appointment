from django.urls import path, include
from users.views import user_views
from rest_framework.routers import DefaultRouter
from users.views.user_views import login_page, index_page

r = DefaultRouter()
r.register('users', user_views.UserView, basename='user')

urlpatterns = [
    path('', include(r.urls)),
    path('index/', index_page, name='index'),
    path('login/', login_page, name='login'),
    path('logout/', user_views.logout_view, name='logout'),

]
