# CompraTiketsConcert - Sistema de Venta de Entradas

Este proyecto es una aplicación web completa para la gestión y venta de entradas para conciertos, desarrollada con un backend en **Django** y un frontend en **React**.

## 📋 Descripción

El sistema permite a los usuarios comprar entradas para eventos (específicamente configurado para "Evan Craft Arica") y proporciona un panel de administración para gestionar las ventas y visualizar los tickets generados.

### Funcionalidades Principales

**Para el Usuario (Público):**
- **Página de Inicio:** Visualización atractiva con video de fondo.
- **Compra de Entradas:** Formulario para registrar la compra de tickets (`/comprar`).

**Para el Administrador:**
- **Login Seguro:** Autenticación mediante JWT (JSON Web Tokens).
- **Dashboard de Tickets:** Visualización y gestión de los tickets vendidos (`/admin/tickets`).

## 🛠 Tecnologías Utilizadas

### Backend
- **Python 3**
- **Django 5.1.4**: Framework web principal.
- **Django REST Framework**: Para la creación de la API REST.
- **JWT (Simple JWT)**: Para autenticación segura.
- **SQLite**: Base de datos por defecto (fácil de configurar para desarrollo).
- **CORS Headers**: Para permitir la comunicación con el frontend.

### Frontend
- **React 19**: Biblioteca de UI.
- **React Router Dom**: Manejo de rutas.
- **Bootstrap 5 & React-Bootstrap**: Estilizado y componentes UI.
- **Axios**: Cliente HTTP para conectar con el backend.

## 🚀 Requisitos Previos

Asegúrate de tener instalado en tu sistema:
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 14+ y npm](https://nodejs.org/)

## ⚙️ Instalación y Configuración

Sigue estos pasos para poner el proyecto en marcha localmente.

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd CompraTiketsConcert
```

### 2. Configurar el Backend (Django)

Navega a la carpeta principal del backend:

```bash
cd backend
```

Se recomienda crear un entorno virtual para aislar las dependencias:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

Instalar las dependencias (si no tienes un archivo requirements.txt, instala las principales manualmente):

```bash
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
```

Realizar las migraciones de la base de datos:

```bash
python manage.py migrate
```

Crear un superusuario para acceder al admin de Django:

```bash
python manage.py createsuperuser
```

Iniciar el servidor de desarrollo:

```bash
python manage.py runserver
```

El backend correrá en `http://localhost:8000`.

### 3. Configurar el Frontend (React)

Abre una nueva terminal y navega a la carpeta del frontend:

```bash
cd frontend
```

Instalar las dependencias de Node:

```bash
npm install
```

Iniciar la aplicación de React:

```bash
npm start
```

El frontend correrá en `http://localhost:3000`.

## 📖 Uso del Proyecto

1. **Backend Admin:**
   - Accede a `http://localhost:8000/admin` para gestionar usuarios y base de datos directamente con el panel de Django.

2. **Aplicación Web:**
   - Abre `http://localhost:3000` en tu navegador.
   - Verás la página de inicio.
   - Haz clic en **"Comprar Entradas"** para probar el flujo de usuario.
   - Haz clic en **"Admin"** para ingresar al panel de control (`/admin/login`). Usa las credenciales que creaste con `createsuperuser` (nota: asegúrate de que el frontend esté enviando las credenciales al endpoint correcto de login).

## 📂 Estructura del Proyecto

```text
CompraTiketsConcert/
├── backend/          # Código fuente del Backend (Django)
│   ├── api/          # Lógica de la API (Vistas, Serializers)
│   ├── backend/      # Configuraciones del proyecto (settings.py, urls.py)
│   └── manage.py     # Script de gestión de Django
└── frontend/         # Código fuente del Frontend (React)
    ├── public/       # Archivos estáticos públicos
    └── src/          # Componentes React (App.js, components/)
```

---
Creado por el equipo de desarrollo de CompraTiketsConcert.
