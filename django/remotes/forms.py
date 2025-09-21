from django import forms
from .models import Remote
from patients.models import Patient

class RemoteForm(forms.ModelForm):
    assigned_patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),   # set at runtime
        required=False,
        label="Assign to Patient"
    )

    class Meta:
        model = Remote
        fields = ['remote_id', 'mac_address', 'ip_address', 'ward', 'bed']

    def __init__(self, *args, **kwargs):
        # 🔴 this line is REQUIRED to avoid the TypeError
        self.user = kwargs.pop('user', None)

        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        # build queryset now (you can scope by self.user if needed)
        self.fields['assigned_patient'].queryset = (
            Patient.objects.filter(admitted=True).order_by('last_name', 'first_name')
        )

        # preselect assigned patient when editing
        if instance:
            current = Patient.objects.filter(remote=instance).first()
            if current:
                self.initial['assigned_patient'] = current
