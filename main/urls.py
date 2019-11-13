from django.urls import path
from main import views, forms
from django.contrib.auth.views import LoginView, LogoutView
app_name = 'main'
urlpatterns = [
    path('sign-in', views.SignInView.as_view(), name='sign_in'),
    path('sign-up', views.SignUpView.as_view(), name='sign_up'),
    path('<slug:slug>/', views.AccountIndexView.as_view(), name='account_index'),
    path('<slug:slug>/delete-account', views.DeleteAccountView.as_view(), name='delete_account'),
    path('<slug:slug>/edit-account', views.EditAccountView.as_view(), name='edit_account'),
    path('create-drive', views.CreateDriveView.as_view(), name='create_drive'),
    path('create-folder', views.CreateFolderView.as_view(), name='create_folder'),
    path('create-file', views.CreateFileView.as_view(), name='create_file'),
    path('update-drive/<int:pk>', views.UpdateDriveView.as_view(), name='update_drive'),
    path('update-file/<int:pk>', views.UpdateFileView.as_view(), name='update_file'),
    path('update-folder/<int:pk>', views.UpdateFolderView.as_view(), name='update_folder'),
    path('<slug:owner.customuser.slug>/folders/<int:pk>/update', views.UpdateFolderView.as_view(), name='update_folder'),
    path('<slug:owner.customuser.slug>/drives/<int:pk>/update', views.UpdateDriveView.as_view(), name='update_drive'),
    path('<slug:owner.customuser.slug>/files/<int:pk>/update', views.UpdateFileView.as_view(), name='update_file'),
    path('<slug:owner.customuser.slug>/delete-items/<int:pk>', views.delete_item, name='delete_item'),
]