from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from accounts.utils import is_admin_clerk_or_superuser
from .forms import PatientEditForm, RFIDAssignForm
from admin_clerk.forms import AdminAdmitForm
from patients.models import Patient
from .forms import PatientEditForm
from django.db.models import Q

@user_passes_test(is_admin_clerk_or_superuser)
def dashboard(request):
    query = request.GET.get("q", "")

    all_patients = Patient.objects.all().order_by('-admitted', 'last_name')

    if query:
        all_patients = all_patients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(ward__icontains=query) |
            Q(bed__icontains=query)
        )

    pending_patients = all_patients.filter(admitted=False)
    admitted_patients = all_patients.filter(admitted=True)

    return render(request, 'admin_clerk/dashboard.html', {
        'query': query,
        'pending_patients': pending_patients,
        'admitted_patients': admitted_patients,
    })


@user_passes_test(is_admin_clerk_or_superuser)
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = PatientEditForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('admin_clerk:dashboard')
    else:
        form = PatientEditForm(instance=patient)

    return render(request, 'admin_clerk/edit_patient.html', {
        'form': form,
        'patient': patient
    })

@user_passes_test(is_admin_clerk_or_superuser)
def assign_rfid(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    form = RFIDAssignForm(request.POST or None, instance=patient)

    if request.method == 'POST' and form.is_valid():
        form.save()  # Just save the RFID
        return redirect('admin_clerk:dashboard')

    return render(request, 'patients/assign_rfid.html', {
        'form': form,
        'patient': patient
    })

@user_passes_test(is_admin_clerk_or_superuser)
def admit_new_patient(request):
    if request.method == 'POST':
        form = AdminAdmitForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.admitted = True
            patient.save()
            return redirect('admin_clerk:dashboard')  # or home
    else:
        form = AdminAdmitForm()

    return render(request, 'admin_clerk/admit_new_patient.html', {
        'form': form
    })