import React, { useState, useEffect } from 'react';
import { FiSearch, FiX } from 'react-icons/fi';

interface SearchBarProps {
  onSearch: (query: string) => void;
  activeFiltersCount?: number;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, activeFiltersCount = 0 }) => {
  const [value, setValue] = useState('');
  const onSearchRef = React.useRef(onSearch);
  const prevValueRef = React.useRef(value);
  const isFirstRender = React.useRef(true);

  React.useEffect(() => {
    onSearchRef.current = onSearch;
  }, [onSearch]);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (prevValueRef.current === value) {
      return;
    }
    prevValueRef.current = value;

    const timeout = setTimeout(() => {
      onSearchRef.current(value);
    }, 300);
    return () => clearTimeout(timeout);
  }, [value]);


  return (
    <div className="glass" style={{ display: 'flex', alignItems: 'center', padding: '8px 16px', margin: '0 16px 16px', gap: '8px' }}>
      <FiSearch color="var(--text-secondary)" />
      <input 
        type="text" 
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search across all fields..."
        style={{
          flex: 1, background: 'transparent', border: 'none', color: 'var(--text-primary)',
          outline: 'none', fontSize: '0.95rem'
        }}
      />
      {value && (
        <button 
          onClick={() => {
            setValue('');
            prevValueRef.current = '';
            onSearchRef.current('');
          }} 
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', display: 'flex', cursor: 'pointer' }}
        >
          <FiX size={18} />
        </button>
      )}

      {activeFiltersCount > 0 && (
        <div style={{ background: 'var(--primary)', color: 'white', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
          {activeFiltersCount} active filter{activeFiltersCount !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};
