from django import forms
from .models import DoctorNote

class DoctorNoteForm(forms.ModelForm):
    class Meta:
        model = DoctorNote
        fields = ['content']  # Remove 'patient' and 'doctor' from the form fields

        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'content': 'Details of the Note',
        }

    def __init__(self, *args, **kwargs):
        super(DoctorNoteForm, self).__init__(*args, **kwargs)
        # You don't need to let the user select 'doctor' or 'patient'
        # These fields are set automatically when the note is saved
        self.fields['content'].widget.attrs.update({'placeholder': 'Enter the details of the note'})
