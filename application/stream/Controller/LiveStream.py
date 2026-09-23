import xml.etree.ElementTree as ET
from database.models import Streaming
from django.http import Http404
from django.views.generic import DetailView
from core.Utils.StreamsUtils.StreamingPluggin import StreamingPluggin
import requests


class LiveStream(DetailView):
	model = Streaming
	template_name = "stream/streaming.html"
	context_object_name = "stream"

	def get_object(self, queryset=None):
		stream_id = self.request.GET.get("zx")
		if not stream_id:
			raise Http404("Stream tidak ditemukan atau token tidak valid.")
		try:
			return Streaming.objects.get(kode=stream_id)
		except Streaming.DoesNotExist:
			raise Http404("Stream tidak ditemukan atau token tidak valid.")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		streamingInit = StreamingPluggin(self.object.keystream.stream)
		rtmp_status = streamingInit.check_rtmp_stat()
		context["is_online"] = rtmp_status["is_online"]
		context["viewers"] = rtmp_status["viewers"]
		return context

	def check_rtmp_stat(self, stream_key):
		stat_url = "http://localhost:8080/stat"
		app_name = "stream"
		default_result = {"is_online": False, "viewers": 0}

		try:
			response = requests.get(stat_url, timeout=3)
			if response.status_code != 200:
				return default_result

			root = ET.fromstring(response.content)

			for app in root.findall(".//application"):
				name_elem = app.find("name")
				if name_elem is not None and name_elem.text == app_name:
					for stream in app.findall(".//stream"):
						s_name = stream.find("name")
						if s_name is not None and s_name.text == stream_key:
							nclients_elem = stream.find("nclients")
							nclients = int(nclients_elem.text) if nclients_elem is not None else 0

							publisher = stream.find("publisher")
							is_publishing = publisher is not None
							viewers = (nclients - 1) if is_publishing and nclients > 0 else 0

							return {"is_online": True, "viewers": max(0, viewers)}

		except (requests.exceptions.RequestException, ET.ParseError):
			return default_result

		return default_result