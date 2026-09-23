from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from studio.Utils.Forms.StreamKeyForm import StreamKeyForm, StreamKeyFormGenerate
from studio.Utils.Forms.StreamingForm import StreamForm

from core.Utils.StreamsUtils.StreamingPluggin import StreamingPluggin
from database.models import StreamKey, KategoriStreaming, Streaming

import requests
import xml.etree.ElementTree as ET

class StudioPage(LoginRequiredMixin,TemplateView):
	template_name = 'studio/apps.html'
	login_url = '/'
	redirect_field_name =''

	def get_context_data(self,**kwargs):
		context = super().get_context_data(**kwargs)
		keystream = StreamKey.objects.filter(user=self.request.user.id).first()
		streamInit = StreamingPluggin(keystream.stream).check_rtmp_stat()
		context['stream_form'] = StreamKeyForm(
			request=self.request
		)
		context['streaming_form'] = StreamForm(
			request=self.request
		)
		
		context['stream_key'] = keystream
		context['status'] = streamInit
		context['streams'] = Streaming.objects.filter(user=self.request.user.id).first()
		context['kategori'] = KategoriStreaming.objects.all()		
		return context

	def post(self, request, *args, **kwargs):
		type = request.POST.get('type')
		if type == '2':
			form = StreamKeyForm(
				request.POST,
				request=request
			)
			if form.is_valid():
				stream_key = form.save()
				redirect('/studio/')
				# setelah berhasil
				# redirect atau proses lainnya

			context = self.get_context_data(**kwargs)
			context['stream_form'] = form

			return self.render_to_response(context)
		elif type == '3':
			# Generate Ulang
			form = StreamKeyFormGenerate(
				request.POST,
				request=request
			)
			if form.is_valid():
				stream_key = form.save()
				redirect('/studio/')
				# setelah berhasil
				# redirect atau proses lainnya
			print(form)
			context = self.get_context_data(**kwargs)
			context['stream_form'] = form

			return self.render_to_response(context)
		else:
			form = StreamForm(request.POST,request.FILES, request=request)
			if form.is_valid():
				stream_key = form.save()
				redirect('/studio/')
				# setelah berhasil
				# redirect atau proses lainnya

			context = self.get_context_data(**kwargs)
			context['stream_form'] = form
			return self.render_to_response(context)
