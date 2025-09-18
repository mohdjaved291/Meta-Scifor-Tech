# Visual API Designer 🎨

A powerful visual tool for designing and generating complete Django REST Framework APIs. Create your API models visually using an intuitive drag-and-drop interface, define relationships, and generate production-ready Django code instantly.

![Visual API Designer](https://img.shields.io/badge/React-18.0+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Visual Model Designer
- **Drag & Drop Interface**: Create and position models visually on a canvas
- **Real-time Editing**: Edit model names and fields with instant preview
- **Field Types**: Support for various Django field types (CharField, EmailField, IntegerField, DateField, etc.)
- **Auto-arrange**: Automatically organize models in a clean layout

### 🔗 Relationship Management
- **Visual Relationships**: Create foreign key relationships between models with visual connectors
- **Interactive Linking**: Click-to-link models with animated connection lines
- **Relationship Visualization**: See all model relationships at a glance

### 🚀 Code Generation
- **Complete Django Project**: Generates full Django REST Framework project structure
- **Models**: Auto-generated Django models with proper field types and relationships
- **Serializers**: DRF serializers for all models
- **ViewSets**: Complete CRUD ViewSets with REST endpoints
- **URLs**: Configured URL routing for all endpoints
- **Admin Interface**: Pre-configured Django admin
- **Requirements**: Generated requirements.txt with dependencies
- **Documentation**: Comprehensive setup instructions

### 📱 User Experience
- **Responsive Design**: Works on desktop and tablet devices
- **Modern UI**: Clean, professional interface with smooth animations
- **Real-time Preview**: See your API structure as you build it
- **Project Management**: Name and manage your API projects

## 🖥️ Screenshots

### Main Interface
The main interface features a sidebar for model editing and a visual canvas for designing your API structure.

### Model Creation
- Add models with a single click
- Define fields with various types
- Visual field management with type selection

### Relationship Designer
- Click "Link" on any model to start relationship creation
- Visual connection lines show model relationships
- Animated indicators for newly created relationships

## 🚀 Quick Start

### Prerequisites
- Node.js 16.0 or higher
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/visual-api-designer.git
   cd visual-api-designer
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server**
   ```bash
   npm start
   # or
   yarn start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 📖 Usage Guide

### Creating Your First API

1. **Add a Model**
   - Click "Add Model" in the sidebar
   - The model appears on the canvas and is selected for editing

2. **Configure the Model**
   - Change the model name in the sidebar editor
   - Add fields by clicking "Add Field"
   - Select appropriate field types for each field
   - Delete fields using the × button

3. **Create Relationships**
   - Click "Link" on a model to enter linking mode
   - Click another model to create a foreign key relationship
   - Visual connection lines will appear between related models

4. **Generate Django Code**
   - Enter your project name in the header
   - Click "Generate Django Code"
   - Download the complete project file

### Generated Project Structure

```
your_project/
├── manage.py
├── requirements.txt
├── README.md
├── your_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── api/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── apps.py
    └── tests.py
```

### Setting Up Generated Django Project

1. **Extract the generated files** into your project directory

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start server**
   ```bash
   python manage.py runserver
   ```

### API Endpoints

Your generated Django project will have the following endpoints:

- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **API Root**: `http://127.0.0.1:8000/api/`
- **Model Endpoints**: `http://127.0.0.1:8000/api/{model-name}s/`

Each model gets full CRUD endpoints:
- `GET /api/models/` - List all instances
- `POST /api/models/` - Create new instance
- `GET /api/models/{id}/` - Retrieve specific instance
- `PUT /api/models/{id}/` - Update specific instance
- `DELETE /api/models/{id}/` - Delete specific instance

## 🛠️ Technologies Used

### Frontend
- **React 18**: Modern React with hooks
- **CSS3**: Custom styling with flexbox and grid
- **SVG**: For relationship visualization
- **File API**: For project download functionality

### Generated Backend
- **Django 4.2+**: Python web framework
- **Django REST Framework**: API framework
- **SQLite**: Default database (configurable)

## 🏗️ Project Architecture

### React Components
- **App.jsx**: Main application component with state management
- **Model Management**: Create, edit, delete models
- **Field Management**: Dynamic field creation and editing
- **Relationship System**: Visual relationship creation and management
- **Code Generator**: Django project generation logic

### State Management
- React useState hooks for component state
- Model and relationship state management
- Real-time UI updates

### Code Generation Engine
- Django model generation with proper field types
- DRF serializer generation
- ViewSet creation with CRUD operations
- URL configuration
- Project structure creation

## 🎨 Customization

### Adding New Field Types
To add support for additional Django field types:

1. Update the `fieldTypes` array in `App.jsx`
2. Add corresponding mapping in `getDjangoFieldType()`
3. Update field options in `getFieldOptions()`

### Styling
- Modify `App.css` for UI customization
- Update color schemes and layout
- Customize model box appearance

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

1. Clone your fork
2. Install dependencies: `npm install`
3. Start development server: `npm start`
4. Make your changes
5. Test thoroughly before submitting PR

## 📋 Roadmap

### Planned Features
- [ ] **Import Existing Django Models**: Reverse engineer from existing projects
- [ ] **Advanced Field Options**: Support for field constraints, choices, etc.
- [ ] **Multiple Database Support**: PostgreSQL, MySQL configuration options
- [ ] **API Documentation**: Auto-generate OpenAPI/Swagger docs
- [ ] **Model Templates**: Pre-built model templates for common use cases
- [ ] **Export Options**: Support for FastAPI, Flask exports
- [ ] **Team Collaboration**: Share and collaborate on API designs
- [ ] **Version Control**: Project versioning and history
- [ ] **Testing Generation**: Auto-generate test cases
- [ ] **Docker Support**: Containerized deployment options

### Known Issues
- Model positioning may need adjustment after browser resize
- Large projects with many models may impact performance
- Relationship deletion is currently not supported via UI

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- React development team
- All contributors and beta testers

e API design meets visual creativity*
