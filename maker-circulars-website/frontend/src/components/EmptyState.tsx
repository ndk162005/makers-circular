import React from 'react';
import { FiUploadCloud } from 'react-icons/fi';

interface EmptyStateProps {
  onImportClick: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onImportClick }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', textAlign: 'center' }}>
      <div style={{ background: 'var(--surface-elevated)', padding: '32px', borderRadius: '50%', marginBottom: '24px', border: '1px solid var(--border)' }}>
        <FiUploadCloud size={64} color="var(--primary)" />
      </div>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '8px', color: 'var(--text-primary)' }}>No datasets imported yet</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '400px' }}>
        Import your first Excel file to get started managing your Maker Circulars data.
      </p>
      <button 
        onClick={onImportClick}
        style={{ 
          background: 'var(--primary)', color: 'white', border: 'none',
          padding: '12px 24px', borderRadius: '8px', fontSize: '1rem', fontWeight: 500,
          display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)'
        }}
      >
        <FiUploadCloud size={20} />
        Import Excel File
      </button>
    </div>
  );
};
