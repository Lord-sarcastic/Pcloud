from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
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
                return HttpResponseRedirect('/secure-digit/')
            else:
                return HttpResponse("<h1>This user is not yet authenticated, contact the admin for more information or create a new account</h1>")
        else:
            return render(request, self.template_name, {'warning' : f"Form not valid!{form['username'].data.lower()}: {form['email'].data} : {form['password'].data}: {form['first_name'].data} : {form['last_name'].data}: {form['confirm_password'].data}", 'form' : self.form_class})
    
    
class SignInView(View):
    template_name = 'main/signin.html'
    
    def get_queryset(self):
        return User.objects.all()
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
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
                    return render(request, self.template_name, {'warning' : 'Wrong password!'})
            except User.DoesNotExist:
                return render(request, self.template_name, {'warning' : 'User does not exist.'})
        else:
            return render(request, self.template_name, {'warning' : f"Form not valid!"})
            
class AccountIndexView(generic.DetailView):
    template_name = 'main/account.html'

    def get_queryset(self):
        return CustomUser.objects.all().filter(user__is_active__eq=True)


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

class CreateDriveView(LoginRequiredMixin, generic.FormView):
    template_name = 'main/create.html'
    form_class = DriveCreateForm

    def form_valid(self, form):
        drive = form.save(commit=False)
        drive.owner = self.request.user
        drive.created_at = timezone.now()
        drive.save()
        return JsonResponse({code : 0}, safe=False)
    

class CreateFolderView(LoginRequiredMixin, generic.FormView):
    template_name = 'main/create.html'
    form_class = FolderCreateForm

    def post(self, request, drive_id, folder_id, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        folder = form.save(commit=False)
        folder.owner = self.request.user
        folder.created_at = timezone.now()
        folder.drive = Drive.objects.get(id=drive_id)
        if folder_id != 0:
            folder.parent = Folder.objects.get(id=folder_id)
        folder.save()
        return JsonResponse({code : 0}, safe=False)

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
    template_name = 'main/folder-index.html'

    def get_queryset(self):
        return Folder.objects.all()

    def get(self, request, id, slug, *args, **kwargs):
        folder = Folder.objects.get(id=id, slug=slug)
        if folder.owner == request.user:
            return render(request, self.template_name, {'folder' : folder})
        else:
            return HttpResponse('<h1>Permission denied</h1>')

class FileView(LoginRequiredMixin, generic.DetailView):
    template_name = 'main/file-index.html'

    def get_queryset(self):
        return File.objects.all()

    def get(self, request, id, slug, *args, **kwargs):
        file = File.objects.get(id=id, slug=slug)
        if file.owner == request.user:
            return render(request, self.template_name, {'file' : file})
        else:
            return HttpResponse('<h1>Permission denied</h1>')

class DriveView(LoginRequiredMixin, generic.DetailView):
    template_name = 'main/drive-index.html'

    def get_queryset(self):
        return Drive.objects.all()

    def get(self, request, id, slug, *args, **kwargs):
        drive = Drive.objects.get(id=id, slug=slug)
        if drive.owner == request.user:
            return render(request, self.template_name, {'drive' : drive})
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
        if item.owner == request.user:
            item.delete()
            return 0
        else:
            return PermissionError
    else:
        return 1