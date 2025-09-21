# from django.shortcuts import render
# from alerts.models import Alert
# from remotes.models import Remote
# from patients.models import Patient
# from django.http import JsonResponse, Http404
# from django.views.decorators.csrf import csrf_exempt
# # Create your views here.
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Alert

# def alert_dashboard(request):
#     alerts = Alert.objects.filter(acknowledged=False).order_by('-timestamp')

#     code_blue_alerts = alerts.filter(alert_type="code_blue")[:5]
#     nurse_call_alerts = alerts.filter(alert_type="nurse_call")[:5]
#     other_alerts = alerts.exclude(alert_type__in=["code_blue", "nurse_call"])[:5]

#     return render(request, 'alerts/dashboard.html', {
#         'code_blue_alerts': code_blue_alerts,
#         'nurse_call_alerts': nurse_call_alerts,
#         'other_alerts': other_alerts,
#     })

# def acknowledge_alert(request, alert_id):
#     alert = get_object_or_404(Alert, id=alert_id)
#     alert.acknowledged = True
#     alert.save()
#     return redirect('alerts:dashboard')

# def full_dashboard(request):
#     alert_type = request.GET.get("type")  # e.g., "code_blue", "nurse_call", "other"

#     if alert_type == "other":
#         alerts = Alert.objects.exclude(alert_type__in=["code_blue", "nurse_call"]).filter(acknowledged=False).order_by('-timestamp')
#     elif alert_type in ["code_blue", "nurse_call", "sound", "movement"]:
#         alerts = Alert.objects.filter(alert_type=alert_type, acknowledged=False).order_by('-timestamp')
#     else:
#         alerts = Alert.objects.none()  # prevent errors on bad input

#     return render(request, 'alerts/full_dashboard.html', {
#         'alerts': alerts,
#         'alert_type': alert_type,
#     })

# @csrf_exempt
# def create_alert(request):
#     data = json.loads(request.body)
#     remote_id = data.get("remote_id")
#     alert_type = data.get("alert_type", "nurse_call")

#     remote = Remote.objects.filter(remote_id=remote_id).first()
#     patient = Patient.objects.filter(ward=remote.ward, bed=remote.bed, admitted=True).first()

#     Alert.objects.create(
#         patient=patient,
#         remote=remote,
#         alert_type=alert_type,
#         acknowledged=False
#     )

#     return JsonResponse({'status': 'alert_created'})
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Alert
from remotes.models import Remote
from patients.models import Patient

def alert_dashboard(request):
    # Get all unacknowledged alerts, ordered by timestamp
    alerts = Alert.objects.filter(acknowledged=False).order_by('-timestamp')

    # Filter and limit alerts by type (first 5 of each)
    code_blue_alerts = alerts.filter(alert_type="code_blue")[:5]
    nurse_call_alerts = alerts.filter(alert_type="nurse_call")[:5]
    other_alerts = alerts.exclude(alert_type__in=["code_blue", "nurse_call"])[:5]

    return render(request, 'alerts/dashboard.html', {
        'code_blue_alerts': code_blue_alerts,
        'nurse_call_alerts': nurse_call_alerts,
        'other_alerts': other_alerts,
    })

def acknowledge_alert(request, alert_id):
    # Retrieve the alert by id, if not found raise 404 error
    alert = get_object_or_404(Alert, id=alert_id)
    
    # Mark the alert as acknowledged
    alert.acknowledged = True
    alert.save()

    # Redirect to the alert dashboard after acknowledging
    return redirect('alerts:dashboard')

def full_dashboard(request):
    # Get alert type from the query parameter
    alert_type = request.GET.get("type")

    # Filter alerts based on alert type and whether they're acknowledged or not
    if alert_type == "other":
        alerts = Alert.objects.exclude(alert_type__in=["code_blue", "nurse_call"]).filter(acknowledged=False).order_by('-timestamp')
    elif alert_type in ["code_blue", "nurse_call", "sound", "movement"]:
        alerts = Alert.objects.filter(alert_type=alert_type, acknowledged=False).order_by('-timestamp')
    else:
        alerts = Alert.objects.none()  # If invalid alert type, return empty queryset

    return render(request, 'alerts/full_dashboard.html', {
        'alerts': alerts,
        'alert_type': alert_type,
    })

@csrf_exempt
def create_alert(request):
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)
        remote_id = data.get("remote_id")
        alert_type = data.get("alert_type", "nurse_call")  # Default to "nurse_call" if not specified

        # Get the remote and corresponding patient
        remote = Remote.objects.filter(remote_id=remote_id).first()
        if not remote:
            return JsonResponse({'status': 'error', 'message': 'Remote not found'}, status=400)

        patient = Patient.objects.filter(ward=remote.ward, bed=remote.bed, admitted=True).first()
        if not patient:
            return JsonResponse({'status': 'error', 'message': 'Patient not found'}, status=400)

        # Create the new alert in the database
        Alert.objects.create(
            patient=patient,
            remote=remote,
            alert_type=alert_type,
            acknowledged=False
        )

        return JsonResponse({'status': 'alert_created'})
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing key: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
