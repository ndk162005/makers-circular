import React from 'react';
import { DataRecord, ColumnDef } from '../types';
import { FiEdit2, FiTrash2, FiExternalLink } from 'react-icons/fi';

interface DataTableProps {
  records: DataRecord[];
  columns: ColumnDef[];
  isLoading: boolean;
  onEdit: (record: DataRecord) => void;
  onDelete: (record: DataRecord) => void;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  onSort: (columnName: string) => void;
  page?: number;
  pageSize?: number;
}

export const DataTable: React.FC<DataTableProps> = ({ records, columns, isLoading, onEdit, onDelete, sortBy, sortOrder, onSort, page = 1, pageSize = 25 }) => {
  if (isLoading && records.length === 0) {
    return (
      <div className="glass" style={{ margin: '0 16px', padding: '20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading data...
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className="glass" style={{ margin: '0 16px', padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        No records found.
      </div>
    );
  }

  const activeColumns = columns
    .filter(c => c.is_active && !['_id', 'id', 'dms'].includes(c.name.toLowerCase()))
    .sort((a, b) => a.position - b.position);

  return (
    <div className="glass" style={{ margin: '0 16px', overflowX: 'auto', position: 'relative' }}>
      {isLoading && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: 'var(--primary)', opacity: 0.8, animation: 'pulse 1s infinite' }} />
      )}
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', whiteSpace: 'nowrap' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface-elevated)' }}>
            <th style={{ padding: '12px 16px', width: '60px', fontWeight: 600, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>#</th>
            {activeColumns.map(col => {
              const displayName = col.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
              return (
              <th 
                key={col.id} 
                onClick={() => onSort(col.name)}
                style={{ padding: '12px 16px', fontWeight: 500, color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.875rem' }}
              >
                {displayName}
                {sortBy === col.name && (
                  <span style={{ marginLeft: '4px' }}>{sortOrder === 'asc' ? '▲' : '▼'}</span>
                )}
              </th>
            )})}
            <th style={{ padding: '12px 16px', width: '80px', textAlign: 'center' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {records.map((row, idx) => {
            const isNew = Boolean(row.data.is_new);
            return (
            <tr 
              key={row.id} 
              style={{ 
                borderBottom: '1px solid var(--border)', 
                background: isNew ? 'rgba(59, 130, 246, 0.08)' : (idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)'),
                borderLeft: isNew ? '4px solid #3b82f6' : '4px solid transparent',
                transition: 'background 0.2s ease'
              }}
            >
              <td style={{ padding: '12px 16px', fontSize: '0.85rem', color: isNew ? '#60a5fa' : 'var(--text-secondary)', fontWeight: 600 }}>
                {(page - 1) * pageSize + idx + 1}
              </td>
              {activeColumns.map(col => {
                const val = row.data[col.name];
                return (
                  <td key={col.id} style={{ padding: '12px 16px', fontSize: '0.875rem' }}>
                    {col.name.toLowerCase().includes('link') || col.name.toLowerCase().includes('url') ? (
                      (typeof val === 'string' && (val.startsWith('https://') || val.startsWith('http://'))) ? (
                        <a href={val} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          Open Document <FiExternalLink size={14} />
                        </a>
                      ) : (
                        <span style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>No valid link</span>
                      )
                    ) : col.name === 'document_name' ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                        <span>{String(val ?? '')}</span>
                        {isNew && (
                          <span 
                            title="Newly added from live Everllence service letters"
                            style={{ 
                              display: 'inline-flex', 
                              alignItems: 'center', 
                              gap: '3px',
                              background: 'linear-gradient(135deg, #2563eb, #3b82f6)',
                              color: '#ffffff',
                              padding: '2px 8px',
                              borderRadius: '10px',
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              letterSpacing: '0.4px',
                              boxShadow: '0 2px 6px rgba(37, 99, 235, 0.35)',
                              flexShrink: 0
                            }}
                          >
                            ★ NEW
                          </span>
                        )}
                      </span>
                    ) : (
                      String(val ?? '')
                    )}
                  </td>
                );
              })}
              <td style={{ padding: '12px 16px', display: 'flex', gap: '8px', justifyContent: 'center' }}>
                <button onClick={() => onEdit(row)} style={{ background: 'transparent', border: 'none', color: 'var(--accent)' }}><FiEdit2 /></button>
                <button onClick={() => onDelete(row)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)' }}><FiTrash2 /></button>
              </td>
            </tr>
          );})}
        </tbody>
      </table>
    </div>
  );
};
