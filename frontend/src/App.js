import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container, Button } from 'react-bootstrap';
import PurchaseForm from './components/PurchaseForm';
import AdminLogin from './components/AdminLogin';
import AdminTickets from './components/AdminTickets';

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/admin/login" />;
};

function App() {
  return (
    <Router>
      <div className="App">
        {/* Video de fondo */}
        <video autoPlay loop muted className="background-video">
          <source src="/path/to/your/video.mp4" type="video/mp4" />
          Tu navegador no soporta el elemento de video.
        </video>

        <Routes>
          <Route
            path="/"
            element={
              <Container className="py-5 text-center d-flex align-items-center justify-content-center vh-100">
                <div className="text-white">
                  <h1 className="display-4 mb-4">Evan Craft Arica</h1>
                  <Button 
                    href="/comprar" 
                    variant="primary" 
                    size="lg" 
                    className="mx-3"
                  >
                    Comprar Entradas
                  </Button>
                  <Button 
                    href="/admin/login" 
                    variant="outline-light" 
                    size="lg"
                    className="mx-3"
                  >
                    Admin
                  </Button>
                </div>
              </Container>
            }
          />
          <Route path="/comprar" element={<PurchaseForm />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route
            path="/admin/tickets"
            element={
              <PrivateRoute>
                <AdminTickets />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;