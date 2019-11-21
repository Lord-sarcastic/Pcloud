from django.urls import path
from main import views, forms
from django.contrib.auth.views import LoginView, LogoutView
app_name = 'main'
urlpatterns = [
    path('', views.SignInView.as_view(), name='sign_in'),
    path('sign-up', views.SignUpView.as_view(), name='sign_up'),
    path('drive/<int:pk>', views.DriveView.as_view(), name='drive_view'),
    path('folder/<int:pk>', views.FolderView.as_view(), name='folder_view'),
    path('file/<int:pk>', views.FileView.as_view(), name='file_view'),
    path('<slug:slug>/', views.AccountIndexView.as_view(), name='account_index'),
    path('<slug:slug>/delete-account', views.DeleteAccountView.as_view(), name='delete_account'),
    path('<slug:slug>/edit-account', views.EditAccountView.as_view(), name='edit_account'),
    path('<slug:slug>/create-drive', views.create_drive, name='create_drive'),
    path('drive/<int:drive_id>/create-folder/parent-<int:parent_id>', views.CreateFolderView.as_view(), name='create_folder'),
    path('drive/<int:drive_id>/create-file/parent-<int:parent_id>', views.create_file, name='create_file'),
    path('edit-drive/<int:drive_id>', views.edit_drive, name='edit_drive'),
    path('update-file/<int:id>', views.UpdateFileView.as_view(), name='update_file'),
    path('edit-folder/<int:folder_id>', views.edit_folder, name='edit_folder'),
    path('delete-item/<int:id>/<int:code>', views.delete_item, name='delete_item'),
]