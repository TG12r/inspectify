from django.db import models
from django.contrib.auth import get_user_model



class ServicioFreelance(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.CharField(max_length=50, help_text='Precio, rango o a convenir')
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='servicios_freelance')
    contacto = models.CharField(max_length=200, help_text='Email, teléfono o medio de contacto')
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
