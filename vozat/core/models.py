from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField

class Radio(models.Model):
    usuario = models.ManyToManyField(settings.AUTH_USER_MODEL)
    radio = models.CharField('Nombre de la Emisora', max_length=50)
    web = models.URLField()

    class Meta:
        ordering = ['radio']
        verbose_name_plural = 'radios'

    def __str__(self):
        return self.radio

class ProgramasRadiales(models.Model):

    rango = (
            ('0', 'Lunes'),
            ('1', 'Martes'),
            ('2', 'Miercoles'),
            ('3', 'Jueves'),
            ('4', 'Viernes'),
            ('5', 'Sábado'),
            ('6', 'Domingo')
        )

    nombre = models.CharField('Nombre del programa de radio', max_length=60)
    dias = MultiSelectField('Selecciona los días', choices = rango, max_length=40)
    inicio = models.TimeField(blank = False, null = True)
    duracion = models.PositiveSmallIntegerField('Duración del programa(minutos)', default=False)
    radios = models.ForeignKey(Radio, on_delete=models.CASCADE)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'programas radiales'

    def __str__(self):
        return self.nombre