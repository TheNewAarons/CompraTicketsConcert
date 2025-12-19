from django.db import models

class Ticket(models.Model):
    TIPO_ENTRADA_CHOICES = [
        ('GENERAL', 'General'),
        ('GOLDEN_NUM', 'Golden Numerada'),
        ('VIP', 'VIP'),
        ('VIP_NUM', 'VIP Numerada'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    dni = models.CharField(max_length=20)
    tipo_entrada = models.CharField(max_length=20, choices=TIPO_ENTRADA_CHOICES)
    numero_asiento = models.IntegerField(null=True, blank=True)
    comprobante_pago = models.ImageField(upload_to='comprobantes/')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    codigo_qr = models.ImageField(upload_to='qr/', blank=True, null=True)

    class Meta:
        unique_together = [['tipo_entrada', 'numero_asiento']]