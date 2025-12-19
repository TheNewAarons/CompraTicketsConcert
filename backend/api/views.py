from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models import Max
from .models import Ticket
from .serializers import TicketSerializer
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
from django.conf import settings
from PIL import Image
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Debug - ver qué datos están llegando
            print("Datos recibidos:", request.data)
            print("Archivos recibidos:", request.FILES)

            # Verificar si hay archivo
            if 'comprobante_pago' not in request.FILES:
                return Response(
                    {'error': 'El comprobante de pago es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Preparar los datos
            data = request.data.dict()
            data['comprobante_pago'] = request.FILES['comprobante_pago']
            
            # Asignar número de asiento solo si es necesario
            tipo_entrada = data.get('tipo_entrada')
            if tipo_entrada in ['GOLDEN_NUM', 'VIP_NUM']:
                ultimo_numero = Ticket.objects.filter(
                    tipo_entrada=tipo_entrada
                ).aggregate(Max('numero_asiento'))['numero_asiento__max'] or 0
                data['numero_asiento'] = ultimo_numero + 1
            else:
                # Si no es un tipo de entrada numerada, asegurarse de que no se asigne un número de asiento
                data['numero_asiento'] = None

            # Validar y guardar
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                print("Errores de validación:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Guardar el ticket
            ticket = serializer.save()

            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr_data = (
                f"TICKET EVAN CRAFT ARICA\n"
                f"----------------------\n"
                f"Nombre: {ticket.nombre}\n"
                f"DNI: {ticket.dni}\n"
                f"Tipo: {ticket.get_tipo_entrada_display()}\n"
                f"{'Asiento: C ' + str(ticket.numero_asiento) if ticket.numero_asiento else ''}\n"
                f"Fecha: {ticket.fecha_compra.strftime('%d/%m/%Y %H:%M')}"
            )
            
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar el código QR
            qr_buffer = BytesIO()
            qr_image.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            filename = f'ticket_qr_{ticket.id}.png'
            ticket.codigo_qr.save(filename, File(qr_buffer), save=True)

            # Crear imagen compuesta
            try:
                # Abrir la imagen de fondo
                background_path = os.path.join(settings.BASE_DIR, 'backend', 'static', 'images', 'evan_craft_bg.jpg')
                background = Image.open(background_path)
                
                # Abrir el QR
                qr_image = Image.open(ticket.codigo_qr.path)
                
                # Ajustar el tamaño del QR para que coincida con el espacio en blanco
                qr_size = (900, 900)  # Tamaño ajustado al espacio blanco
                qr_image = qr_image.resize(qr_size)
                
                # Ajustar la posición para centrar en el espacio blanco
                qr_x = 290  # Posición X ajustada
                qr_y = 190   # Posición Y ajustada
                
                # Crear una copia de la imagen de fondo
                composite = background.copy()
                
                # Pegar el QR en la posición calculada
                composite.paste(qr_image, (qr_x, qr_y))
                
                # Guardar la imagen compuesta
                composite_path = os.path.join(settings.MEDIA_ROOT, f'ticket_completo_{ticket.id}.png')
                composite.save(composite_path)

                # Enviar email con la imagen compuesta
                html_message = f"""
                    <html>
                        <body style="font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
                            <div style="max-width: 800px; margin: 0 auto; background-color: white; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                                <img src="cid:ticket_image" style="width: 100%; height: auto; display: block;">
                                
                                <div style="padding: 40px; text-align: center;">
                                    <h2 style="color: #2c3e50; font-size: 28px; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px; border-bottom: 2px solid #f1c40f; padding-bottom: 10px;">
                                        Detalles de tu Ticket
                                    </h2>
                                    
                                    <div style="background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%); padding: 30px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                                        <div style="display: inline-block; text-align: left; min-width: 280px;">
                                            <p style="margin: 15px 0; font-size: 16px;">
                                                <strong style="color: #2c3e50; display: inline-block; width: 140px;">Nombre:</strong> 
                                                <span style="color: #34495e;">{ticket.nombre}</span>
                                            </p>
                                            <p style="margin: 15px 0; font-size: 16px;">
                                                <strong style="color: #2c3e50; display: inline-block; width: 140px;">Tipo de Entrada:</strong> 
                                                <span style="color: #34495e;">{ticket.get_tipo_entrada_display()}</span>
                                            </p>
                                            <p style="margin: 15px 0; font-size: 16px;">
                                                <strong style="color: #2c3e50; display: inline-block; width: 140px;">Fecha del Evento:</strong> 
                                                <span style="color: #34495e;">25 de Enero</span>
                                            </p>
                                            <p style="margin: 15px 0; font-size: 16px;">
                                                <strong style="color: #2c3e50; display: inline-block; width: 140px;">Fecha de Compra:</strong> 
                                                <span style="color: #34495e;">{ticket.fecha_compra.strftime('%d/%m/%Y %H:%M')}</span>
                                            </p>
                                        </div>
                                    </div>

                                    <div style="margin: 30px 0; padding: 20px; border-radius: 10px; background-color: #fff3cd; border: 1px solid #ffeeba;">
                                        <p style="color: #856404; font-weight: bold; font-size: 18px; margin-bottom: 10px;">
                                            Estado: Pendiente de Verificación
                                        </p>
                                        <p style="color: #856404; font-size: 16px; margin: 0;">
                                            Una vez que verifiquemos tu pago, recibirás un correo de confirmación
                                            con tu entrada definitiva.
                                        </p>
                                    </div>

                                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 14px; color: #666;">
                                        <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                                        <p style="margin: 5px 0;">WhatsApp: +56 9 3867 8468</p>
                                    </div>
                                </div>
                            </div>
                        </body>
                    </html>
                """

                # Crear el mensaje
                text_content = strip_tags(html_message)
                email = EmailMultiAlternatives(
                    subject='Tu Entrada - Evan Craft en Arica',
                    body=text_content,
                    from_email='Evan Craft Arica <evancraftarica@gmail.com>',
                    to=[ticket.email]
                )

                # Adjuntar versión HTML
                email.attach_alternative(html_message, "text/html")
                
                # Adjuntar la imagen compuesta
                with open(composite_path, 'rb') as f:
                    ticket_image = MIMEImage(f.read())
                    ticket_image.add_header('Content-ID', '<ticket_image>')
                    email.attach(ticket_image)

                email.mixed_subtype = 'related'
                email.send(fail_silently=False)
                print("Email enviado exitosamente")

                # Limpiar el archivo temporal
                os.remove(composite_path)

            except Exception as e:
                print(f"Error enviando email: {str(e)}")
                print(f"Error detallado: ", str(e.__class__), str(e))

            return Response({
                'message': 'Ticket creado exitosamente',
                'ticket': self.get_serializer(ticket).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error detallado: {str(e)}")
            return Response({
                'error': f'Error inesperado: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verificar_pago(self, request, pk=None):
        ticket = self.get_object()
        ticket.estado = 'VERIFICADO'
        ticket.save()

        # Enviar email con el ticket final
        try:
            # Crear imagen compuesta
            background_path = os.path.join(settings.BASE_DIR, 'backend', 'static', 'images', 'evan_craft_bg.jpg')
            background = Image.open(background_path)
            
            qr_image = Image.open(ticket.codigo_qr.path)
            
            # Ajustar el tamaño del QR para que coincida con el espacio en blanco
            qr_size = (900, 900)  # Tamaño ajustado al espacio blanco
            qr_image = qr_image.resize(qr_size)
            
            # Ajustar la posición para centrar en el espacio blanco
            qr_x = 290  # Posición X ajustada
            qr_y = 190  # Posición Y ajustada
            
            composite = background.copy()
            composite.paste(qr_image, (qr_x, qr_y))
            
            # Guardar la imagen compuesta
            composite_path = os.path.join(settings.MEDIA_ROOT, f'ticket_final_{ticket.id}.png')
            composite.save(composite_path)

            # Crear el mensaje de correo
            html_message = f"""
                <html>
                    <body style="font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
                        <div style="max-width: 800px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1);">
                            <img src="cid:ticket_image" style="width: 100%; height: auto; display: block;">
                            
                            <div style="padding: 40px; text-align: center;">
                                <h2 style="color: #2c3e50; font-size: 32px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; border-bottom: 2px solid #f1c40f; padding-bottom: 10px;">
                                    Tu Ticket Final
                                </h2>
                                
                                <div style="background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%); padding: 30px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                                    <div style="display: inline-block; text-align: left; min-width: 280px;">
                                        <p style="margin: 15px 0; font-size: 18px;">
                                            <strong style="color: #2c3e50;">Nombre:</strong> 
                                            <span style="color: #34495e;">{ticket.nombre}</span>
                                        </p>
                                        <p style="margin: 15px 0; font-size: 18px;">
                                            <strong style="color: #2c3e50;">Tipo de Entrada:</strong> 
                                            <span style="color: #34495e;">{ticket.get_tipo_entrada_display()}</span>
                                        </p>
                                        {f'<p style="margin: 15px 0; font-size: 18px;"><strong style="color: #2c3e50;">Número de Asiento: C </strong> <span style="color: #34495e;">{ticket.numero_asiento}</span></p>' if ticket.numero_asiento else ''}
                                        <p style="margin: 15px 0; font-size: 18px;">
                                            <strong style="color: #2c3e50;">Fecha del Evento:</strong> 
                                            <span style="color: #34495e;">25 de Enero</span>
                                        </p>
                                        <p style="margin: 15px 0; font-size: 18px;">
                                            <strong style="color: #2c3e50;">Fecha de Compra:</strong> 
                                            <span style="color: #34495e;">{ticket.fecha_compra.strftime('%d/%m/%Y %H:%M')}</span>
                                        </p>
                                    </div>
                                </div>

                                <div style="margin: 30px 0; padding: 20px; border-radius: 10px; background-color: #d4edda; border: 1px solid #c3e6cb;">
                                    <p style="color: #155724; font-weight: bold; font-size: 20px; margin-bottom: 10px;">
                                        Estado: Verificado
                                    </p>
                                    <p style="color: #155724; font-size: 16px; margin: 0;">
                                        Tu pago ha sido verificado. ¡Disfruta del evento!
                                    </p>
                                </div>

                                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 14px; color: #666;">
                                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                                    <p style="margin: 5px 0;">Email: evancraftarica@gmail.com</p>
                                </div>
                            </div>
                        </div>
                    </body>
                </html>
            """

            # Crear el mensaje
            text_content = strip_tags(html_message)
            email = EmailMultiAlternatives(
                subject='Tu Ticket Final - Evan Craft en Arica',
                body=text_content,
                from_email='Evan Craft Arica <evancraftarica@gmail.com>',
                to=[ticket.email]
            )

            # Adjuntar versión HTML
            email.attach_alternative(html_message, "text/html")
            
            # Adjuntar la imagen compuesta
            with open(composite_path, 'rb') as f:
                ticket_image = MIMEImage(f.read())
                ticket_image.add_header('Content-ID', '<ticket_image>')
                email.attach(ticket_image)

            email.mixed_subtype = 'related'
            email.send(fail_silently=False)
            print("Email enviado exitosamente con el ticket final")

            # Limpiar el archivo temporal
            os.remove(composite_path)

        except Exception as e:
            print(f"Error enviando email: {str(e)}")

        return Response({
            'message': 'Pago verificado y ticket enviado exitosamente',
            'estado': ticket.estado
        })

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Debug para ver qué datos llegan
        print(f"Intento de login - Username: {username}")
        
        # Intentar autenticar
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Si la autenticación es exitosa, usar la implementación original
            return super().post(request, *args, **kwargs)
        else:
            # Si falla, dar más detalles sobre el error
            return Response({
                'error': 'Credenciales inválidas',
                'detail': 'El usuario o la contraseña son incorrectos'
            }, status=status.HTTP_401_UNAUTHORIZED)