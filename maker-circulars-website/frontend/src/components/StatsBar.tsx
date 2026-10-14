import React from 'react';
import { FiFileText, FiUsers, FiLink, FiPlusCircle } from 'react-icons/fi';
import { Stats } from '../types';

interface StatsBarProps {
  stats: Stats | null;
}

export const StatsBar: React.FC<StatsBarProps> = ({ stats }) => {
  if (!stats) return null;

  const statItems = [
    { label: 'Total Records', value: stats.total_records, icon: FiFileText, color: 'var(--primary)' },
    { label: 'Total Makers', value: stats.total_makers, icon: FiUsers, color: 'var(--accent)' },
    { label: 'Docs With Links', value: stats.docs_with_links, icon: FiLink, color: 'var(--success)' },
    { label: 'Newly Added', value: stats.newly_added_records, icon: FiPlusCircle, color: '#f59e0b' },
  ];

  return (
    <div className="animate-slide-up" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', margin: '0 16px 24px' }}>
      {statItems.map((item, index) => (
        <div key={index} className="glass" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: `${item.color}20`, padding: '12px', borderRadius: '10px', color: item.color, display: 'flex' }}>
            <item.icon size={24} />
          </div>
          <div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '4px' }}>{item.label}</div>
            <div style={{ color: 'var(--text-primary)', fontSize: '1.5rem', fontWeight: 600 }}>{item.value.toLocaleString()}</div>
          </div>
        </div>
      ))}
    </div>
  );
};
