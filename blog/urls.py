from django.urls import path

from blog import views

app_name = 'blog'


urlpatterns = [
    path("", views.post_list, name='post_list'),
    path("<int:id>/", views.post_detail, name='post_detail'),
    path("post/share/", views.PostShareView.as_view(), name='post_share'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:id>/post/delete/', views.post_delete, name='delete'),
    path('search/', views.post_search, name='post_search'),

]