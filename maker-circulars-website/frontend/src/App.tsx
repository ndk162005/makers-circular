import React, { useState, useEffect, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { apiService } from './services/api';
import { Header } from './components/Header';
import { StatsBar } from './components/StatsBar';
import { SearchBar } from './components/SearchBar';
import { MakerFilter } from './components/MakerFilter';
import { DataTable } from './components/DataTable';
import { Pagination } from './components/Pagination';
import { EmptyState } from './components/EmptyState';
import { ImportModal } from './components/ImportModal';
import { RecordModal } from './components/RecordModal';
import { DeleteConfirmModal } from './components/DeleteConfirmModal';
import { ColumnManager } from './components/ColumnManager';
import { Dataset, DataRecord, Maker, ColumnDef, Stats } from './types';
import { FiPlus, FiSettings } from 'react-icons/fi';

function App() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [currentDatasetId, setCurrentDatasetId] = useState<number | null>(null);
  
  const [records, setRecords] = useState<DataRecord[]>([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [columns, setColumns] = useState<ColumnDef[]>([]);
  const [makers, setMakers] = useState<Maker[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [search, setSearch] = useState('');
  const [selectedMaker, setSelectedMaker] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [onlyNew, setOnlyNew] = useState(false);

  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isColumnManagerOpen, setIsColumnManagerOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState<DataRecord | null>(null);
  const [deletingRecord, setDeletingRecord] = useState<DataRecord | null>(null);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const res = await apiService.getDatasets();
      setDatasets(res.data.items);
      if (res.data.items.length > 0 && !currentDatasetId) {
        setCurrentDatasetId(res.data.items[0].id);
      } else if (res.data.items.length === 0) {
        setLoading(false);
      }
    } catch (err) {
      toast.error('Failed to load datasets');
      setLoading(false);
    }
  };

  const fetchMetadata = async (datasetId: number) => {
    try {
      const [colRes, statsRes, makersRes] = await Promise.all([
        apiService.getColumns(datasetId),
        apiService.getStats(datasetId),
        apiService.getMakers(datasetId),
      ]);
      setColumns(colRes.data);
      setStats(statsRes.data);
      setMakers(makersRes.data);
    } catch (err) {
      console.error('Failed to load metadata', err);
    }
  };

  const fetchRecords = async () => {
    if (!currentDatasetId) return;
    setLoading(true);
    try {
      const recRes = await apiService.getRecords({
        dataset_id: currentDatasetId,
        page,
        page_size: pageSize,
        search,
        maker: selectedMaker,
        sort_by: sortBy,
        sort_order: sortOrder,
        only_new: onlyNew,
      });
      setRecords(recRes.data.items);
      setTotalRecords(recRes.data.total);
    } catch (err) {
      toast.error('Failed to load records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentDatasetId) {
      fetchMetadata(currentDatasetId);
    } else {
      setColumns([]);
      setMakers([]);
      setStats(null);
    }
  }, [currentDatasetId]);

  useEffect(() => {
    if (currentDatasetId) {
      fetchRecords();
    } else {
      setRecords([]);
      setTotalRecords(0);
      setLoading(false);
    }
  }, [currentDatasetId, page, pageSize, search, selectedMaker, sortBy, sortOrder, onlyNew]);

  const handleSearch = useCallback((val: string) => {
    setSearch(val);
    setPage(1);
  }, []);

  const handleSaveRecord = async (data: any) => {
    try {
      if (editingRecord?.id) {
        await apiService.updateRecord(editingRecord.id, data);
        toast.success('Record updated successfully');
      } else if (currentDatasetId) {
        await apiService.createRecord(currentDatasetId, data);
        toast.success('Record created successfully');
      }
      setEditingRecord(null);
      fetchRecords();
      if (currentDatasetId) fetchMetadata(currentDatasetId);
    } catch (err) {
      toast.error('Failed to save record');
    }
  };

  const handleDeleteRecord = async () => {
    if (!deletingRecord) return;
    try {
      await apiService.deleteRecord(deletingRecord.id);
      toast.success('Record deleted successfully');
      setDeletingRecord(null);
      fetchRecords();
      if (currentDatasetId) fetchMetadata(currentDatasetId);
    } catch (err) {
      toast.error('Failed to delete record');
    }
  };

  const handleDatasetChange = (id: number) => {
    setCurrentDatasetId(id);
    setPage(1);
    setSearch('');
    setSelectedMaker(null);
  };

  const handleAddRow = () => {
    const emptyData: any = {};
    columns.forEach(c => emptyData[c.name] = '');
    setEditingRecord({ id: 0, dataset_id: currentDatasetId!, data: emptyData, created_at: '', updated_at: '' });
  };

  const currentDataset = datasets.find(d => d.id === currentDatasetId) || null;

  return (
    <>
      <Toaster position="top-right" toastOptions={{
        style: { background: 'var(--surface-color)', color: 'var(--text-primary)', border: '1px solid var(--border)' }
      }} />
      
      <Header 
        datasets={datasets} 
        currentDataset={currentDataset} 
        onDatasetChange={handleDatasetChange} 
        onImportClick={() => setIsImportOpen(true)} 
      />

      {currentDatasetId ? (
        <>
          <StatsBar stats={stats} />
          
          <div style={{ display: 'flex', alignItems: 'center', margin: '0 16px 16px', gap: '16px' }}>
            <div style={{ flex: 1 }}>
              <SearchBar onSearch={handleSearch} activeFiltersCount={search || selectedMaker ? 1 : 0} />
            </div>
            <button 
              onClick={() => { setOnlyNew(prev => !prev); setPage(1); }}
              style={{ 
                background: onlyNew ? 'linear-gradient(135deg, #1d4ed8, #2563eb)' : 'var(--surface-elevated)', 
                border: onlyNew ? '1px solid #60a5fa' : '1px solid var(--border)', 
                color: onlyNew ? '#ffffff' : 'var(--text-primary)', 
                padding: '8px 16px', 
                borderRadius: '6px', 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                cursor: 'pointer',
                fontWeight: onlyNew ? 600 : 500,
                boxShadow: onlyNew ? '0 0 12px rgba(37, 99, 235, 0.4)' : 'none',
                transition: 'all 0.2s ease'
              }}
              title="Show only records newly added apart from the Excel data"
            >
              ★ Newly Added {stats?.newly_added_records ? `(${stats.newly_added_records})` : ''}
            </button>
            <button 
              onClick={() => setIsColumnManagerOpen(true)}
              style={{ background: 'var(--surface-elevated)', border: '1px solid var(--border)', color: 'var(--text-primary)', padding: '8px 16px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
            >
              <FiSettings /> Columns
            </button>
            <button 
              onClick={handleAddRow}
              style={{ background: 'var(--primary)', border: 'none', color: 'white', padding: '8px 16px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
            >
              <FiPlus /> Add Row
            </button>
          </div>

          <MakerFilter 
            makers={makers} 
            selectedMaker={selectedMaker} 
            onSelect={(m) => { setSelectedMaker(m); setPage(1); }} 
            totalRecords={stats?.total_records || 0} 
          />
          
          <DataTable 
            records={records} columns={columns} isLoading={loading} 
            onEdit={setEditingRecord} onDelete={setDeletingRecord}
            sortBy={sortBy} sortOrder={sortOrder}
            page={page} pageSize={pageSize}
            onSort={(col) => {
              if (sortBy === col) {
                setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
              } else {
                setSortBy(col);
                setSortOrder('asc');
              }
              setPage(1);
            }}
          />
          <Pagination 
            page={page} 
            totalPages={Math.max(1, Math.ceil(totalRecords / pageSize))} 
            pageSize={pageSize} 
            totalRecords={totalRecords}
            onPageChange={setPage} 
            onPageSizeChange={(newSize) => { 
              setPageSize(newSize); 
              setPage(1); 
            }}
          />
        </>
      ) : (
        !loading && <EmptyState onImportClick={() => setIsImportOpen(true)} />
      )}

      <ImportModal isOpen={isImportOpen} onClose={() => setIsImportOpen(false)} onSuccess={fetchDatasets} />
      
      {isColumnManagerOpen && (
        <ColumnManager 
          columns={columns} 
          onClose={() => setIsColumnManagerOpen(false)} 
          onAdd={async (name, type) => {
            await apiService.addColumn(currentDatasetId!, name, type);
            const colRes = await apiService.getColumns(currentDatasetId!);
            setColumns(colRes.data);
          }}
          onDelete={async (id) => {
            await apiService.deleteColumn(id);
            const colRes = await apiService.getColumns(currentDatasetId!);
            setColumns(colRes.data);
          }}
          onRename={async (id, newName) => {
            await apiService.renameColumn(id, newName);
            const colRes = await apiService.getColumns(currentDatasetId!);
            setColumns(colRes.data);
          }}
        />
      )}
      
      {editingRecord && <RecordModal record={editingRecord} columns={columns} onClose={() => setEditingRecord(null)} onSave={handleSaveRecord} />}
      {deletingRecord && <DeleteConfirmModal record={deletingRecord} onClose={() => setDeletingRecord(null)} onConfirm={handleDeleteRecord} />}
    </>
  );
}

export default App;
