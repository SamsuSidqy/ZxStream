import os

from django import forms
from django.conf import settings

from database.models import Streaming, StreamKey


class StreamForm(forms.ModelForm):
	filegambar = forms.ImageField(
		required=False,
		label="Thumbnail",
	)

	class Meta:
		model = Streaming
		fields = [
			"title",
			"deskripsi",
			"keystream",
			"kategori",
			"user",
			"kode",
			"filegambar",
		]
	def __init__(self, *args, request=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.request = request
		self.fields["keystream"].required = False
		self.fields["kode"].required = False

	def save(self, commit=True):
	    user = self.request.user

	    old_instance = Streaming.objects.filter(user=user).first()
	    streamkey = StreamKey.objects.filter(user=user).first()

	    if old_instance:
	        # UPDATE object lama
	        instance = old_instance

	        instance.title = self.cleaned_data.get("title")
	        instance.deskripsi = self.cleaned_data.get("deskripsi")
	        instance.kategori = self.cleaned_data.get("kategori")

	    else:
	        # CREATE object baru
	        instance = super().save(commit=False)

	        instance.user = user
	        instance.keystream = streamkey
	        instance.kode = "SALD1293"

	    # Pastikan field otomatis/relasi tetap ada
	    instance.keystream = streamkey
	    instance.kode = "SALD1293"
	    instance.user = user

	    filegambar = self.cleaned_data.get("filegambar")

	    if filegambar:
	        upload_dir = os.path.join(
	            settings.MEDIA_ROOT,
	            "thumbnail",
	        )

	        os.makedirs(upload_dir, exist_ok=True)

	        filename = filegambar.name
	        file_path = os.path.join(upload_dir, filename)

	        with open(file_path, "wb+") as destination:
	            for chunk in filegambar.chunks():
	                destination.write(chunk)

	        instance.thumbnail = filename

	    if commit:
	        instance.save()

	    return instance


