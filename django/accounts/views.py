from pyexpat.errors import messages
from django.shortcuts import render

# Create your views here.
# accounts/views.py

from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CreateUserForm, UpdateUserForm, ProfileForm
from .models import Profile

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def user_admin_panel(request):
    users = User.objects.all().order_by('-is_active', 'username')
    return render(request, 'accounts/user_admin_panel.html', {'users': users})

@user_passes_test(is_superuser)
def create_user(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user, role=user_form.cleaned_data['role'])
            return redirect('accounts:user_admin_panel')
    else:
        user_form = CreateUserForm()
    return render(request, 'accounts/create_user.html', {'form': user_form})

@user_passes_test(is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:user_admin_panel')
    else:
        user_form = UpdateUserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_user.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'target_user': user,
    })

@user_passes_test(is_superuser)
def assign_role(request, user_id, role):
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)
    profile.role = role
    profile.save()
    messages.success(request, f"The role '{role}' has been assigned to {user.username}.")
    return redirect('accounts:user_admin_panel')  # Redirect to the admin panel