import requests
import xml.etree.ElementTree as ET
import os
from django.conf import settings
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.views import View

from database.models import Streaming

class StreamingPluggin:

	PRIVATE_KEY = None
	def __init__(self, streamkey = None):
		self.PRIVATE_KEY = streamkey
		pass

	def check_rtmp_stat(self):
		stat_url = settings.STAT_URL
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
						if s_name is not None and s_name.text == self.PRIVATE_KEY:
							nclients_elem = stream.find("nclients")
							nclients = int(nclients_elem.text) if nclients_elem is not None else 0

							publisher = stream.find("publisher")
							is_publishing = publisher is not None
							viewers = (nclients - 1) if is_publishing and nclients > 0 else 0

							return {"is_online": True, "viewers": max(0, viewers)}

		except (requests.exceptions.RequestException, ET.ParseError):
			return default_result

		return default_result

	def check_rtmp_stat_multiple(self, array_key_stream):
		stat_url = settings.STAT_URL
		print(stat_url)
		app_name = "stream"
		
		online_keys = []
		print("Array input:", array_key_stream)

		try:
			response = requests.get(stat_url, timeout=3)
			if response.status_code != 200:
				return online_keys

			root = ET.fromstring(response.content)

			for app in root.findall(".//application"):
				name_elem = app.find("name")
				if name_elem is not None and name_elem.text == app_name:
					
					for stream in app.findall(".//stream"):
						s_name = stream.find("name")
						if s_name is not None and s_name.text is not None:
							stream_name = s_name.text.strip()
							print(f"Cek Stream XML: '{stream_name}'")
							
							if stream_name in array_key_stream:
								publisher = stream.find("publisher")
								
								# Cek isi elemen publisher untuk debugging
								print(f"-> Ditemukan dalam array! Elemen publisher: {publisher}")								
								online_keys.append(stream_name)
								print(f"-> BERHASIL DITAMBAHKAN: {stream_name}")

			return online_keys

		except (requests.exceptions.RequestException, ET.ParseError) as e:
			print(f"Error: {e}")
			return []

	def proxy(self, target_url, is_manifest):
		try:
			if is_manifest:
				upstream = requests.get(target_url, timeout=3)
				if upstream.status_code != 200:
					raise Http404("Playlist tidak ditemukan di NGINX.")
				return HttpResponse(
						upstream.text,
						content_type="application/vnd.apple.mpegurl",
				)
			else:
				upstream = requests.get(target_url, stream=True, timeout=5)
				if upstream.status_code != 200:
					raise Http404("Segmen tidak ditemukan di NGINX.")
				return StreamingHttpResponse(
						upstream.iter_content(chunk_size=8192),
						content_type="video/mp2t",
				)
		except requests.exceptions.RequestException:
			raise Http404("Gagal terhubung ke media server.")