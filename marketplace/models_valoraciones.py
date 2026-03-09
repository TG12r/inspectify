from django.db import models
from .models_servicios import ServicioFreelance

class ServicioFreelanceValoracion(models.Model):
    servicio = models.ForeignKey(ServicioFreelance, on_delete=models.CASCADE, related_name='valoraciones')
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('servicio', 'usuario')

    def __str__(self):
        return f"{self.usuario.username} - {self.calificacion} estrellas"
