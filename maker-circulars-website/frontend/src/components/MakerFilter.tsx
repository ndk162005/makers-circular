import React from 'react';
import { Maker } from '../types';

interface MakerFilterProps {
  makers: Maker[];
  selectedMaker: string | null;
  onSelect: (makerName: string | null) => void;
  totalRecords: number;
}

export const MakerFilter: React.FC<MakerFilterProps> = ({ makers, selectedMaker, onSelect, totalRecords }) => {
  return (
    <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', margin: '0 16px 24px', paddingBottom: '8px' }} className="maker-scroll">
      <button
        onClick={() => onSelect(null)}
        style={{
          background: selectedMaker === null ? 'var(--primary)' : 'var(--surface-elevated)',
          color: selectedMaker === null ? 'white' : 'var(--text-secondary)',
          border: '1px solid var(--border)',
          padding: '6px 16px', borderRadius: '20px', whiteSpace: 'nowrap',
          display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem'
        }}
      >
        All Makers
        <span style={{ background: 'rgba(255,255,255,0.2)', padding: '2px 6px', borderRadius: '10px', fontSize: '0.75rem' }}>
          {totalRecords}
        </span>
      </button>
      
      {makers.map((m, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(m.maker)}
          style={{
            background: selectedMaker === m.maker ? 'var(--primary)' : 'var(--surface-elevated)',
            color: selectedMaker === m.maker ? 'white' : 'var(--text-secondary)',
            border: '1px solid var(--border)',
            padding: '6px 16px', borderRadius: '20px', whiteSpace: 'nowrap',
            display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem'
          }}
        >
          {m.maker || 'Unknown'}
          <span style={{ background: 'rgba(255,255,255,0.2)', padding: '2px 6px', borderRadius: '10px', fontSize: '0.75rem' }}>
            {m.count}
          </span>
        </button>
      ))}
    </div>
  );
};
