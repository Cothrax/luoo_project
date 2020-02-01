from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('search_song/', views.search_song, name='search_song'),
    path('page/<int:vol_id>', views.page, name='page'),
    path('file/', views.file)
]
