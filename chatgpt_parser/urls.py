from django.contrib import admin
from django.urls import path
from chatgpt_parser import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('generate_texts/', views.GenerateTexts.as_view(), name='generate_texts'),
    path('texts_list/', views.TextsList.as_view(), name='texts_list'),
    path('download_set/<int:set_id>/',
         views.generate_set_for_download, name='download_set'),
    path('<int:pk>/delete/', views.DeleteTextsSet.as_view(), name='delete_texts_set'),
]
