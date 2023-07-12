from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
import reply.views

app_name = "user"

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('signup/', views.signup_view, name="signup"),    
    path('activate/<str:uidb64>/<str:token>/', views.activate, name="activate"),
    
    path('', views.index_view, name="index"),
    path('password_reset/', views.password_reset_request, name="password_reset"),
    
    path('blog/', views.blog_view, name="blog"),    
    path('blog/<int:post_id>/', views.blogdt_view, name='blogdt'),
    
    path('create/', views.create, name="create"),    
    path('upload/', views.upload_view, name="upload"),    
    path('download/<int:post_id>/', views.download_file, name='download_file'),
    
    path('reply/create/<int:post_id>', reply.views.create),    
    path('delete/comment/<int:post_id>/<int:com_id>', views.delete_comment, name="delete_comment"),    
    path('edit/comment/<int:post_id>/<int:com_id>', views.edit_comment, name="edit_comment"),
    path('delete/<int:post_id>', views.delete, name="delete"),
    path('edit/<int:post_id>', views.edit, name="edit"),
    
    path('withdraw/', views.withdraw, name="withdraw"),
    path('mypage/<int:id>/', views.mypage_view, name="mypage"),
    path('mypage/update/<int:id>/', views.mypage_update, name="mypage_update"),
    path('mypage/update/password/<int:id>/', views.new_password, name="new_password"),
    path('mypage/my_post', views.my_post, name="my_post"),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)