import React, { useState } from 'react';
import { FiUploadCloud, FiX, FiFileText } from 'react-icons/fi';
import { apiService } from '../services/api';
import { ImportPreview } from '../types';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ImportModal: React.FC<ImportModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState<File | null>(null);
  
  // State for step 1 response
  const [uploadRes, setUploadRes] = useState<{file_id: string, sheet_names: string[], original_filename: string} | null>(null);
  
  // State for step 2 selection
  const [selectedSheet, setSelectedSheet] = useState<string>('');
  
  // State for step 3 preview
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setLoading(true);
      try {
        const res = await apiService.uploadFile(selected);
        setUploadRes(res.data);
        
        if (res.data.sheet_names && res.data.sheet_names.length > 0) {
          if (res.data.sheet_names.length === 1) {
            // Auto select if only 1 sheet
            handleSheetSelection(res.data.file_id, res.data.sheet_names[0]);
          } else {
            setStep(2);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSheetSelection = async (fileId: string, sheetName: string) => {
    setLoading(true);
    setSelectedSheet(sheetName);
    try {
      const res = await apiService.getPreview(fileId, sheetName);
      setPreview(res.data);
      setStep(3);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (mode: string) => {
    if (!preview) return;
    setLoading(true);
    try {
      await apiService.confirmImport(preview.file_id, selectedSheet, mode, preview.duplicate_warning?.existing_dataset_id);
      setStep(4); // Success
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setStep(1);
    setFile(null);
    setUploadRes(null);
    setSelectedSheet('');
    setPreview(null);
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto', padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Import Data</h2>
          <button onClick={() => { reset(); onClose(); }} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)' }}><FiX size={24} /></button>
        </div>

        {step === 1 && (
          <div style={{ border: '2px dashed var(--border)', borderRadius: '12px', padding: '40px', textAlign: 'center' }}>
            <FiUploadCloud size={48} color="var(--primary)" style={{ marginBottom: '16px' }} />
            <h3 style={{ marginBottom: '8px' }}>Upload Excel File</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Drag and drop your .xlsx file here, or click to browse.</p>
            <input type="file" id="file" accept=".xlsx" style={{ display: 'none' }} onChange={handleFileChange} />
            <label htmlFor="file" style={{ background: 'var(--primary)', color: 'white', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', display: 'inline-block' }}>
              {loading ? 'Uploading...' : 'Browse Files'}
            </label>
          </div>
        )}

        {step === 2 && uploadRes && (
          <div>
            <h3 style={{ marginBottom: '16px' }}>Select Sheet</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Multiple sheets found in {uploadRes.original_filename}. Please select one:</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {uploadRes.sheet_names.map((sheet, idx) => (
                <button 
                  key={idx}
                  onClick={() => handleSheetSelection(uploadRes.file_id, sheet)}
                  disabled={loading}
                  style={{
                    padding: '12px', background: 'var(--surface-elevated)', border: '1px solid var(--border)',
                    borderRadius: '8px', textAlign: 'left', color: 'var(--text-primary)'
                  }}
                >
                  {sheet}
                </button>
              ))}
            </div>
            {loading && <div style={{ marginTop: '16px', color: 'var(--text-secondary)' }}>Loading preview...</div>}
          </div>
        )}

        {step === 3 && preview && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px', background: 'var(--surface-elevated)', padding: '16px', borderRadius: '8px' }}>
              <FiFileText size={24} color="var(--accent)" />
              <div>
                <div style={{ fontWeight: 500 }}>{preview.filename} ({selectedSheet})</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{preview.row_count} rows • {preview.columns.length} columns</div>
              </div>
            </div>

            <div style={{ marginBottom: '24px', overflowX: 'auto', background: 'var(--surface-elevated)', borderRadius: '8px', border: '1px solid var(--border)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', whiteSpace: 'nowrap' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)' }}>
                    {preview.columns.map((col, idx) => (
                      <th key={idx} style={{ padding: '10px 16px', fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.preview_data.map((row, rowIdx) => (
                    <tr key={rowIdx} style={{ borderBottom: rowIdx === preview.preview_data.length - 1 ? 'none' : '1px solid var(--border)' }}>
                      {preview.columns.map((col, colIdx) => (
                        <td key={colIdx} style={{ padding: '10px 16px', fontSize: '0.875rem' }}>{String(row[col] ?? '')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {preview.duplicate_warning ? (
              <div style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)', padding: '16px', borderRadius: '8px', marginBottom: '24px' }}>
                <strong>Warning:</strong> A dataset with the filename "{preview.duplicate_warning.existing_filename}" already exists.
                <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                  <button onClick={() => handleConfirm('replace')} disabled={loading} style={{ background: 'var(--warning)', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '6px', flex: 1 }}>Replace Existing</button>
                  <button onClick={() => handleConfirm('new')} disabled={loading} style={{ background: 'transparent', border: '1px solid var(--warning)', color: 'var(--warning)', padding: '8px 16px', borderRadius: '6px', flex: 1 }}>Import as New</button>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button onClick={() => { reset(); onClose(); }} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)', padding: '10px 20px', borderRadius: '6px' }}>Cancel</button>
                <button onClick={() => handleConfirm('new')} disabled={loading} style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px' }}>
                  {loading ? 'Importing...' : 'Confirm Import'}
                </button>
              </div>
            )}
          </div>
        )}

        {step === 4 && (
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <FiUploadCloud size={32} />
            </div>
            <h3 style={{ marginBottom: '8px' }}>Import Successful!</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Your dataset has been imported and processed successfully.</p>
            <button onClick={() => { onSuccess(); onClose(); reset(); }} style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px' }}>
              View Dataset
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
