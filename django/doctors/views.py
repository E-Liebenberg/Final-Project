from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from patients.models import Patient
from .forms import DoctorNoteForm
from accounts.models import Profile  # Import Profile model

# Check if the user is a doctor or superuser
def is_doctor_or_superuser(user):
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'doctor')

@login_required
def doctors_dashboard(request):
    # Get patients assigned to the logged-in doctor
    patients = Patient.objects.filter(doctor=request.user)

    # Fetch the most recent doctor note for each patient
    doctor_notes = {
        patient.id: patient.doctor_notes.filter(doctor=request.user).order_by('-timestamp').first()
        for patient in patients
    }

    return render(request, 'doctors/dashboard.html', {
        'patients': patients,
        'doctor_notes': doctor_notes
    })


@login_required
@user_passes_test(is_doctor_or_superuser)
def add_doctor_note(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = DoctorNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.doctor = request.user  # Automatically set the logged-in user as the doctor
            note.patient = patient  # Automatically associate the patient from the URL
            note.save()
            messages.success(request, "Doctor note added successfully.")
            return redirect('doctors:doctors_dashboard')  # Redirect to the doctor dashboard
    else:
        form = DoctorNoteForm()

    return render(request, 'doctors/add_doctor_note.html', {'form': form, 'patient': patient})
