import React from 'react';
import { DataRecord } from '../types';
import { FiAlertTriangle } from 'react-icons/fi';

interface DeleteConfirmModalProps {
  record: DataRecord | null;
  onClose: () => void;
  onConfirm: () => void;
}

export const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({ record, onClose, onConfirm }) => {
  if (!record) return null;

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '400px', padding: '24px', textAlign: 'center' }}>
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
          <FiAlertTriangle size={32} />
        </div>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '12px' }}>Delete Record?</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '0.95rem' }}>
          Are you sure you want to permanently delete this record? This action cannot be undone.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
          <button onClick={onClose} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)', padding: '10px 20px', borderRadius: '6px', flex: 1 }}>Cancel</button>
          <button onClick={onConfirm} style={{ background: 'var(--danger)', border: 'none', color: 'white', padding: '10px 20px', borderRadius: '6px', flex: 1 }}>Delete</button>
        </div>
      </div>
    </div>
  );
};
