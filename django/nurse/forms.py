# nurse/forms.py

from django import forms
from patients.models import Patient
from remotes.models import Remote

class AssignRemoteForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['remote']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show remotes that are not assigned to another patient
        self.fields['remote'].queryset = Remote.objects.filter(patient__isnull=True)


class BillStockForm(forms.Form):
    note = forms.CharField(label="Stock Used", widget=forms.Textarea(attrs={'rows': 3}))