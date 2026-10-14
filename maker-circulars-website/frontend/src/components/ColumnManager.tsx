import React, { useState } from 'react';
import { ColumnDef } from '../types';
import { FiX, FiPlus, FiTrash2, FiEdit2 } from 'react-icons/fi';

interface ColumnManagerProps {
  columns: ColumnDef[];
  onClose: () => void;
  onAdd: (name: string, type: string) => void;
  onDelete: (id: number) => void;
  onRename: (id: number, newName: string) => void;
}

export const ColumnManager: React.FC<ColumnManagerProps> = ({ columns, onClose, onAdd, onDelete, onRename }) => {
  const [newColName, setNewColName] = useState('');
  const [newColType, setNewColType] = useState('text');

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '600px', maxHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '20px', borderBottom: '1px solid var(--border)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Manage Columns</h2>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)' }}><FiX size={24} /></button>
        </div>
        
        <div style={{ padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {columns.filter(c => !['_id', 'id', 'dms'].includes(c.name.toLowerCase())).map(col => {
            const displayName = col.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            return (
            <div key={col.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: 'var(--surface-elevated)', borderRadius: '8px' }}>
              <div>
                <div style={{ fontWeight: 500 }}>{displayName}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{col.data_type}</div>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button style={{ background: 'transparent', border: 'none', color: 'var(--accent)' }}><FiEdit2 /></button>
                <button onClick={() => onDelete(col.id)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)' }}><FiTrash2 /></button>
              </div>
            </div>
            );
          })}
        </div>

        <div style={{ padding: '20px', borderTop: '1px solid var(--border)', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <input 
            type="text" 
            placeholder="New column name" 
            value={newColName}
            onChange={(e) => setNewColName(e.target.value)}
            style={{ flex: 1, background: 'var(--bg)', border: '1px solid var(--border)', color: 'white', padding: '8px 12px', borderRadius: '6px' }}
          />
          <select 
            value={newColType}
            onChange={(e) => setNewColType(e.target.value)}
            style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'white', padding: '8px 12px', borderRadius: '6px' }}
          >
            <option value="text">Text</option>
            <option value="number">Number</option>
            <option value="boolean">Boolean</option>
            <option value="date">Date</option>
          </select>
          <button 
            onClick={() => { if (newColName) { onAdd(newColName, newColType); setNewColName(''); } }}
            style={{ background: 'var(--primary)', border: 'none', color: 'white', padding: '8px 16px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}
          >
            <FiPlus /> Add
          </button>
        </div>
      </div>
    </div>
  );
};
