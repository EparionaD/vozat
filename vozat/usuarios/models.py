from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    avatar = models.ImageField('Foto de perfil', upload_to = 'avatar')

    class Meta:
        ordering = ('username',)
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.username