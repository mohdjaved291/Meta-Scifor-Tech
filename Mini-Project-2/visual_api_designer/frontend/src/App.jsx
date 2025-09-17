import React, { useState, useRef, useMemo } from 'react';
import { useToast } from './hooks/use-toast';
import { Toaster } from './components/ui/toaster';
import './App.css';

const FIELD_OPTIONS = [
  { label: "Number (Integer)", value: "integer" },
  { label: "Text (String)", value: "string" },
  { label: "Email", value: "email" },
  { label: "Date", value: "date" },
  { label: "Date & Time", value: "datetime" },
  { label: "True/False", value: "boolean" },
  { label: "Long Text (TextField)", value: "text" },
];

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';


function uid(prefix = "id") {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
}

function TypeBadge({ type }) {
  const typeMap = {
    integer: "Number",
    string: "String",
    email: "Email",
    date: "Date",
    datetime: "DateTime",
    boolean: "Boolean",
    text: "Text"
  };

  return (
    <span className="type-badge">
      {typeMap[type] || type}
    </span>
  );
}

function SectionTitle({ children }) {
  return <h2 className="section-title">{children}</h2>;
}

const App = () => {
  const [models, setModels] = useState([
    {
      id: uid("mdl"),
      name: "User",
      fields: [
        { id: uid("f"), name: "id", type: "integer", auto: true, primary: true },
        { id: uid("f"), name: "email", type: "email" },
        { id: uid("f"), name: "full_name", type: "string" },
        { id: uid("f"), name: "membership_date", type: "date" },
      ],
      relations: [],
      position: { x: 50, y: 50 }
    },
    {
      id: uid("mdl"),
      name: "Book",
      fields: [
        { id: uid("f"), name: "id", type: "integer", auto: true, primary: true },
        { id: uid("f"), name: "title", type: "string" },
        { id: uid("f"), name: "author", type: "string" },
        { id: uid("f"), name: "isbn", type: "string" },
        { id: uid("f"), name: "publication_year", type: "integer" },
      ],
      relations: [],
      position: { x: 350, y: 50 }
    },
    {
      id: uid("mdl"),
      name: "BorrowRecord",
      fields: [
        { id: uid("f"), name: "id", type: "integer", auto: true, primary: true },
        { id: uid("f"), name: "borrow_date", type: "datetime" },
        { id: uid("f"), name: "return_date", type: "datetime" },
        { id: uid("f"), name: "returned", type: "boolean" },
      ],
      relations: [],
      position: { x: 650, y: 50 }
    },
  ]);

  const [relationships, setRelationships] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [projectName, setProjectName] = useState('My API Project');
  const [isGenerating, setIsGenerating] = useState(false);
  const canvasRef = useRef(null);

  const { toast } = useToast();

  const selectedId = selectedModel?.id || null;
  const selected = useMemo(() => models.find((m) => m.id === selectedId) || null, [models, selectedId]);

  const addModel = () => {
    const newModel = {
      id: uid("mdl"),
      name: `NewModel${models.length + 1}`,
      fields: [
        { id: uid("f"), name: 'id', type: 'integer', auto: true, primary: true },
      ],
      relations: [],
      position: {
        x: 50 + (models.length * 100),
        y: 50
      }
    };
    setModels(prev => [...prev, newModel]);
    setSelectedModel(newModel);
  };

  const removeField = (modelId, fieldId) => {
    setModels(prev =>
      prev.map(m => m.id === modelId ? {
        ...m,
        fields: m.fields.filter(f => f.id !== fieldId)
      } : m)
    );
  };

  const addField = (modelId) => {
    const newField = {
      id: uid("f"),
      name: 'new_field',
      type: 'string',
      max_length: 255,
    };

    setModels(prev =>
      prev.map(m => m.id === modelId ? {
        ...m,
        fields: [...m.fields, newField]
      } : m)
    );
  };

  const updateField = (modelId, fieldId, patch) => {
    setModels(prev =>
      prev.map(m =>
        m.id === modelId ? {
          ...m,
          fields: m.fields.map(f => f.id === fieldId ? { ...f, ...patch } : f)
        } : m
      )
    );

    if (selectedModel && selectedModel.id === modelId) {
      setSelectedModel(prevSelected => ({
        ...prevSelected,
        fields: prevSelected.fields.map(f => f.id === fieldId ? { ...f, ...patch } : f)
      }));
    }
  };

  const renameModel = (modelId, name) => {
    setModels(prev => prev.map(m => m.id === modelId ? { ...m, name } : m));

    if (selectedModel && selectedModel.id === modelId) {
      setSelectedModel(prev => ({ ...prev, name }));
    }
  };

  const removeModel = (modelId) => {
    const removed = models.find(m => m.id === modelId);
    const next = models.filter(m => m.id !== modelId);
    setModels(next);

    if (selectedModel?.id === modelId) {
      setSelectedModel(next[0] || null);
    }

    setRelationships(prev =>
      prev.filter(rel => rel.from_model_id !== modelId && rel.to_model_id !== modelId)
    );

    if (removed) {
      toast({
        title: "Model removed",
        description: `${removed.name} was deleted.`,
      });
    }
  };

  const linkAllModels = () => {
    const updated = models.map(m => ({
      ...m,
      relations: models.filter(o => o.id !== m.id).map(o => o.id),
    }));
    setModels(updated);

    const newRelationships = [];
    for (let i = 0; i < models.length; i++) {
      for (let j = 0; j < models.length; j++) {
        if (i !== j) {
          const fromModel = models[i];
          const toModel = models[j];
          newRelationships.push({
            id: uid("rel"),
            from_model_id: fromModel.id,
            to_model_id: toModel.id,
            from_model: fromModel.name,
            to_model: toModel.name,
            field_name: toModel.name.toLowerCase(),
            related_name: `${fromModel.name.toLowerCase()}_set`,
            created_at: Date.now()
          });
        }
      }
    }
    setRelationships(newRelationships);

    const names = updated.map(m => m.name).join(", ");
    toast({
      title: "Linked all models",
      description: `${updated.length} models linked: ${names}`,
    });
  };

  const generateCode = async () => {
    setIsGenerating(true);

    setTimeout(() => {
      try {
        // Create schema from visual design
        const schema = {
          models: models.map(model => ({
            name: model.name,
            fields: model.fields.filter(f => !f.auto)
          })),
          relationships
        };

        // Generate complete Django project
        const djangoFiles = generateDjangoProject(schema, projectName);

        // Create and download the complete project
        downloadProjectFiles(djangoFiles, projectName);

        toast({
          title: "Django code generated!",
          description: "Your complete project has been downloaded.",
        });

      } catch (error) {
        console.error('Generation failed:', error);
        toast({
          title: "Generation failed",
          description: error.message,
          variant: "destructive",
        });
      } finally {
        setIsGenerating(false);
      }
    }, 1000);
  };

  // Generate complete Django project structure
  const generateDjangoProject = (schema, projectName) => {
    const appName = 'api';
    const projectSlug = projectName.toLowerCase().replace(/\s+/g, '_');
    const files = {};

    // Generate models.py with relationships
    files[`${projectSlug}/${appName}/models.py`] = generateModelsFile(schema);
    files[`${projectSlug}/${appName}/serializers.py`] = generateSerializersFile(schema);
    files[`${projectSlug}/${appName}/views.py`] = generateViewsFile(schema);
    files[`${projectSlug}/requirements.txt`] = 'Django>=4.2.0\ndjangorestframework>=3.14.0\n';
    files[`${projectSlug}/README.md`] = `# ${projectName}\n\nGenerated Django REST API with ${schema.models.length} models and ${schema.relationships.length} relationships.\n\n## Models\n${schema.models.map(m => `- ${m.name}`).join('\n')}\n\n## Setup\n1. pip install -r requirements.txt\n2. python manage.py makemigrations\n3. python manage.py migrate\n4. python manage.py runserver`;

    return files;
  };

  const generateModelsFile = (schema) => {
    let content = `from django.db import models\n\n`;

    schema.models.forEach(model => {
      content += `class ${model.name}(models.Model):\n`;
      model.fields.forEach(field => {
        const fieldType = field.type === 'string' ? 'CharField' :
          field.type === 'integer' ? 'IntegerField' :
            field.type === 'email' ? 'EmailField' :
              field.type === 'date' ? 'DateField' :
                field.type === 'datetime' ? 'DateTimeField' :
                  field.type === 'boolean' ? 'BooleanField' : 'CharField';
        const options = field.type === 'string' || field.type === 'email' ? '(max_length=255)' : '()';
        content += `    ${field.name} = models.${fieldType}${options}\n`;
      });

      // Add relationships
      const modelRelationships = schema.relationships.filter(rel => rel.from_model === model.name);
      modelRelationships.forEach(rel => {
        content += `    ${rel.field_name} = models.ForeignKey(${rel.to_model}, on_delete=models.CASCADE)\n`;
      });

      content += `\n    def __str__(self):\n        return str(self.${model.fields[0]?.name || 'id'})\n\n`;
    });

    return content;
  };

  const generateSerializersFile = (schema) => {
    let content = `from rest_framework import serializers\nfrom .models import ${schema.models.map(m => m.name).join(', ')}\n\n`;

    schema.models.forEach(model => {
      content += `class ${model.name}Serializer(serializers.ModelSerializer):\n`;
      content += `    class Meta:\n`;
      content += `        model = ${model.name}\n`;
      content += `        fields = '__all__'\n\n`;
    });

    return content;
  };

  const generateViewsFile = (schema) => {
    let content = `from rest_framework import viewsets\nfrom .models import ${schema.models.map(m => m.name).join(', ')}\nfrom .serializers import ${schema.models.map(m => m.name + 'Serializer').join(', ')}\n\n`;

    schema.models.forEach(model => {
      content += `class ${model.name}ViewSet(viewsets.ModelViewSet):\n`;
      content += `    queryset = ${model.name}.objects.all()\n`;
      content += `    serializer_class = ${model.name}Serializer\n\n`;
    });

    return content;
  };

  const downloadProjectFiles = (files, projectName) => {
    let content = `# ${projectName} - Django REST API\n# Generated Files:\n\n`;

    Object.entries(files).forEach(([filepath, fileContent]) => {
      content += `\n${'='.repeat(50)}\n# FILE: ${filepath}\n${'='.repeat(50)}\n\n`;
      content += fileContent;
      content += '\n';
    });

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName.toLowerCase().replace(/\s+/g, '_')}_django_project.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <main className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="app-icon">
              <defs>
                <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#8b5cf6', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#a855f7', stopOpacity: 1 }} />
                </linearGradient>
                <linearGradient id="cardGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#ffffff', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#f3f4f6', stopOpacity: 1 }} />
                </linearGradient>
              </defs>
              <rect width="32" height="32" rx="6" fill="url(#bgGradient)" />
              <rect x="4" y="6" width="8" height="7" rx="2" fill="url(#cardGradient)" stroke="#e5e7eb" strokeWidth="0.5" />
              <line x1="5.5" y1="8" x2="10.5" y2="8" stroke="#8b5cf6" strokeWidth="0.5" />
              <line x1="5.5" y1="9.5" x2="9" y2="9.5" stroke="#6b7280" strokeWidth="0.5" />
              <line x1="5.5" y1="11" x2="10" y2="11" stroke="#6b7280" strokeWidth="0.5" />
              <rect x="14" y="6" width="8" height="7" rx="2" fill="url(#cardGradient)" stroke="#e5e7eb" strokeWidth="0.5" />
              <line x1="15.5" y1="8" x2="20.5" y2="8" stroke="#8b5cf6" strokeWidth="0.5" />
              <line x1="15.5" y1="9.5" x2="19" y2="9.5" stroke="#6b7280" strokeWidth="0.5" />
              <line x1="15.5" y1="11" x2="20" y2="11" stroke="#6b7280" strokeWidth="0.5" />
              <rect x="9" y="16" width="8" height="7" rx="2" fill="url(#cardGradient)" stroke="#e5e7eb" strokeWidth="0.5" />
              <line x1="10.5" y1="18" x2="15.5" y2="18" stroke="#8b5cf6" strokeWidth="0.5" />
              <line x1="10.5" y1="19.5" x2="14" y2="19.5" stroke="#6b7280" strokeWidth="0.5" />
              <line x1="10.5" y1="21" x2="15" y2="21" stroke="#6b7280" strokeWidth="0.5" />
              <path d="M12 13 L14 16" stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M18 13 L17 16" stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" />
              <circle cx="12" cy="13" r="1.5" fill="#ffffff" />
              <circle cx="18" cy="13" r="1.5" fill="#ffffff" />
              <circle cx="14" cy="16" r="1.5" fill="#ffffff" />
              <circle cx="17" cy="16" r="1.5" fill="#ffffff" />
              <g opacity="0.3">
                <circle cx="26" cy="26" r="0.5" fill="#ffffff" />
                <circle cx="28" cy="26" r="0.5" fill="#ffffff" />
                <circle cx="26" cy="28" r="0.5" fill="#ffffff" />
                <circle cx="28" cy="28" r="0.5" fill="#ffffff" />
              </g>
            </svg>
            <h1>Visual API Designer</h1>
          </div>
          <div className="header-right">
            <input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="project-input"
              placeholder="Project name"
            />
            <button
              onClick={linkAllModels}
              type="button"
              className="btn btn-secondary"
            >
              Link All
            </button>
            <button
              onClick={generateCode}
              disabled={isGenerating || models.length === 0}
              className="btn btn-primary"
            >
              {isGenerating ? 'Generating...' : 'Generate Django Code'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className={`app-body ${models.length > 0 ? "with-sidebar" : "no-sidebar"}`}>
        {/* Sidebar */}
        {models.length > 0 && (
          <aside className="sidebar">
            <div className="sidebar-content">
              <SectionTitle>Components</SectionTitle>
              <div className="button-group">
                <button
                  onClick={addModel}
                  className="btn btn-primary btn-full"
                >
                  + Add Model
                </button>
                <button
                  className="btn btn-secondary btn-full"
                  onClick={() => toast({
                    title: "Arrange Models",
                    description: "Auto-arrange feature coming soon!"
                  })}
                >
                  Arrange
                </button>
              </div>

              <div className="divider"></div>

              <SectionTitle>Edit Model</SectionTitle>
              {selected ? (
                <div className="model-editor">
                  <label className="field-label">Model Name</label>
                  <input
                    value={selected.name}
                    onChange={(e) => renameModel(selected.id, e.target.value)}
                    className="input"
                  />

                  <div className="fields-section">
                    <div className="fields-header">
                      <span className="field-label">Fields</span>
                      <button
                        onClick={() => addField(selected.id)}
                        className="btn btn-small"
                      >
                        + Add Field
                      </button>
                    </div>

                    <ul className={`fields-list ${selected.fields.length > 5 ? "scrollable" : ""}`}>
                      {selected.fields.map((f) => (
                        <li key={f.id} className="field-item">
                          <div className="field-controls">
                            <input
                              value={f.name}
                              onChange={(e) => updateField(selected.id, f.id, { name: e.target.value })}
                              disabled={f.auto}
                              className="input input-small"
                            />
                            <select
                              value={f.type}
                              onChange={(e) => updateField(selected.id, f.id, { type: e.target.value })}
                              disabled={f.auto}
                              className="select select-small"
                            >
                              {FIELD_OPTIONS.map((opt) => (
                                <option key={opt.value} value={opt.value}>
                                  {opt.label}
                                </option>
                              ))}
                            </select>
                            {!f.auto && (
                              <button
                                onClick={() => removeField(selected.id, f.id)}
                                className="btn btn-danger btn-small"
                              >
                                ×
                              </button>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="no-selection">Select a model card to edit its fields.</p>
              )}
            </div>
          </aside>
        )}

        {/* Canvas */}
        <section className="canvas" ref={canvasRef}>
          {models.length === 0 ? (
            <div className="empty-state">
              <h2>Welcome to Visual API Designer</h2>
              <p>Start by adding your first model to design your API</p>
              <button
                onClick={addModel}
                className="btn btn-primary"
              >
                + Add Your First Model
              </button>
            </div>
          ) : (
            <div className="models-grid">
              {models.map((m) => (
                <div
                  key={m.id}
                  onClick={() => setSelectedModel(m)}
                  className={`model-card ${selectedId === m.id ? 'selected' : ''}`}
                >
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm(`Are you sure you want to delete the "${m.name}" model?`)) {
                        removeModel(m.id);
                      }
                    }}
                    className="model-delete-btn"
                    type="button"
                  >
                    ×
                  </button>

                  <div className="model-header">
                    <h3>{m.name}</h3>
                    <span className="field-count">
                      {m.fields.length} fields
                    </span>
                  </div>

                  <ul className={`field-list ${m.fields.length > 5 ? "scrollable" : ""}`}>
                    {m.fields.map((f) => (
                      <li key={f.id} className="field-preview">
                        <span className="field-name">{f.name}</span>
                        <TypeBadge type={f.type} />
                      </li>
                    ))}
                  </ul>

                  <div className="model-footer">
                    <span className="links-count">
                      {m.relations.length} links
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
      <Toaster />
    </main>
  );
};

export default App;