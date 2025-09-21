from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Remote
from .forms import RemoteForm  # Assuming you have a form for adding/editing remotes

# Optional: Only allow staff (using is_staff)
@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def manage_remotes(request):
    remotes = Remote.objects.all().order_by('ward', 'bed')
    return render(request, 'remotes/manage_remotes.html', {'remotes': remotes})

# View to add a new remote
@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def add_remote(request):
    if request.method == 'POST':
        form = RemoteForm(request.POST, user=request.user)  # Pass user to form
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'New remote added successfully!')
                return redirect('remotes:manage_remotes')
            except Exception as e:
                messages.error(request, f'Error adding remote: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RemoteForm(user=request.user)  # Pass user here too

    return render(request, 'remotes/add_edit_remote.html', {'form': form})

# View to edit an existing remote
@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def edit_remote(request, remote_id):
    remote = get_object_or_404(Remote, id=remote_id)

    if request.method == 'POST':
        form = RemoteForm(request.POST, instance=remote)
        if form.is_valid():
            remote = form.save()

            # Update patient assignment
            assigned_patient = form.cleaned_data.get('assigned_patient')
            from patients.models import Patient

            # Unassign this remote from all patients
            Patient.objects.filter(remote=remote).update(remote=None)

            if assigned_patient:
                assigned_patient.remote = remote
                assigned_patient.save()

            messages.success(request, 'Remote details updated successfully!')
            return redirect('remotes:manage_remotes')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RemoteForm(instance=remote)

    return render(request, 'remotes/add_edit_remote.html', {'form': form, 'remote': remote})


# View to delete a remote
@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def delete_remote(request, remote_id):
    remote = get_object_or_404(Remote, id=remote_id)

    if request.method == 'POST':
        try:
            remote.delete()
            messages.success(request, 'Remote deleted successfully!')
            return redirect('remotes:manage_remotes')
        except Exception as e:
            messages.error(request, f'Error deleting remote: {str(e)}')

    return render(request, 'remotes/confirm_delete.html', {'remote': remote})
