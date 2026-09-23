from api.Controller.Security.ValidateStream import ValidateStreamView
from api.Controller.Streams.SecureStream import SecureHLSProxyView
from django.urls import path

app_name = "api"

urlpatterns = [
	path('validate-stream/', ValidateStreamView.as_view()),
	path(
		'api/v1/streams-app/<str:kode>/',
		SecureHLSProxyView.as_view(),
		name="hls-stream",
	),
	path(
		'api/v1/streams-app/<str:kode>/<path:filename>',
		SecureHLSProxyView.as_view(),
		name="hls-segment",
	),
]