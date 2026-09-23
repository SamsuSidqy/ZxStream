from datetime import timedelta
from django.utils import timezone
from django import forms
from django.db import models
from database.models import StreamKey, Authentikasi


class StreamKeyForm(forms.ModelForm):
    class Meta:
        model = StreamKey
        fields = []

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

        if request:
            user_id = request.user.id

            if user_id:
                try:
                    self.user = Authentikasi.objects.get(id=user_id)
                    print("ada user")
                except Authentikasi.DoesNotExist:
                    print("User tidak ditemukan:", user_id)
                    pass

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.user = self.user
        instance.expired_in = timezone.now() + timedelta(hours=1)

        if commit:
            instance.save()

        return instance

class StreamKeyFormGenerate(forms.ModelForm):
    class Meta:
        model = StreamKey
        fields = []
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_streamkey')
        ]


    def __init__(self,*args,request=None,**kwargs):
        super().__init__(*args,**kwargs)
        pk = StreamKey.objects.get(user=request.user.id)
        self.instance = pk

    def save(self,commit=True):
        instance = self.instance

        instance.created_at = timezone.now()
        if commit:
            instance.save()
        return instance
