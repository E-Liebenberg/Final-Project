from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientForm
from django.contrib import messages
from .models import Patient
from .forms import ConfirmAdmissionForm
from django.contrib.auth.decorators import login_required
from remotes.models import Remote
from patients.models import Patient

def admit_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.admitted = False  # Admission pending confirmation
            patient.save()
            messages.success(request, f"Patient {patient.first_name} {patient.last_name} admitted successfully.")
            return render(request, 'patients/admission_success.html', {'patient': patient})
        else:
            messages.error(request, "There was an error with the form. Please review the fields.")
    else:
        form = PatientForm()

    return render(request, 'patients/admit_patient.html', {
        'form': form
    })

def is_admin_clerk_or_superuser(user):
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin_clerk')


@user_passes_test(is_admin_clerk_or_superuser)
def pending_admissions(request):
    patients = Patient.objects.filter(admitted=False)
    return render(request, 'patients/pending_admissions.html', {'patients': patients})

@user_passes_test(is_admin_clerk_or_superuser)
def confirm_admission(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    form = ConfirmAdmissionForm(request.POST or None, instance=patient)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('pending_admissions')

    return render(request, 'patients/confirm_admission.html', {
        'form': form,
        'patient': patient
    })


@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "You are not registered as a patient.")
        return redirect("home")  # You can redirect elsewhere

    # Ensure correct type and format
    ward = str(patient.ward).strip()
    bed = str(patient.bed).strip()

    # Debug print (remove in production)
    print("Patient ward:", repr(ward))
    print("Patient bed:", repr(bed))

    # Find matching remote
    remote = Remote.objects.filter(ward=ward, bed=bed).first()
    print("Matching remote:", remote)

    return render(request, 'patients/dashboard.html', {
        'patient': patient,
        'remote': remote
    })