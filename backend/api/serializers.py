from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('estado', 'codigo_qr', 'fecha_compra')
        extra_kwargs = {
            'numero_asiento': {'required': False},
            'comprobante_pago': {'required': True, 'allow_null': False},
        }

    def create(self, validated_data):
        # Asegurarse de que el estado inicial sea 'PENDIENTE'
        validated_data['estado'] = 'PENDIENTE'
        return super().create(validated_data)