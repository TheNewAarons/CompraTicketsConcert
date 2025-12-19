import React, { useState, useEffect, useCallback } from 'react';
import { Container, Table, Button, Badge, Alert, Modal, Image } from 'react-bootstrap';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const AdminTickets = () => {
  const [tickets, setTickets] = useState([]);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const navigate = useNavigate();

  const fetchTickets = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/admin/login');
        return;
      }

      const response = await axios.get('http://localhost:8000/api/tickets/', {
        headers: { 
          'Authorization': `Bearer ${token}`,
        }
      });
      setTickets(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        navigate('/admin/login');
      } else {
        setError('Error al cargar los tickets');
      }
    }
  }, [navigate]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  const handleVerificar = async (ticketId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://localhost:8000/api/tickets/${ticketId}/verificar_pago/`,
        {},
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
          }
        }
      );
      await fetchTickets();
      setShowModal(false);
    } catch (error) {
      setError('Error al verificar el ticket');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/admin/login');
  };

  const handleShowComprobante = (ticket) => {
    setSelectedTicket(ticket);
    setShowModal(true);
  };

  const getEstadoBadge = (estado) => {
    const variants = {
      'PENDIENTE': 'warning',
      'VERIFICADO': 'success',
      'RECHAZADO': 'danger'
    };
    return <Badge bg={variants[estado]}>{estado}</Badge>;
  };

  return (
    <>
      <Container className="py-5">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Administración de Tickets</h2>
          <Button variant="outline-danger" onClick={handleLogout}>
            Cerrar Sesión
          </Button>
        </div>

        {error && (
          <Alert variant="danger" className="mb-4" onClose={() => setError(null)} dismissible>
            {error}
          </Alert>
        )}

        <Table responsive striped bordered hover>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Tipo</th>
              <th>Asiento</th>
              <th>Estado</th>
              <th>Fecha</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map(ticket => (
              <tr key={ticket.id}>
                <td>{ticket.id}</td>
                <td>{ticket.nombre}</td>
                <td>{ticket.email}</td>
                <td>{ticket.tipo_entrada}</td>
                <td>{ticket.numero_asiento || '-'}</td>
                <td>{getEstadoBadge(ticket.estado)}</td>
                <td>{new Date(ticket.fecha_compra).toLocaleString()}</td>
                <td>
                  <div className="d-flex gap-2">
                    <Button
                      variant="info"
                      size="sm"
                      onClick={() => handleShowComprobante(ticket)}
                    >
                      Ver Comprobante
                    </Button>
                    {ticket.estado === 'PENDIENTE' && (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleVerificar(ticket.id)}
                      >
                        Verificar
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Container>

      <Modal 
        show={showModal} 
        onHide={() => setShowModal(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>
            Comprobante de Pago - Ticket #{selectedTicket?.id}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedTicket && (
            <div>
              <div className="mb-3">
                <strong>Nombre:</strong> {selectedTicket.nombre}<br />
                <strong>Email:</strong> {selectedTicket.email}<br />
                <strong>Tipo de Entrada:</strong> {selectedTicket.tipo_entrada}<br />
                <strong>Estado:</strong> {selectedTicket.estado}
              </div>
              
              <div className="text-center">
                <Image 
                  src={selectedTicket.comprobante_pago} 
                  alt="Comprobante de pago"
                  fluid
                  style={{ maxHeight: '60vh' }}
                />
              </div>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cerrar
          </Button>
          {selectedTicket?.estado === 'PENDIENTE' && (
            <Button 
              variant="success"
              onClick={() => handleVerificar(selectedTicket.id)}
            >
              Verificar Pago
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default AdminTickets;
