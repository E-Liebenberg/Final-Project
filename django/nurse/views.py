
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from nurse.forms import AssignRemoteForm
from patients.models import Patient
from django.contrib import messages
from nurse.forms import BillStockForm 
from patients.models import Patient, NurseNote
from patients.forms import NurseNoteForm

@login_required
def nurse_dashboard(request):
    patients = Patient.objects.filter(admitted=True)
    return render(request, 'nurse/dashboard.html', {'patients': patients})

@login_required
def assign_remote_to_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, admitted=True)

    if request.method == 'POST':
        form = AssignRemoteForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('nurse:nurse_dashboard')
    else:
        form = AssignRemoteForm(instance=patient)

    return render(request, 'nurse/assign_remote.html', {
        'form': form,
        'patient': patient
    })

@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'patients/patient_detail.html', {'patient': patient})

@login_required
def edit_remote(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, admitted=True)

    if request.method == 'POST':
        form = AssignRemoteForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('nurse:nurse_dashboard')
    else:
        form = AssignRemoteForm(instance=patient)

    return render(request, 'nurse/edit_remote.html', {
        'form': form,
        'patient': patient
    })

@login_required
def remove_remote(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, admitted=True)

    if patient.remote:
        patient.remote = None
        patient.save()
        messages.success(request, f"Remote unassigned from {patient.first_name} {patient.last_name}.")
    else:
        messages.warning(request, "This patient has no remote assigned.")

    return redirect('nurse:nurse_dashboard')


@login_required
def bill_stock_to_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, admitted=True)

    if request.method == 'POST':
        form = BillStockForm(request.POST)
        if form.is_valid():
            stock_note = form.cleaned_data['note']
            patient.stock_used += f"\n{stock_note}"
            patient.stock_billed += f"\n{stock_note}"
            patient.save()
            messages.success(request, "Stock billed successfully.")
            return redirect('nurse:nurse_dashboard')
    else:
        form = BillStockForm()

    return render(request, 'nurse/bill_stock.html', {'form': form, 'patient': patient})

@login_required
def add_nurse_note(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = NurseNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.patient = patient
            note.nurse = request.user
            note.save()
            messages.success(request, "Nurse note added successfully.")
            return redirect('nurse:patient_detail', patient_id=patient.id)
    else:
        form = NurseNoteForm()

    return render(request, 'nurse/add_nurse_note.html', {
        'form': form,
        'patient': patient
    })