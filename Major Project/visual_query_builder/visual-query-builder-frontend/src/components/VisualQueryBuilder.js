import React, { useState, useEffect } from 'react';
import { Database, Table, Settings, Play, Eye, ChevronDown, ChevronUp, X, Download, Copy } from 'lucide-react';
import { queryBuilderAPI } from '../api';
import { Button } from './ui/button';
import { Card, CardHeader, CardContent, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const VisualQueryBuilder = () => {
    const [connections, setConnections] = useState([]);
    const [selectedConnection, setSelectedConnection] = useState('');
    const [schema, setSchema] = useState({});
    const [expandedTables, setExpandedTables] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Visual query state
    const [visualQuery, setVisualQuery] = useState({
        tables: [],
        columns: [],
        joins: [],
        where: [],
        groupBy: [],
        orderBy: []
    });

    const [sqlQuery, setSqlQuery] = useState('-- Your generated SQL query will appear here\nSELECT * FROM table_name LIMIT 10;');
    const [performanceMetrics, setPerformanceMetrics] = useState({
        predictedTime: '--',
        complexityScore: '--',
        estimatedRows: '--',
        confidence: '--'
    });

    // New state for query results
    const [queryResults, setQueryResults] = useState(null);
    const [showResults, setShowResults] = useState(false);

    // Load connections on component mount
    useEffect(() => {
        loadConnections();
    }, []);

    const loadConnections = async () => {
        try {
            setLoading(true);
            const response = await queryBuilderAPI.getConnections();
            setConnections(response.data);
            setError('');
        } catch (error) {
            console.error('Failed to load connections:', error);
            setError('Failed to load database connections');
        } finally {
            setLoading(false);
        }
    };

    const loadSchema = async (connectionId) => {
        if (!connectionId) return;

        try {
            setLoading(true);
            const response = await queryBuilderAPI.getSchema(connectionId);
            setSchema(response.data.schema || {});
            setSelectedConnection(connectionId);
            setError('');
        } catch (error) {
            console.error('Failed to load schema:', error);
            setError('Failed to load database schema');
        } finally {
            setLoading(false);
        }
    };

    const toggleTable = (tableName) => {
        setExpandedTables(prev => ({
            ...prev,
            [tableName]: !prev[tableName]
        }));
    };

    // Drag and Drop Handlers
    const handleDragStart = (e, dragData) => {
        e.dataTransfer.setData('text/plain', JSON.stringify(dragData));
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    };

    const handleDragEnter = (e) => {
        e.preventDefault();
        e.currentTarget.classList.add('border-black', 'bg-gray-50');
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('border-black', 'bg-gray-50');
    };

    const handleDrop = (e, dropZone) => {
        e.preventDefault();
        e.currentTarget.classList.remove('border-black', 'bg-gray-50');

        try {
            const dragData = JSON.parse(e.dataTransfer.getData('text/plain'));

            switch (dropZone) {
                case 'select':
                    if (dragData.type === 'column') {
                        addToSelect(dragData);
                    }
                    break;
                case 'from':
                    if (dragData.type === 'table') {
                        addToFrom(dragData);
                    }
                    break;
                case 'where':
                    if (dragData.type === 'column') {
                        addToWhere(dragData);
                    }
                    break;
                case 'groupBy':
                    if (dragData.type === 'column') {
                        addToGroupBy(dragData);
                    }
                    break;
                case 'orderBy':
                    if (dragData.type === 'column') {
                        addToOrderBy(dragData);
                    }
                    break;
                default:
                    console.warn('Unknown drop zone:', dropZone);
                    break;
            }
        } catch (err) {
            console.error('Failed to parse drag data:', err);
        }
    };

    const addToSelect = (dragData) => {
        if (!visualQuery.columns.includes(dragData.fullName)) {
            setVisualQuery(prev => ({
                ...prev,
                columns: [...prev.columns, dragData.fullName]
            }));
        }
    };

    const addToFrom = (dragData) => {
        if (!visualQuery.tables.includes(dragData.table)) {
            setVisualQuery(prev => ({
                ...prev,
                tables: [...prev.tables, dragData.table]
            }));
        }
    };

    const addToWhere = (dragData) => {
        const newCondition = {
            column: dragData.fullName,
            operator: '=',
            value: ''
        };
        setVisualQuery(prev => ({
            ...prev,
            where: [...prev.where, newCondition]
        }));
    };

    const addToGroupBy = (dragData) => {
        if (!visualQuery.groupBy.includes(dragData.fullName)) {
            setVisualQuery(prev => ({
                ...prev,
                groupBy: [...prev.groupBy, dragData.fullName]
            }));
        }
    };

    const addToOrderBy = (dragData) => {
        const newOrder = {
            column: dragData.fullName,
            direction: 'ASC'
        };
        setVisualQuery(prev => ({
            ...prev,
            orderBy: [...prev.orderBy, newOrder]
        }));
    };

    const removeFromArray = (section, index) => {
        setVisualQuery(prev => ({
            ...prev,
            [section]: prev[section].filter((_, i) => i !== index)
        }));
    };

    const updateWhereCondition = (index, field, value) => {
        setVisualQuery(prev => ({
            ...prev,
            where: prev.where.map((condition, i) =>
                i === index ? { ...condition, [field]: value } : condition
            )
        }));
    };

    const updateOrderByCondition = (index, direction) => {
        setVisualQuery(prev => ({
            ...prev,
            orderBy: prev.orderBy.map((order, i) =>
                i === index ? { ...order, direction } : order
            )
        }));
    };

    const buildQuery = async () => {
        if (!selectedConnection) {
            setError('Please select a database connection first');
            return;
        }

        if (visualQuery.tables.length === 0) {
            setError('Please add at least one table to FROM section');
            return;
        }

        try {
            setLoading(true);
            const response = await queryBuilderAPI.buildQuery({
                visual_query: visualQuery,
                connection_id: selectedConnection
            });

            const data = response.data;
            setSqlQuery(data.sql_query);
            setPerformanceMetrics({
                predictedTime: data.prediction.predicted_time.toFixed(3),
                complexityScore: data.analysis.complexity_score,
                estimatedRows: data.analysis.estimated_rows.toLocaleString(),
                confidence: Math.round(data.prediction.confidence * 100)
            });
            setError('');
        } catch (error) {
            console.error('Failed to build query:', error);
            setError('Failed to build query: ' + (error.response?.data?.error || error.message));
        } finally {
            setLoading(false);
        }
    };

    const executeQuery = async () => {
        if (!sqlQuery || sqlQuery.includes('-- Your generated')) {
            setError('Please build a query first');
            return;
        }

        try {
            setLoading(true);
            const response = await queryBuilderAPI.executeQuery({
                sql_query: sqlQuery,
                connection_id: selectedConnection,
                visual_query: visualQuery
            });

            console.log('Query results:', response.data);

            // Store results and show results panel
            setQueryResults(response.data);
            setShowResults(true);
            setError('');

            // Success message
            alert(`Query executed successfully! ${response.data.rows_returned} rows returned in ${response.data.execution_time.toFixed(3)}s`);
        } catch (error) {
            console.error('Failed to execute query:', error);
            setError('Failed to execute query: ' + (error.response?.data?.error || error.message));
        } finally {
            setLoading(false);
        }
    };

    const selectAllColumns = () => {
        setVisualQuery(prev => ({
            ...prev,
            columns: ['*']
        }));
    };

    // Helper functions for results export
    const downloadResults = (format) => {
        if (!queryResults || !queryResults.results) return;

        let content = '';
        let filename = '';
        let mimeType = '';

        if (format === 'json') {
            content = JSON.stringify(queryResults.results, null, 2);
            filename = 'query_results.json';
            mimeType = 'application/json';
        } else if (format === 'csv') {
            if (queryResults.results.length > 0) {
                const headers = Object.keys(queryResults.results[0]);
                const csvContent = [
                    headers.join(','),
                    ...queryResults.results.map(row =>
                        headers.map(header => {
                            const value = row[header];
                            // Escape quotes and wrap in quotes if contains comma
                            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                                return `"${value.replace(/"/g, '""')}"`;
                            }
                            return value;
                        }).join(',')
                    )
                ].join('\n');
                content = csvContent;
            }
            filename = 'query_results.csv';
            mimeType = 'text/csv';
        }

        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const copyToClipboard = () => {
        if (!queryResults || !queryResults.results) return;

        const text = JSON.stringify(queryResults.results, null, 2);
        navigator.clipboard.writeText(text).then(() => {
            alert('Results copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
        });
    };

    // Results Panel Component
    const ResultsPanel = () => {
        if (!showResults || !queryResults) return null;

        return (
            <div className="mt-6 border-2 border-gray-300 rounded-lg shadow-sm bg-white">
                <div className="bg-gray-50 border-b border-gray-300 px-6 py-4 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-black">Query Results</h3>
                    <button
                        onClick={() => setShowResults(false)}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-6">
                    {/* Execution Summary */}
                    <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
                        <div className="text-sm text-green-800">
                            <strong>Execution Time:</strong> {queryResults.execution_time?.toFixed(3)}s |
                            <strong> Rows Returned:</strong> {queryResults.rows_returned} |
                            <strong> Data Source:</strong> {queryResults.data_source || 'database'}
                        </div>
                    </div>

                    {/* Performance Insights */}
                    {queryResults.performance_insights && (
                        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
                            <h4 className="font-medium text-blue-800 mb-2">Performance Insights:</h4>
                            <ul className="text-sm text-blue-700">
                                {queryResults.performance_insights.map((insight, index) => (
                                    <li key={index}>• {insight}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Results Table */}
                    {queryResults.results && queryResults.results.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="min-w-full border border-gray-300">
                                <thead className="bg-gray-50">
                                    <tr>
                                        {Object.keys(queryResults.results[0]).map(column => (
                                            <th key={column} className="px-4 py-2 border border-gray-300 text-left text-sm font-medium text-gray-700">
                                                {column}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {queryResults.results.slice(0, 100).map((row, index) => (
                                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                            {Object.keys(queryResults.results[0]).map(column => (
                                                <td key={column} className="px-4 py-2 border border-gray-300 text-sm">
                                                    {row[column] !== null && row[column] !== undefined ? String(row[column]) : 'NULL'}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>

                            {queryResults.results.length > 100 && (
                                <div className="mt-2 text-sm text-gray-600 text-center">
                                    Showing first 100 rows of {queryResults.rows_returned} total results
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            No data returned from query
                        </div>
                    )}

                    {/* Query Analysis */}
                    {queryResults.analysis && (
                        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                            <h4 className="font-medium text-yellow-800 mb-2">Query Analysis:</h4>
                            <div className="text-sm text-yellow-700 grid grid-cols-2 gap-4">
                                <div>Complexity Score: {queryResults.analysis.complexity_score}</div>
                                <div>Operations: {queryResults.analysis.operations?.join(', ')}</div>
                                <div>Tables: {queryResults.analysis.tables?.join(', ')}</div>
                                <div>Joins: {queryResults.analysis.joins}</div>
                            </div>

                            {queryResults.analysis.optimization_suggestions?.length > 0 && (
                                <div className="mt-2">
                                    <strong>Optimization Suggestions:</strong>
                                    <ul className="mt-1">
                                        {queryResults.analysis.optimization_suggestions.map((suggestion, index) => (
                                            <li key={index} className="text-sm">• {suggestion}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Export Options */}
                    <div className="mt-4 flex gap-2">
                        <button
                            onClick={() => downloadResults('json')}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                        >
                            <Download className="w-4 h-4" />
                            Export JSON
                        </button>
                        <button
                            onClick={() => downloadResults('csv')}
                            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
                        >
                            <Download className="w-4 h-4" />
                            Export CSV
                        </button>
                        <button
                            onClick={copyToClipboard}
                            className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                        >
                            <Copy className="w-4 h-4" />
                            Copy to Clipboard
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-gray-50 p-5">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-5xl font-light mb-3 text-black">Visual Database Query Builder</h1>
                    <p className="text-xl text-gray-600">Build complex database queries with drag-and-drop simplicity and AI-powered performance predictions</p>
                </div>

                {/* Error Display */}
                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[600px]">
                    {/* Database Schema Panel */}
                    <Card className="border-2 border-gray-300 shadow-sm">
                        <CardHeader className="bg-gray-50 border-b border-gray-300 pb-6">
                            <CardTitle className="flex items-center text-black">
                                <Database className="mr-3" />
                                Database Schema
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-6">
                            {/* Connection Selector */}
                            <div className="mb-8">
                                <Select value={selectedConnection} onValueChange={loadSchema}>
                                    <SelectTrigger className="w-full border-2 border-gray-300 focus:border-black">
                                        <SelectValue placeholder="Select Database Connection" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {connections.map(conn => (
                                            <SelectItem key={conn.id} value={conn.id.toString()}>
                                                {conn.name} ({conn.database})
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Database Overview */}
                            {selectedConnection && (
                                <div className="bg-gray-50 border border-gray-300 rounded p-3 mb-6">
                                    <h4 className="font-semibold mb-3 text-black">Database Overview</h4>
                                    <div className="grid grid-cols-3 gap-2 mb-3">
                                        <div className="text-center bg-white border border-gray-200 rounded p-2">
                                            <div className="text-xl font-bold text-black">{Object.keys(schema).length}</div>
                                            <div className="text-xs text-gray-600">Tables</div>
                                        </div>
                                        <div className="text-center bg-white border border-gray-200 rounded p-2">
                                            <div className="text-xl font-bold text-black">
                                                {Object.values(schema).reduce((total, table) => total + (table.stats?.record_count || 0), 0).toLocaleString()}
                                            </div>
                                            <div className="text-xs text-gray-600">Total Records</div>
                                        </div>
                                        <div className="text-center bg-white border border-gray-200 rounded p-2">
                                            <div className="text-xl font-bold text-black">0</div>
                                            <div className="text-xs text-gray-600">Relationships</div>
                                        </div>
                                    </div>
                                    <div className="text-sm text-gray-700">
                                        Database schema loaded successfully
                                    </div>
                                </div>
                            )}

                            {/* Loading State */}
                            {loading && (
                                <div className="text-center py-4">
                                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
                                    <p className="mt-2 text-gray-600">Loading...</p>
                                </div>
                            )}

                            {/* Schema Display */}
                            <div className="space-y-4 max-h-96 overflow-y-auto">
                                {Object.keys(schema).map(tableName => (
                                    <div key={tableName} className="border-2 border-gray-300 rounded-lg overflow-hidden">
                                        {/* Table Header - Draggable */}
                                        <div
                                            className="p-3 bg-white border-b border-gray-300 cursor-grab active:cursor-grabbing flex justify-between items-center hover:bg-gray-50 transition-colors"
                                            draggable
                                            onDragStart={(e) => handleDragStart(e, {
                                                type: 'table',
                                                table: tableName
                                            })}
                                            onClick={() => toggleTable(tableName)}
                                        >
                                            <div>
                                                <div className="font-semibold flex items-center text-black">
                                                    <Table className="w-4 h-4 mr-2" />
                                                    {tableName}
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    {schema[tableName].stats?.record_count || 1000} rows
                                                </div>
                                            </div>
                                            {expandedTables[tableName] ?
                                                <ChevronUp className="w-5 h-5" /> :
                                                <ChevronDown className="w-5 h-5" />
                                            }
                                        </div>

                                        {/* Columns - Show when expanded */}
                                        {expandedTables[tableName] && (
                                            <div className="p-2 space-y-1 bg-gray-50">
                                                {schema[tableName].columns?.map(column => (
                                                    <div
                                                        key={column.name}
                                                        className="p-2 bg-white hover:bg-gray-100 rounded cursor-grab active:cursor-grabbing flex justify-between items-center text-sm border border-gray-200 hover:border-gray-400 transition-colors"
                                                        draggable
                                                        onDragStart={(e) => handleDragStart(e, {
                                                            type: 'column',
                                                            table: tableName,
                                                            column: column.name,
                                                            fullName: `${tableName}.${column.name}`,
                                                            dataType: column.type
                                                        })}
                                                    >
                                                        <span className="font-medium flex items-center">
                                                            <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                                                            {column.name}
                                                            {column.primary_key && <span className="ml-1 text-black">🔑</span>}
                                                        </span>
                                                        <span className="text-gray-600 font-mono text-xs">{column.type}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}

                                {Object.keys(schema).length === 0 && !loading && selectedConnection && (
                                    <div className="text-center py-8 text-gray-500">
                                        <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
                                        <p>No tables found in the selected database</p>
                                    </div>
                                )}

                                {!selectedConnection && (
                                    <div className="text-center py-8 text-gray-500">
                                        <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
                                        <p>Select a database connection to view schema</p>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Query Builder Panel */}
                    <Card className="border-2 border-gray-300 shadow-sm">
                        <CardHeader className="bg-gray-50 border-b border-gray-300">
                            <CardTitle className="flex items-center text-black">
                                <Settings className="mr-3" />
                                Query Builder
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                {/* SELECT Columns */}
                                <div>
                                    <h4 className="font-medium mb-2 text-black">SELECT Columns</h4>
                                    <div
                                        className="min-h-16 border-2 border-dashed border-gray-300 rounded-lg p-3 bg-gray-50 transition-colors cursor-pointer"
                                        onDragOver={handleDragOver}
                                        onDragEnter={handleDragEnter}
                                        onDragLeave={handleDragLeave}
                                        onDrop={(e) => handleDrop(e, 'select')}
                                        onClick={selectAllColumns}
                                    >
                                        {visualQuery.columns.length === 0 ? (
                                            <div className="text-gray-400 text-center py-2 italic">
                                                Drag columns here or click to select all (*)
                                            </div>
                                        ) : (
                                            <div className="flex flex-wrap gap-2">
                                                {visualQuery.columns.map((column, index) => (
                                                    <span key={index} className="bg-black text-white px-3 py-1 rounded text-sm flex items-center">
                                                        {column}
                                                        <button
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                removeFromArray('columns', index);
                                                            }}
                                                            className="ml-2 hover:bg-gray-700 rounded-full w-4 h-4 flex items-center justify-center text-xs"
                                                        >
                                                            ×
                                                        </button>
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* FROM Tables */}
                                <div>
                                    <h4 className="font-medium mb-2 text-black">FROM Tables</h4>
                                    <div
                                        className="min-h-16 border-2 border-dashed border-gray-300 rounded-lg p-3 bg-gray-50 transition-colors"
                                        onDragOver={handleDragOver}
                                        onDragEnter={handleDragEnter}
                                        onDragLeave={handleDragLeave}
                                        onDrop={(e) => handleDrop(e, 'from')}
                                    >
                                        {visualQuery.tables.length === 0 ? (
                                            <div className="text-gray-400 text-center py-2 italic">
                                                Drag tables here
                                            </div>
                                        ) : (
                                            <div className="flex flex-wrap gap-2">
                                                {visualQuery.tables.map((table, index) => (
                                                    <span key={index} className="bg-gray-600 text-white px-3 py-1 rounded text-sm flex items-center">
                                                        {table}
                                                        <button
                                                            onClick={() => removeFromArray('tables', index)}
                                                            className="ml-2 hover:bg-gray-500 rounded-full w-4 h-4 flex items-center justify-center text-xs"
                                                        >
                                                            ×
                                                        </button>
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* WHERE Conditions */}
                                <div>
                                    <h4 className="font-medium mb-2 text-black">WHERE Conditions</h4>
                                    <div
                                        className="min-h-16 border-2 border-dashed border-gray-300 rounded-lg p-3 bg-gray-50 transition-colors"
                                        onDragOver={handleDragOver}
                                        onDragEnter={handleDragEnter}
                                        onDragLeave={handleDragLeave}
                                        onDrop={(e) => handleDrop(e, 'where')}
                                    >
                                        {visualQuery.where.length === 0 ? (
                                            <div className="text-gray-400 text-center py-2 italic">
                                                Drag columns to add filters
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                {visualQuery.where.map((condition, index) => (
                                                    <div key={index} className="bg-white border border-gray-300 p-2 rounded flex items-center gap-2 flex-wrap">
                                                        <span className="text-sm font-medium">{condition.column}</span>
                                                        <select
                                                            value={condition.operator}
                                                            onChange={(e) => updateWhereCondition(index, 'operator', e.target.value)}
                                                            className="text-xs border border-gray-300 rounded px-1 py-1"
                                                        >
                                                            <option value="=">=</option>
                                                            <option value="!=">!=</option>
                                                            <option value=">">{'>'}</option>
                                                            <option value="<">{'<'}</option>
                                                            <option value="LIKE">LIKE</option>
                                                        </select>
                                                        <input
                                                            type="text"
                                                            value={condition.value}
                                                            onChange={(e) => updateWhereCondition(index, 'value', e.target.value)}
                                                            placeholder="Value"
                                                            className="text-xs border border-gray-300 rounded px-2 py-1 flex-1 min-w-20"
                                                        />
                                                        <button
                                                            onClick={() => removeFromArray('where', index)}
                                                            className="text-red-500 hover:bg-red-100 rounded-full w-6 h-6 flex items-center justify-center text-xs"
                                                        >
                                                            ×
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* ORDER BY */}
                                <div>
                                    <h4 className="font-medium mb-2 text-black">ORDER BY</h4>
                                    <div
                                        className="min-h-16 border-2 border-dashed border-gray-300 rounded-lg p-3 bg-gray-50 transition-colors"
                                        onDragOver={handleDragOver}
                                        onDragEnter={handleDragEnter}
                                        onDragLeave={handleDragLeave}
                                        onDrop={(e) => handleDrop(e, 'orderBy')}
                                    >
                                        {visualQuery.orderBy.length === 0 ? (
                                            <div className="text-gray-400 text-center py-2 italic">
                                                Drag columns for sorting
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                {visualQuery.orderBy.map((order, index) => (
                                                    <div key={index} className="bg-white border border-gray-300 p-2 rounded flex items-center gap-2">
                                                        <span className="text-sm font-medium">{order.column}</span>
                                                        <select
                                                            value={order.direction}
                                                            onChange={(e) => updateOrderByCondition(index, e.target.value)}
                                                            className="text-xs border border-gray-300 rounded px-1 py-1"
                                                        >
                                                            <option value="ASC">ASC</option>
                                                            <option value="DESC">DESC</option>
                                                        </select>
                                                        <button
                                                            onClick={() => removeFromArray('orderBy', index)}
                                                            className="text-red-500 hover:bg-red-100 rounded-full w-6 h-6 flex items-center justify-center text-xs"
                                                        >
                                                            ×
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6 flex gap-3">
                                <Button
                                    onClick={buildQuery}
                                    disabled={loading}
                                    className="flex-1 bg-black text-white hover:bg-gray-800 border-2 border-black"
                                    variant="default"
                                >
                                    <Settings className="mr-2 w-4 h-4" />
                                    {loading ? 'Building...' : 'Build Query'}
                                </Button>
                                <Button
                                    onClick={executeQuery}
                                    disabled={loading || sqlQuery.includes('-- Your generated')}
                                    className="flex-1 bg-black text-white hover:bg-gray-800 border-2 border-black"
                                    variant="default"
                                >
                                    <Play className="mr-2 w-4 h-4" />
                                    {loading ? 'Executing...' : 'Execute Query'}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Performance Panel */}
                    <Card className="border-2 border-gray-300 shadow-sm">
                        <CardHeader className="bg-gray-50 border-b border-gray-300">
                            <CardTitle className="flex items-center text-black">
                                <Eye className="mr-3" />
                                Query Analysis & Performance
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {/* SQL Preview */}
                            <div className="bg-black text-green-400 p-4 rounded-lg mb-6 font-mono text-sm">
                                <pre className="whitespace-pre-wrap">{sqlQuery}</pre>
                            </div>

                            {/* Performance Metrics */}
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-center">
                                    <div className="text-2xl font-bold text-black">{performanceMetrics.predictedTime}</div>
                                    <div className="text-sm text-gray-600">Predicted Time (s)</div>
                                </div>
                                <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-center">
                                    <div className="text-2xl font-bold text-black">{performanceMetrics.complexityScore}</div>
                                    <div className="text-sm text-gray-600">Complexity Score</div>
                                </div>
                                <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-center">
                                    <div className="text-2xl font-bold text-black">{performanceMetrics.estimatedRows}</div>
                                    <div className="text-sm text-gray-600">Estimated Rows</div>
                                </div>
                                <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-center">
                                    <div className="text-2xl font-bold text-black">{performanceMetrics.confidence}</div>
                                    <div className="text-sm text-gray-600">Confidence %</div>
                                </div>
                            </div>

                            {/* Performance Category */}
                            <div className="bg-black text-white p-3 rounded-lg text-center font-medium mb-4">
                                Ready to build query
                            </div>

                            {/* Optimization Suggestions */}
                            <div>
                                <h4 className="font-medium mb-3 text-black">Optimization Suggestions</h4>
                                <div className="bg-gray-50 border border-gray-200 p-3 rounded">
                                    <p className="text-sm text-gray-700">Build a query to see optimization suggestions</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Results Panel - Added here */}
                <ResultsPanel />
            </div>
        </div>
    );
};

export default VisualQueryBuilder;