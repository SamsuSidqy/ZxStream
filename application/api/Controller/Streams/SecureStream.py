import requests
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.views import View
from django.conf import settings
from core.Utils.StreamsUtils.StreamingPluggin import StreamingPluggin
from database.models import Streaming


class SecureHLSProxyView(View):
	NGINX_HLS_URL = settings.HLS_URL

	def get(self, request, kode, filename=None):
		# 1. VALIDASI REFERER (anti hotlink dasar)
		referer = request.META.get("HTTP_REFERER", "")
		host = request.get_host()
		is_local_dev = host.startswith("localhost") or host.startswith("127.0.0.1")

		if referer and host not in referer and not is_local_dev:
			return HttpResponse(
					"Forbidden: Akses luar atau hotlinking terdeteksi", status=403
			)

		# 2. VALIDASI STREAM
		stream = Streaming.objects.filter(kode=kode).first()
		if not stream:
			raise Http404("Stream tidak ditemukan.")

		stream_key = stream.keystream.stream
		streamingInit = StreamingPluggin(stream_key)

		# 3a. REQUEST MANIFEST UTAMA (master .m3u8)
		if filename is None:
			target_url = f"{self.NGINX_HLS_URL}/{stream_key}.m3u8"
			return streamingInit.proxy(target_url, is_manifest=True)

		# 3b. REQUEST NESTED FILE (variant playlist / segmen .ts)
		# Anti path traversal & anti akses stream lain:
		# filename WAJIB diawali stream_key milik kode ini.
		if ".." in filename:
			return HttpResponse("Forbidden: Path tidak valid.", status=403)

		if not filename.startswith(stream_key):
			return HttpResponse("Forbidden: Resource tidak valid.", status=403)

		is_manifest = filename.endswith(".m3u8")
		if not (is_manifest or filename.endswith(".ts")):
			raise Http404("Format file tidak didukung.")

		target_url = f"{self.NGINX_HLS_URL}/{filename}"
		return streamingInit.proxy(target_url, is_manifest=is_manifest)	