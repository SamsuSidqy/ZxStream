from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify
from datetime import datetime,timedelta
from django.utils.crypto import get_random_string
import secrets
import string

from database.Utils.Authentication.Users import UserManager

class Authentikasi(AbstractUser):
	id 		 = models.AutoField(primary_key=True)
	username = models.CharField(max_length=255,unique=True)
	email 	 = models.CharField(max_length=255,unique=True)

	REQUIRED_FIELDS = ['email']

	objects = UserManager()

	def save(self,*args,**kwargs):
		# Tambahkan Logic Jika Perluu...		
		super(Authentikasi,self).save(*args,**kwargs)

class ProfileUser(models.Model):
	user = models.OneToOneField(
		Authentikasi, 
		on_delete=models.CASCADE, 
		related_name='profile'
	)
	photo 		= models.TextField(null=True, blank=True)
	birthday	= models.DateTimeField(null=True)
	created_at 	= models.DateTimeField(auto_now_add=True)
	updated_at 	= models.DateTimeField(auto_now=True)
	def __str__(self):
		return f"{self.user.username}'s Profile"

class StreamKey(models.Model):
	id 	 = models.AutoField(primary_key=True)
	user = models.OneToOneField(
		Authentikasi, 
		on_delete=models.CASCADE, 
		related_name='user_stream',
		null=True,
		blank=True,		
	)
	stream 		= models.TextField(unique=True)
	expired_in	= models.DateTimeField(null=True)
	created_at 	= models.DateTimeField(auto_now_add=True)	
	updated_at 	= models.DateTimeField(auto_now=True)

	def generate_stream_key(self):
		chars = string.ascii_letters + string.digits

		while True:
			code = ''.join(secrets.choice(chars) for _ in range(32))
			stream = f'zx_live_{code}'

			if not StreamKey.objects.filter(stream=stream).exists():
				return stream

	def save(self, *args, **kwargs):
		self.stream = self.generate_stream_key()

		if not self.expired_in:
			from datetime import timedelta
			from django.utils import timezone

			self.expired_in = timezone.now() + timedelta(hours=1)

		super().save(*args, **kwargs)

class KategoriStreaming(models.Model):
	id 			= models.AutoField(primary_key=True)
	title 		= models.CharField(max_length=255,unique=True)
	slug		= models.SlugField(unique=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super(Blogging, self).save(*args, **kwargs)

class Streaming(models.Model):
	id 			= models.AutoField(primary_key=True)
	title 		= models.CharField(max_length=255)
	deskripsi	= models.TextField()
	keystream = models.ForeignKey(
		StreamKey, 
		on_delete=models.CASCADE, 
		related_name="keystream",
		unique=True,
	)
	kategori = models.ForeignKey(
		KategoriStreaming, 
		on_delete=models.CASCADE, 
		related_name="kategori",
		null=True,
		blank=True
	)
	user = models.OneToOneField(
		Authentikasi, 
		on_delete=models.CASCADE, 
		related_name='streaming_user',
		null=True,
		blank=True,
		unique=True,
	)
	thumbnail	= models.TextField()
	kode		= models.TextField(unique=True)
	created_at 	= models.DateTimeField(auto_now_add=True)
	updated_at 	= models.DateTimeField(auto_now=True)

	def save(self,*args,**kwargs):
		self.kode = get_random_string(7)
		super(Streaming,self).save(*args,**kwargs)

