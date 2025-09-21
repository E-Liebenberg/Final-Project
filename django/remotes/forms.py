from django import forms
from .models import Remote
from patients.models import Patient

class RemoteForm(forms.ModelForm):
    assigned_patient = forms.ModelChoiceField(
        queryset=Patient.objects.filter(admitted=True),
        required=False,
        label="Assign to Patient"
    )

    class Meta:
        model = Remote
        fields = ['remote_id', 'mac_address', 'ip_address', 'ward', 'bed']

    def __init__(self, *args, **kwargs):
        # Optional: assign initial patient if editing
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.setdefault('initial', {})
            from patients.models import Patient
            patient = Patient.objects.filter(remote=instance).first()
            if patient:
                initial['assigned_patient'] = patient

        super().__init__(*args, **kwargs)
