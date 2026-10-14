import React, { useState } from 'react';
import { DataRecord, ColumnDef } from '../types';
import { FiX } from 'react-icons/fi';

interface RecordModalProps {
  record: DataRecord | null;
  columns: ColumnDef[];
  onClose: () => void;
  onSave: (data: any) => void;
}

export const RecordModal: React.FC<RecordModalProps> = ({ record, columns, onClose, onSave }) => {
  const [formData, setFormData] = useState<any>(record?.data || {});
  
  if (!record) return null;

  const handleChange = (colName: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [colName]: value }));
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '600px', maxHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '20px', borderBottom: '1px solid var(--border)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{record.id ? 'Edit Record' : 'Add Record'}</h2>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)' }}><FiX size={24} /></button>
        </div>
        
        <div style={{ padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {columns.filter(c => c.is_active && !['_id', 'id', 'dms'].includes(c.name.toLowerCase())).map(col => {
            const displayName = col.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            return (
            <div key={col.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{displayName}</label>
              <input 
                type={col.data_type === 'number' ? 'number' : 'text'}
                value={formData[col.name] || ''}
                onChange={(e) => handleChange(col.name, e.target.value)}
                style={{ 
                  background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-primary)',
                  padding: '10px', borderRadius: '6px', outline: 'none'
                }}
              />
            </div>
            );
          })}
        </div>

        <div style={{ padding: '20px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button onClick={onClose} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)', padding: '8px 16px', borderRadius: '6px' }}>Cancel</button>
          <button onClick={() => onSave(formData)} style={{ background: 'var(--primary)', border: 'none', color: 'white', padding: '8px 16px', borderRadius: '6px' }}>Save Changes</button>
        </div>
      </div>
    </div>
  );
};
