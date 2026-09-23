from stream.Controller.Homepage import HomePage, LoginPage, LogouPage
from stream.Controller.LiveStream import LiveStream
from django.urls import path

app_name = "stream"

urlpatterns = [
	path('',HomePage.as_view(),name="homepage"),
	path('auth/login/',LoginPage.as_view(),name="login"),
	path('auth/logout/',LogouPage.as_view(),name="logout"),
	path('watch',LiveStream.as_view()),
]