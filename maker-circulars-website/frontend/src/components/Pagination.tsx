import React from 'react';
import { FiChevronLeft, FiChevronRight, FiChevronsLeft, FiChevronsRight } from 'react-icons/fi';

interface PaginationProps {
  page: number;
  totalPages: number;
  pageSize: number;
  totalRecords: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ page, totalPages, pageSize, totalRecords, onPageChange, onPageSizeChange }) => {
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, totalRecords);

  const getPageNumbers = () => {
    if (totalPages <= 1) return [1];
    const pages: (number | string)[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      let startPage = Math.max(2, page - 1);
      let endPage = Math.min(totalPages - 1, page + 1);

      if (page <= 3) {
        startPage = 2;
        endPage = 4;
      } else if (page >= totalPages - 2) {
        startPage = totalPages - 3;
        endPage = totalPages - 1;
      }

      if (startPage > 2) pages.push('...');
      for (let i = startPage; i <= endPage; i++) pages.push(i);
      if (endPage < totalPages - 1) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '16px', padding: '0 8px', color: 'var(--text-secondary)', fontSize: '0.875rem', flexWrap: 'wrap', gap: '12px' }}>
      <div>
        Showing {totalRecords === 0 ? 0 : start}-{end} of {totalRecords} records
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        <select 
          value={pageSize} 
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          style={{ background: 'var(--surface-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: '4px', padding: '6px 10px', cursor: 'pointer' }}
        >
          <option value="25">25 per page</option>
          <option value="50">50 per page</option>
          <option value="100">100 per page</option>
        </select>

        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <button 
            onClick={() => onPageChange(1)} 
            disabled={page <= 1} 
            style={{ ...btnStyle, cursor: page <= 1 ? 'not-allowed' : 'pointer', opacity: page <= 1 ? 0.35 : 1 }}
            title="First page"
          >
            <FiChevronsLeft />
          </button>
          <button 
            onClick={() => onPageChange(page - 1)} 
            disabled={page <= 1} 
            style={{ ...btnStyle, cursor: page <= 1 ? 'not-allowed' : 'pointer', opacity: page <= 1 ? 0.35 : 1 }}
            title="Previous page"
          >
            <FiChevronLeft />
          </button>
          
          {getPageNumbers().map((p, i) => typeof p === 'number' ? (
            <button
              key={i}
              onClick={() => onPageChange(p)}
              style={{
                ...btnStyle,
                cursor: 'pointer',
                minWidth: '32px',
                padding: '6px 8px',
                background: p === page ? 'var(--primary)' : 'var(--surface-elevated)',
                color: p === page ? 'white' : 'var(--text-primary)',
                fontWeight: p === page ? 600 : 400,
                border: p === page ? '1px solid var(--primary)' : '1px solid var(--border)'
              }}
            >
              {p}
            </button>
          ) : (
            <span key={i} style={{ padding: '0 4px', color: 'var(--text-secondary)' }}>...</span>
          ))}

          <button 
            onClick={() => onPageChange(page + 1)} 
            disabled={page >= totalPages || totalPages === 0} 
            style={{ ...btnStyle, cursor: (page >= totalPages || totalPages === 0) ? 'not-allowed' : 'pointer', opacity: (page >= totalPages || totalPages === 0) ? 0.35 : 1 }}
            title="Next page"
          >
            <FiChevronRight />
          </button>
          <button 
            onClick={() => onPageChange(totalPages)} 
            disabled={page >= totalPages || totalPages === 0} 
            style={{ ...btnStyle, cursor: (page >= totalPages || totalPages === 0) ? 'not-allowed' : 'pointer', opacity: (page >= totalPages || totalPages === 0) ? 0.35 : 1 }}
            title="Last page"
          >
            <FiChevronsRight />
          </button>
        </div>
      </div>
    </div>
  );
};

const btnStyle: React.CSSProperties = {
  background: 'var(--surface-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: '4px',
  padding: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center'
};
