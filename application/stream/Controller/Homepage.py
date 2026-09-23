import xml.etree.ElementTree as ET

from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.Utils.StreamsUtils.StreamingPluggin import StreamingPluggin
from database.models import Streaming, KategoriStreaming


class HomePage(TemplateView):
	template_name = 'stream/apps.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get the existing context
		context = super().get_context_data(**kwargs)
		context['kategori'] = KategoriStreaming.objects.all()

		# Get query parameters from self.request.GET
		kategori = self.request.GET.get('zx_kategori', '')
		
		if kategori:
			streams = Streaming.objects.filter(kategori__slug=kategori).values_list('keystream__stream', flat=True)
		else:
			streams = Streaming.objects.values_list('keystream__stream', flat=True)

		streaming_init = StreamingPluggin()
		key_stream_online = streaming_init.check_rtmp_stat_multiple(list(streams))

		context['streamOnline'] = Streaming.objects.filter(keystream__stream__in=key_stream_online)
		
		print(key_stream_online) # Tetap bisa diprint untuk debugging
		
		return context


class LoginPage(LoginView):
	template_name = 'stream/login.html'
	

	# 2. Mencegah user yang sudah login mengakses halaman login
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('/studio/')
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		return '/studio/'

class LogouPage(LogoutView):

	def get_success_url(self):
		return '/'