# Visual Database Query Builder

![Visual Query Builder](https://img.shields.io/badge/Django-4.2.7-green)
![React](https://img.shields.io/badge/React-18.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A powerful web application that allows users to build complex database queries using an intuitive drag-and-drop interface with AI-powered performance predictions and optimization suggestions.

## 🚀 Features

### Core Functionality
- **🎯 Visual Query Building**: Drag-and-drop interface for building SQL queries without writing code
- **🔍 Multi-Database Support**: Compatible with PostgreSQL, MySQL, SQLite, and Oracle
- **⚡ Performance Prediction**: AI-powered analysis predicts query execution time and performance
- **🎯 Real-time Optimization**: Get optimization suggestions as you build your queries
- **📊 Schema Visualization**: Interactive database schema browser with table relationships
- **📈 Query History**: Track and analyze your query performance over time
- **📊 Performance Analytics**: Detailed metrics and insights for query optimization

### Advanced Features
- **🤖 AI-Powered Analysis**: Machine learning-based performance prediction
- **🔗 Auto-Join Detection**: Automatically detects and suggests table relationships
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🔐 Secure Connections**: Encrypted database passwords and secure connections
- **📤 Export Options**: Export query results in various formats
- **⚙️ Customizable Interface**: Flexible and intuitive user interface

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API development
- **SQLAlchemy** - Database connections and ORM
- **Scikit-learn** - Machine learning for performance prediction
- **SQLParse** - SQL query parsing and analysis
- **PostgreSQL/MySQL/SQLite** - Database support

### Frontend
- **React 18** - User interface framework
- **Tailwind CSS** - Styling and responsive design
- **Lucide React** - Modern icon library
- **Radix UI** - Accessible component primitives
- **Axios** - HTTP client for API calls

### Development Tools
- **Git** - Version control
- **ESLint** - Code linting
- **Prettier** - Code formatting

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- **Python 3.8+**
- **Node.js 16+**
- **Git**
- **pip** (Python package manager)
- **npm** (Node package manager)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/visual-query-builder.git
cd visual-query-builder
```

### 2. Backend Setup (Django)

#### Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Database Setup
```bash
# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 3. Frontend Setup (React)

#### Navigate to Frontend Directory
```bash
cd visual-query-builder-frontend
```

#### Install Node Dependencies
```bash
npm install
```

## 🏃‍♂️ Running the Application

### Development Mode

#### Start Backend Server
```bash
# In project root directory (with virtual environment activated)
python manage.py runserver
```
The Django backend will be available at `http://localhost:8000`

#### Start Frontend Server
```bash
# In visual-query-builder-frontend directory
npm start
```
The React frontend will be available at `http://localhost:3000`

### Production Mode

#### Build React Frontend
```bash
cd visual-query-builder-frontend
npm run build
```

#### Copy Built Files
```bash
cd ..
mkdir -p static
cp -r visual-query-builder-frontend/build/* static/
```

#### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### Start Production Server
```bash
python manage.py runserver
```
The complete application will be available at `http://localhost:8000`

## 📖 Usage Guide

### 1. Database Connection Setup

1. Access the Django admin panel at `http://localhost:8000/admin/`
2. Log in with your superuser credentials
3. Navigate to "Database Connections"
4. Add your database connection details:
   - **Name**: A friendly name for your connection
   - **Engine**: Choose from PostgreSQL, MySQL, SQLite, or Oracle
   - **Host**: Database server hostname
   - **Port**: Database server port
   - **Database**: Database name
   - **Username**: Database username
   - **Password**: Database password

### 2. Building Queries

1. **Select Connection**: Choose a database connection from the dropdown
2. **Browse Schema**: Explore your database tables and columns
3. **Drag & Drop**: 
   - Drag tables to the "FROM" section
   - Drag columns to the "SELECT" section
   - Drag columns to "WHERE" for filtering
   - Use "ORDER BY" for sorting
4. **Build Query**: Click "Build Query" to generate SQL and get performance analysis
5. **Execute**: Click "Execute Query" to run your query and see results

### 3. Performance Analysis

The application provides:
- **Execution Time Prediction**: AI-powered estimates
- **Complexity Score**: Query complexity analysis
- **Optimization Suggestions**: Recommendations for better performance
- **Resource Usage**: Memory and CPU estimates

## 🔌 API Endpoints

### Database Connections
- `GET /api/connections/` - List all database connections
- `POST /api/connections/` - Create new database connection
- `GET /api/connections/{id}/schema/` - Get database schema

### Query Operations
- `POST /api/query/build/` - Build and analyze query
- `POST /api/query/execute/` - Execute query
- `GET /api/query/history/` - Get query execution history

### Analytics
- `GET /api/analytics/` - Get performance analytics and metrics

### Example API Usage

#### Build a Query
```bash
curl -X POST http://localhost:8000/api/query/build/ \
  -H "Content-Type: application/json" \
  -d '{
    "visual_query": {
      "tables": ["users"],
      "columns": ["id", "name", "email"],
      "where": [],
      "orderBy": []
    },
    "connection_id": 1
  }'
```

## 🚀 Deployment

### PythonAnywhere Deployment

1. **Prepare for deployment**:
   ```bash
   # Build React frontend
   cd visual-query-builder-frontend
   npm run build
   cd ..
   cp -r visual-query-builder-frontend/build/* static/
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Deploy on PythonAnywhere**:
   - Follow the detailed deployment guide in `deploy_instructions.md`
   - Configure WSGI file
   - Set up static files
   - Configure database

### Environment Variables

Create a `.env` file in your project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

## 🧪 Testing

### Backend Tests
```bash
python manage.py test
```

### Frontend Tests
```bash
cd visual-query-builder-frontend
npm test
```

### API Testing with Postman
Import the provided Postman collection for comprehensive API testing.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Commit your changes**:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
6. **Push to the branch**:
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript code
- Write comprehensive tests
- Update documentation for new features
- Use meaningful commit messages

## 🔧 Configuration

### Django Settings

Key configuration options in `settings.py`:

```python
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Query Builder specific settings
QUERY_BUILDER_SETTINGS = {
    "DEFAULT_QUERY_TIMEOUT": 30,  # seconds
    "MAX_RESULT_ROWS": 10000,
    "ENABLE_QUERY_CACHING": True,
    "CACHE_TIMEOUT": 300,  # 5 minutes
}
```

### React Configuration

Frontend configuration in `visual-query-builder-frontend/src/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues
- **Import errors**: Ensure virtual environment is activated
- **Database connection errors**: Check database credentials and connectivity
- **Migration errors**: Run `python manage.py makemigrations` then `python manage.py migrate`

#### Frontend Issues
- **Build errors**: Delete `node_modules` and run `npm install` again
- **API connection errors**: Verify backend is running and CORS is configured
- **Component errors**: Check browser console for detailed error messages

#### Performance Issues
- **Slow queries**: Review optimization suggestions in the performance panel
- **High memory usage**: Consider query result pagination
- **Timeout errors**: Increase `DEFAULT_QUERY_TIMEOUT` in settings

### Getting Help

- Check the [Issues](https://github.com/yourusername/visual-query-builder/issues) page
- Create a new issue with detailed information
- Join our community discussions

## 📊 Performance Features

### Query Analysis
- **Complexity Scoring**: Automated assessment of query complexity
- **Execution Plan Analysis**: Detailed examination of database execution plans
- **Index Usage**: Analysis of index utilization and recommendations

### Machine Learning
- **Performance Prediction**: ML models predict query execution time
- **Pattern Recognition**: Identifies common performance bottlenecks
- **Adaptive Learning**: Models improve with more query data

### Optimization
- **Index Recommendations**: Suggests optimal indexes for better performance
- **Query Rewriting**: Proposes alternative query structures
- **Resource Monitoring**: Tracks CPU, memory, and I/O usage

## 🔐 Security

### Data Protection
- **Encrypted Passwords**: All database passwords are encrypted at rest
- **SQL Injection Prevention**: Parameterized queries prevent injection attacks
- **User Authentication**: Secure user authentication and session management
- **CORS Protection**: Configured CORS policies for API security

### Best Practices
- Regular security updates
- Environment variable usage for sensitive data
- HTTPS enforcement in production
- Regular security audits

## 📈 Roadmap

### Upcoming Features
- [ ] **Advanced Visualization**: Interactive query execution plans
- [ ] **Real-time Collaboration**: Multi-user query building
- [ ] **Export Options**: CSV, Excel, PDF export formats
- [ ] **Query Scheduling**: Automated query execution
- [ ] **Integration APIs**: Connect with popular BI tools
- [ ] **Advanced Analytics**: Detailed performance dashboards
- [ ] **Query Templates**: Pre-built query templates for common use cases
- [ ] **Data Visualization**: Built-in charting and graphing capabilities

### Performance Improvements
- [ ] Query result caching
- [ ] Connection pooling
- [ ] Async query execution
- [ ] Progressive loading for large datasets

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: [Project Wiki](https://github.com/yourusername/visual-query-builder/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/visual-query-builder/issues)
- **Email**: support@visualquerybuilder.com
- **Community**: [Discord Server](https://discord.gg/visualquerybuilder)

## 🎯 Acknowledgments

- Django community for the excellent web framework
- React team for the powerful frontend library
- Scikit-learn for machine learning capabilities
- All contributors who have helped improve this project

---

**Made with ❤️ by the Visual Query Builder Team**

For more information, visit our [website](https://visualquerybuilder.com) or check out the [documentation](https://docs.visualquerybuilder.com).
