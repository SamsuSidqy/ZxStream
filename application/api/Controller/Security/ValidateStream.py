from django.http import HttpResponse, HttpResponseForbidden
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from database.models import StreamKey

@method_decorator(csrf_exempt, name='dispatch')
class ValidateStreamView(View):
    def post(self, request, *args, **kwargs):
        # 1. Validasi keamanan: Pastikan request hanya berasal dari localhost / internal Docker
        client_ip = request.META.get('REMOTE_ADDR')
        allowed_ips = ['127.0.0.1', '::1', '172.17.0.1']
        
        if client_ip not in allowed_ips and not client_ip.startswith('172.'):
            return HttpResponseForbidden("Akses ditolak: Bukan dari localhost.")

        # 2. Ambil data stream key yang dikirim oleh Nginx-RTMP
        stream_key = request.POST.get('name')
        
        # 3. Logika validasi stream key (sesuaikan dengan database Anda)
        stream = StreamKey.objects.filter(stream=stream_key).first()
        if stream:
            # Status 200 OK: Nginx mengizinkan streaming dimulai
            return HttpResponse("OK", status=200)
        else:
            # Status 403 Forbidden: Nginx menolak streaming
            return HttpResponseForbidden("Stream key salah!")

    def get(self, request, *args, **kwargs):
        # Mencegah akses via browser (GET request)
        return HttpResponseForbidden("Metode tidak diizinkan.")