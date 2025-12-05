import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, Save, Check, AlertCircle, Loader2, Plus, Trash2, Edit2, X } from 'lucide-react';
import './index.css';

function App() {
  const [items, setItems] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);

  // Queue Processor
  useEffect(() => {
    const processQueue = async () => {
      if (isProcessing) return;

      const nextItemIndex = items.findIndex(item => item.status === 'QUEUED');
      if (nextItemIndex === -1) return;

      setIsProcessing(true);
      const item = items[nextItemIndex];

      // Update status to SCANNING
      updateItemStatus(item.id, 'SCANNING');

      try {
        const formData = new FormData();
        formData.append('file', item.file);

        const response = await fetch(getApiUrl('scan'), {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) throw new Error('Scan failed');

        const result = await response.json();
        updateItem(item.id, { status: 'EDITING', data: result });
      } catch (err) {
        console.error(err);
        updateItem(item.id, { status: 'ERROR', error: 'Scan failed' });
      } finally {
        setIsProcessing(false);
      }
    };

    processQueue();
  }, [items, isProcessing]);

  const getApiUrl = (endpoint) => {
    const hostname = window.location.hostname;
    const host = hostname === 'localhost' ? '127.0.0.1' : hostname;
    return `http://${host}:8001/${endpoint}`;
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      const newItems = files.map(file => ({
        id: Math.random().toString(36).substr(2, 9),
        file,
        preview: URL.createObjectURL(file),
        status: 'QUEUED',
        data: {},
        error: ''
      }));
      setItems(prev => [...prev, ...newItems]);
    }
    // Reset input
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const updateItem = (id, updates) => {
    setItems(prev => prev.map(item => item.id === id ? { ...item, ...updates } : item));
  };

  const updateItemStatus = (id, status) => {
    updateItem(id, { status });
  };

  const updateItemData = (id, key, value) => {
    setItems(prev => prev.map(item => {
      if (item.id === id) {
        return { ...item, data: { ...item.data, [key]: value } };
      }
      return item;
    }));
  };

  const removeItem = (id) => {
    setItems(prev => prev.filter(item => item.id !== id));
  };

  const handleSaveItem = async (id) => {
    const item = items.find(i => i.id === id);
    if (!item) return;

    updateItemStatus(id, 'SAVING');
    try {
      const response = await fetch(getApiUrl('save'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data),
      });

      if (!response.ok) throw new Error('Save failed');

      updateItemStatus(id, 'SAVED');
    } catch (err) {
      console.error(err);
      updateItem(id, { status: 'ERROR', error: 'Save failed' });
    }
  };

  const handleSaveAll = async () => {
    const itemsToSave = items.filter(item => item.status === 'EDITING');

    // Sort by date ascending so that IDs are assigned chronologically
    itemsToSave.sort((a, b) => {
      const dateA = new Date(a.data.date || '9999/12/31'); // Fallback for missing date
      const dateB = new Date(b.data.date || '9999/12/31');
      return dateA - dateB;
    });

    // Save sequentially to avoid overwhelming the sheet API
    for (const item of itemsToSave) {
      await handleSaveItem(item.id);
    }
  };

  const renderField = (item, label, key, type = 'text', placeholder = '') => (
    <div className="form-group">
      <label>{label}</label>
      <input
        type={type}
        value={item.data[key] || ''}
        onChange={(e) => updateItemData(item.id, key, e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );

  return (
    <div className="app-container">
      <header className="header">
        <h1>OP Log Scanner</h1>
        {items.length > 0 && (
          <button className="btn-icon" onClick={() => fileInputRef.current.click()}>
            <Plus size={24} />
          </button>
        )}
      </header>

      <main>
        {items.length === 0 ? (
          <div className="upload-section">
            <button className="btn-primary" onClick={() => fileInputRef.current.click()}>
              <Camera size={24} />
              <span>Scan OP Logs</span>
            </button>
            <p className="hint">Select multiple images to batch scan</p>
          </div>
        ) : (
          <div className="items-list">
            {items.map(item => (
              <div key={item.id} className={`item-card status-${item.status.toLowerCase()}`}>
                <div className="item-header">
                  <img src={item.preview} alt="Thumb" className="item-thumb" />
                  <div className="item-info">
                    <span className="item-status-badge">{item.status}</span>
                    {item.data.id && <span className="item-id">ID: {item.data.id}</span>}
                  </div>
                  <button className="btn-icon danger" onClick={() => removeItem(item.id)}>
                    <X size={20} />
                  </button>
                </div>

                {item.status === 'SCANNING' && (
                  <div className="item-loading">
                    <Loader2 className="spinner" size={24} />
                    <span>Analyzing...</span>
                  </div>
                )}

                {item.status === 'ERROR' && (
                  <div className="item-error">
                    <AlertCircle size={16} />
                    <span>{item.error}</span>
                    <button onClick={() => updateItemStatus(item.id, 'QUEUED')}>Retry</button>
                  </div>
                )}

                {(item.status === 'EDITING' || item.status === 'SAVING' || item.status === 'SAVED') && (
                  <div className="item-form">
                    <div className="form-grid compact">
                      {renderField(item, 'ID', 'id')}
                      {renderField(item, 'Date', 'date')}
                      {renderField(item, 'Sex', 'sex', 'number')}
                      {renderField(item, 'Age', 'age', 'number')}
                      {renderField(item, 'Side', 'side', 'number')}
                      {renderField(item, 'Diag', 'diagnosis')}
                      {renderField(item, 'Cement', 'cement')}
                      {renderField(item, 'Stem', 'stem')}
                      {renderField(item, 'MDM', 'mdm', 'number')}
                      {renderField(item, 'Cup', 'cup')}
                      {renderField(item, 'Screw', 'screw')}
                      {renderField(item, 'Head', 'head')}
                      {renderField(item, 'Time', 'time', 'number')}
                      {renderField(item, 'Bleeding', 'bleeding', 'number')}
                      {renderField(item, 'Comment', 'comment')}
                    </div>

                    {item.status === 'EDITING' && (
                      <button className="btn-save-item" onClick={() => handleSaveItem(item.id)}>
                        <Save size={16} /> Save
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}

            <div className="batch-actions">
              <button className="btn-primary full-width" onClick={handleSaveAll}>
                <Save size={20} /> Save All Pending
              </button>
            </div>
          </div>
        )}

        <input
          type="file"
          accept="image/*"
          multiple // Allow multiple files
          capture="environment"
          ref={fileInputRef}
          onChange={handleFileSelect}
          hidden
        />
      </main>
    </div>
  );
}

export default App;
