from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.db.models import Q, F, Count
from .models import File, Folder, Drive, CustomUser
from .forms import *

class SignUpView(generic.FormView):
    template_name = 'main/register.html'
    form_class = CreateUserForm
    
    def get_queryset(self):
        return User.objects.all()
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form' : self.form_class})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            if form['password'].data != form['confirm_password'].data:
                return render(request, self.template_name, {'warning' : 'Passwords do not match.', 'form' : self.form_class})

            if len(form['password'].data) < 8:
                return render(request, self.template_name, {'warning' : 'Password too short, should not be less than 8 characters.', 'form' : self.form_class})

            try:
                user = User.objects.get(username=form['username'].data.lower())
                return render(request, self.template_name, {'warning' : 'Username already exists.', 'form' : self.form_class})
            except User.DoesNotExist:
                user = User.objects.create_user(form['username'].data.lower(), email=form['email'].data, password=form['password'].data, first_name=form['first_name'].data.capitalize(), last_name=form['last_name'].data.lower())
                customuser = CustomUser(user=user)
                customuser.save()
            user = authenticate(username=user.username, password=form['password'].data)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(f'/{user.customuser.slug}/')
            else:
                return HttpResponse("<h1>This user is not yet authenticated, contact the admin for more information or create a new account</h1>")
        else:
            return render(request, self.template_name, {'warning' : "Form not valid!", 'form' : self.form_class})
    
    
class SignInView(generic.FormView):
    template_name = 'main/signin.html'
    form_class= UserLoginForm
    
    def get_queryset(self):
        return User.objects.all()
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form' : self.form_class})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        # if form.is_valid():
        try:
            user = User.objects.get(username=form['username'].data.lower())
            if user.check_password(form['password'].data):
                user = authenticate(username=user.username, password=form['password'].data)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect('/secure-digit/')
                else:
                    return HttpResponse("<h1>This user is not yet authenticated, contact the admin for more information or create a new account</h1>")
            else:
                return render(request, self.template_name, {'warning' : 'Wrong password!', 'form' : self.form_class})
        except User.DoesNotExist:
            return render(request, self.template_name, {'warning' : 'User does not exist.', 'form' : self.form_class})
        # else:
        #     return render(request, self.template_name, {'warning' : f"Form not valid!", 'form' : self.form_class})
            
class AccountIndexView(generic.DetailView):
    template_name = 'main/index.html'

    def get_queryset(self):
        return CustomUser.objects.all().filter(user__is_active__exact=True)

    def get_context_data(self, **kwargs):
        context = super(AccountIndexView, self).get_context_data(**kwargs)
        context['most_recent_folders'] = Folder.objects.all().filter(owner__exact=self.request.user.customuser).order_by('-created_at')
        context['drives'] = Drive.objects.all()
        context['files'] = File.objects.all()
        return context


class DeleteAccountView(LoginRequiredMixin, generic.DetailView):
    login_url = '/'
    template_name = 'main/delete_account.html'

    def get_queryset(self):
        return CustomUser.objects.all().filter(is_active__eq=True)

    def get(self, request, slug, *args, **kwargs):
        try:
            customuser = CustomUser.objects.get(slug=slug)
        except CustomUser.DoesNotExist:
            return render(request, self.template_name, {'warning' : 'I don\'t know how you managed to do this, but... this can\'t just work'})
        if request.user == customuser.user:
            return render(request, self.template_name, {'customuser' : customuser})
        else:
            raise PermissionError('You are unable to can (*_*)')

    def post(self, request, slug, *args, **kwargs):
        try:
            user = CustomUser.objects.get(slug=slug).user
        except CustomUser.DoesNotExist:
            return render(request, self.template_name, {'warning' : 'I don\'t know how you managed to do this, but... this can\'t just work'})
        if request.user == user:
            user.is_valid = False
            user.save()
            return HttpResponseRedirect('/')
        else:
            raise PermissionError('You are unable to can (*_*)')
        
class EditAccountView(DeleteAccountView):
    template_name = 'main/edit_account.html'

    def get_queryset(self):
        return super().get_queryset()

    def get(self, request, slug, *args, **kwargs):
        try:
            user = CustomUser.objects.get(slug=slug).user
        except CustomUser.DoesNotExist:
            return render(request, self.template_name, {'warning' : 'I don\'t know how you managed to do this, but... this can\'t just work'})
        if request.user == user:
            return render(request, self.template_name, {'user' : user, 'form' : EditUserForm(instance=user)})
        else:
            raise PermissionError('You are unable to can (*_*)')

    def post(self, request, slug, *args, **kwargs):
        try:
            user = CustomUser.objects.get(slug=slug).user
        except User.DoesNotExist:
            return render(request, self.template_name, {'warning' : 'I don\'t know how you managed to do this, but... this can\'t just work'})
        if request.user == user:
            form = EditUserForm(request.POST)
            if form.is_valid():
                try:
                    check_user = User.objects.get(username=form['username'].data.lower())
                    if user != check_user:
                        return render(request, self.template_name, {'warning' : 'Username already exists.'})
                except User.DoesNotExist:
                    user = User.objects.create_user(form['username'].data.lower(), email=form['email'].data, password=form['password'].data, first_name=form['first_name'].data.capitalize(), last_name=form['last_name'].data.lower())
                form.save(commit=False)
                form.save()
                return HttpResponseRedirect(f'/{user.slug}/')
        else:
            raise PermissionError('You are unable to can (*_*)')

#class CreateDriveView(LoginRequiredMixin, generic.FormView):
#    template_name = 'main/create.html'
#    form_class = DriveCreateForm
#
#    def form_valid(self, form):
#        drive = form.save(commit=False)
#        drive.owner = self.request.user
#        drive.created_at = timezone.now()
#        drive.save()
#        return JsonResponse({code : 0}, safe=False)

def create_drive(request, slug):
    if request.method == "POST":
        form = DriveCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = CustomUser.objects.get(slug=slug).user
            if request.user == user:
                drive = form.save(commit=False)
                drive.owner = user.customuser
                drive.created_at = timezone.now()
                drive.save()
                return HttpResponseRedirect(f'/{user.customuser.slug}/')
            else:
                return PermissionDenied
        else:
            return HttpResponse('<h1>Form is not valid</h1>')
    else:
        form = DriveCreateForm
    return render(request, 'main/create-drive.html', {'form' : form})

def edit_drive(request, drive_id):
    drive = Drive.objects.get(id=drive_id)
    if request.method == "POST":
        form = DriveCreateForm(request.POST, request.FILES)
        if form.is_valid():
            if request.user == drive.owner.user:
                drive.name = form['name'].data
                if form['cover_picture'].data:
                    drive.cover_picture = form['cover_picture'].data
                drive.created_at = timezone.now()
                drive.save()
                return HttpResponseRedirect(f'/{request.user.customuser.slug}/')
            else:
                return HttpResponse('<h1>Permission denied</h1>')
        else:
            return HttpResponse('<h1>Form is not valid</h1>')
    else:
        form = DriveCreateForm(instance=drive)
    return render(request, 'main/edit-drive.html', {'form' : form, 'id' : drive.id})

def edit_folder(request, folder_id):
    folder = Folder.objects.get(id=folder_id)
    if request.method == "POST":
        form = FolderCreateForm(request.POST, request.FILES)
        if form.is_valid():
            if request.user == folder.owner.user:
                folder.name = form['name'].data
                if form['cover_picture'].data:
                    folder.cover_picture = form['cover_picture'].data
                folder.created_at = timezone.now()
                folder.save()
                return HttpResponseRedirect(f'/folder/{folder.id}/')
            else:
                return HttpResponse('<h1>Permission denied</h1>')
        else:
            return HttpResponse('<h1>Form is not valid</h1>')
    else:
        form = FolderCreateForm(instance=folder)
    return render(request, 'main/edit-folder.html', {'form' : form, 'folder_id' : folder_id})

def create_file(request, parent_id, drive_id):
    if request.method == "POST":
        form = FileCreateForm(request.POST, request.FILES)
        if form.is_valid():
            if request.user == Folder.objects.get(id=parent_id).owner.user:
                file = form.save(commit=False)
                file.owner = request.user.customuser
                file.folder = Folder.objects.get(id=parent_id)
                if drive_id != 0:
                    file.drive = Drive.objects.get(id=drive_id)
                file.created_at = timezone.now()
                file.save()
                return HttpResponseRedirect(f'/folder/{file.folder.id}')
            else:
                return HttpResponse('<h1>Permission denied</h1>')
        else:
            return HttpResponse('<h1>Form is not valid</h1>')
    else:
        form = FileCreateForm
        return render(request, 'main/create-file.html', {'form' : form, 'drive_id' : drive_id, 'parent_id' : parent_id})

class CreateFolderView(LoginRequiredMixin, generic.FormView):
    template_name = 'main/create-folder.html'
    form_class = FolderCreateForm

    def post(self, request, drive_id, parent_id, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        folder = form.save(commit=False)
        folder.owner = self.request.user.customuser
        folder.created_at = timezone.now()
        folder.drive = Drive.objects.get(id=drive_id)
        if parent_id != 0:
            folder.parent = Folder.objects.get(id=parent_id)
        folder.save()
        return HttpResponseRedirect(f'/drive/{folder.drive.id}')
    
    def get(self, request, drive_id, parent_id, *args, **kwargs):
        return render(request, self.template_name, {'form' : self.form_class, 'drive_id' : drive_id, 'parent_id' : parent_id})

class CreateFileView(LoginRequiredMixin, generic.FormView):
    template_name = 'main/create.html'
    form_class = FileCreateForm

    def post(self, request, drive_id, folder_id, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        folder = form.save(commit=False)
        folder.owner = self.request.user
        folder.created_at = timezone.now()
        if folder_id != 0:
            folder.parent = Folder.objects.get(id=folder_id)
        folder.drive = Drive.objects.get(id=drive_id)
        folder.save()
        return JsonResponse({code : 0}, safe=False)

class UpdateDriveView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'main/update.html'
    form_class = DriveCreateForm

class UpdateFolderView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'main/update.html'
    form_class = FolderCreateForm

class UpdateFileView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'main/update.html'
    form_class = FileCreateForm

class FolderView(LoginRequiredMixin, generic.DetailView):
    template_name = 'main/folder-listings.html'

    def get_queryset(self):
        return Folder.objects.all()

    def get(self, request, pk, *args, **kwargs):
        folder = Folder.objects.get(pk=pk)
        if folder.owner == request.user.customuser:
            return render(request, self.template_name, {'the_folder' : folder})
        else:
            return HttpResponse('<h1>Permission denied</h1>')

class FileView(LoginRequiredMixin, generic.DetailView):
    template_name = 'main/file-index.html'

    def get_queryset(self):
        return File.objects.all()

    def get(self, request, id, *args, **kwargs):
        file = File.objects.get(id=id)
        if file.owner == request.user.customuser:
            return render(request, self.template_name, {'file' : file})
        else:
            return HttpResponse('<h1>Permission denied</h1>')

class DriveView(LoginRequiredMixin, generic.DetailView):
    template_name = 'main/drive-listings.html'

    def get_queryset(self):
        return Drive.objects.all()

    def get(self, request, pk, *args, **kwargs):
        drive = Drive.objects.get(pk=pk)
        if drive.owner == request.user.customuser:
            return render(request, self.template_name, {'the_drive' : drive})
        else:
            return HttpResponse('<h1>Permission denied</h1>')

def delete_item(request, id, code):
    if request.method == 'POST':
        if code == 1:
            item = Drive.objects.get(id=id)
        elif code == 2:
            item = Folder.objects.get(id=id)
        elif code == 3:
            item = File.objects.get(id=id)
        else:
            return 1
        if item.owner == request.user.customuser:
            item_id = {"id" : id, "success" : "1"}
            item.delete()
            return JsonResponse(item_id)
        else:
            item_id = {"id" : id, "success" : "0", "error" : "User has no permission"}
            return JsonResponse(item_id)
    else:
        item_id = {"id" : id, "success" : "0"}
        return JsonResponse(item_id)