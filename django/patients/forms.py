from django import forms
from .models import Patient
from .models import NurseNote

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'national_id',
            'dob',
            'gender',
            'country',
            'medical_condition',
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(),
            'medical_condition': forms.Textarea(attrs={'rows': 2}),
        }

class ConfirmAdmissionForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['admitted', 'rfid_tag']

class NurseNoteForm(forms.ModelForm):
    class Meta:
        model = NurseNote
        fields = ['note_type', 'content']
        widgets = {
            'note_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'note_type': 'Type of Note',
            'content': 'Details',
        }



