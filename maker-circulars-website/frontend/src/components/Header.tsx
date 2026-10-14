import React from 'react';
import { FiDatabase, FiUploadCloud } from 'react-icons/fi';
import { Dataset } from '../types';

interface HeaderProps {
  datasets: Dataset[];
  currentDataset: Dataset | null;
  onDatasetChange: (datasetId: number) => void;
  onImportClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ datasets, currentDataset, onDatasetChange, onImportClick }) => {
  return (
    <header className="glass" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', margin: '16px', zIndex: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ background: 'var(--primary)', padding: '8px', borderRadius: '8px', display: 'flex' }}>
          <FiDatabase size={24} color="white" />
        </div>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>Maker Circulars</h1>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {datasets.length > 0 && (
          <select 
            value={currentDataset?.id || ''} 
            onChange={(e) => onDatasetChange(Number(e.target.value))}
            style={{ 
              background: 'var(--surface-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border)',
              padding: '8px 12px', borderRadius: '6px', outline: 'none'
            }}
          >
            {datasets.map(d => (
              <option key={d.id} value={d.id}>{d.filename} ({d.worksheet_name})</option>
            ))}
          </select>
        )}
        
        <button 
          onClick={onImportClick}
          style={{ 
            display: 'flex', alignItems: 'center', gap: '8px',
            background: 'var(--primary)', color: 'white', border: 'none',
            padding: '8px 16px', borderRadius: '6px', fontWeight: 500,
          }}
        >
          <FiUploadCloud size={18} />
          Import Excel
        </button>
      </div>
    </header>
  );
};
