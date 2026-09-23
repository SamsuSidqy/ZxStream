from studio.Control.Studio import StudioPage
from django.urls import path

app_name = "studio"

urlpatterns = [
	path('/',StudioPage.as_view()),
]