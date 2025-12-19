import React, { useState } from 'react';
import { Form, Button, Container, Alert, Card, Modal } from 'react-bootstrap';
import axios from 'axios';

const PurchaseForm = () => {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
    dni: '',
    tipo_entrada: '',
    comprobante_pago: null
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [ticketData, setTicketData] = useState(null);

  const tiposEntrada = [
    { value: 'GENERAL', label: 'General - 15.000 CLP', precio: 15000 },
    { value: 'GOLDEN_NUM', label: 'Golden Numerada - 20.000 CLP', precio: 20000 },
    { value: 'VIP', label: 'VIP - 25.000 CLP', precio: 25000 },
    { value: 'VIP_NUM', label: 'VIP Numerada - 32.000 CLP', precio: 32000 }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!formData.comprobante_pago) {
      setError('Por favor, seleccione un comprobante de pago');
      setLoading(false);
      return;
    }

    const data = new FormData();
    
    // Agregar campos básicos
    data.append('nombre', formData.nombre);
    data.append('email', formData.email);
    data.append('telefono', formData.telefono);
    data.append('dni', formData.dni);
    data.append('tipo_entrada', formData.tipo_entrada);

    // Agregar el archivo explícitamente
    data.append('comprobante_pago', formData.comprobante_pago);

    // Debug - ver qué se está enviando
    console.log('Enviando datos:');
    for (let pair of data.entries()) {
      console.log(pair[0] + ':', pair[1]);
    }

    try {
      const response = await axios.post('http://localhost:8000/api/tickets/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      console.log('Respuesta:', response.data);
      setTicketData(response.data);
      setShowModal(true);
    } catch (error) {
      console.error('Error completo:', error);
      console.error('Datos del error:', error.response?.data);
      
      let errorMessage = 'Error al procesar la solicitud. Por favor, intente nuevamente.';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (typeof error.response.data === 'object') {
          errorMessage = Object.entries(error.response.data)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n');
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
        console.log('Archivo seleccionado:', file);
        setFormData(prev => ({
            ...prev,
            comprobante_pago: file
        }));
    }
  };

  return (
    <>
      <Container className="py-5">
        <Card className="shadow">
          <Card.Body>
            <h2 className="text-center mb-4">Compra tu Entrada</h2>
            
            {error && (
              <Alert variant="danger" style={{ whiteSpace: 'pre-line' }}>
                {error}
              </Alert>
            )}

            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>Nombre Completo</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Ingrese su nombre completo"
                  value={formData.nombre}
                  onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Email</Form.Label>
                <Form.Control
                  type="email"
                  placeholder="Ingrese su email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Teléfono</Form.Label>
                <Form.Control
                  type="tel"
                  placeholder="Ingrese su teléfono"
                  value={formData.telefono}
                  onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>DNI</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Ingrese su DNI"
                  value={formData.dni}
                  onChange={(e) => setFormData({...formData, dni: e.target.value})}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Tipo de Entrada</Form.Label>
                <Form.Select
                  value={formData.tipo_entrada}
                  onChange={(e) => setFormData({...formData, tipo_entrada: e.target.value})}
                  required
                >
                  <option value="">Seleccione tipo de entrada</option>
                  {tiposEntrada.map(tipo => (
                    <option key={tipo.value} value={tipo.value}>
                      {tipo.label}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-4">
                <Form.Label>Comprobante de Pago</Form.Label>
                <Form.Control
                  type="file"
                  onChange={handleFileChange}
                  accept="image/*"
                  required
                />
                <Form.Text className="text-muted">
                  Por favor, adjunte el comprobante de su transferencia
                </Form.Text>
              </Form.Group>

              <div className="d-grid gap-2">
                <Button 
                  variant="primary" 
                  type="submit" 
                  disabled={loading}
                  size="lg"
                >
                  {loading ? 'Procesando...' : 'Comprar Entrada'}
                </Button>
              </div>
            </Form>
          </Card.Body>
        </Card>
      </Container>

      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg" centered>
        <Modal.Header closeButton>
          <Modal.Title>¡Compra Exitosa!</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {ticketData && (
            <div className="text-center">
              <h4>Se ha enviado una copia a tu correo electrónico: {formData.email}</h4>

              <Alert variant="info">
                <p className="mb-1"><strong>Importante:</strong></p>
                <p className="mb-0">
                  Tu ticket está pendiente de verificación. Una vez que verifiquemos tu pago,
                  recibirás un correo de confirmación.
                </p>
              </Alert>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default PurchaseForm; 