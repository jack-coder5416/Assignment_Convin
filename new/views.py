from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView
from google.oauth2 import credentials
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import secrets

class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect/',
        
        )
        state = secrets.token_urlsafe(16)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state='16'
        )
        request.session['google_auth_state'] = '16'
        return redirect(auth_url)

class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        if request.GET.get('state') != '16':
            return HttpResponseBadRequest('Invalid state parameter')

        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/'
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        service = build('calendar', 'v3', credentials=credentials)
        events = service.events().list(calendarId='primary').execute()

        return JsonResponse(events)
