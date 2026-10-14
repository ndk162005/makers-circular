import axios from 'axios';
import { Dataset, DataRecord, Maker, ColumnDef, ImportPreview, UploadResponse, Stats, PaginatedResponse, DatasetListResponse } from '../types';

const api = axios.create({
  baseURL: '/api'
});

export const apiService = {
  // Import endpoints
  uploadFile: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<UploadResponse>('/import/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getPreview: (fileId: string, sheetName?: string) =>
    api.post<ImportPreview>('/import/preview', { file_id: fileId, sheet_name: sheetName }),
  confirmImport: (fileId: string, sheetName: string, importMode: string, existingDatasetId?: number) =>
    api.post('/import/confirm', {
      file_id: fileId,
      sheet_name: sheetName,
      import_mode: importMode,
      existing_dataset_id: existingDatasetId
    }),

  // Dataset endpoints
  getDatasets: () => api.get<DatasetListResponse>('/datasets'),
  getDataset: (id: number) => api.get<Dataset>(`/datasets/${id}`),
  deleteDataset: (id: number) => api.delete(`/datasets/${id}`),

  // Record endpoints
  getRecords: (params: {
    dataset_id: number;
    page?: number;
    page_size?: number;
    search?: string;
    maker?: string | null;
    sort_by?: string;
    sort_order?: string;
    only_new?: boolean;
  }) => {
    const cleanParams: any = { ...params };
    if (!cleanParams.search) delete cleanParams.search;
    if (!cleanParams.maker) delete cleanParams.maker;
    if (!cleanParams.sort_by) delete cleanParams.sort_by;
    if (!cleanParams.only_new) delete cleanParams.only_new;
    return api.get<PaginatedResponse>('/records', { params: cleanParams });
  },
  getRecord: (id: number) => api.get<DataRecord>(`/records/${id}`),
  createRecord: (datasetId: number, data: object) =>
    api.post<DataRecord>('/records', { dataset_id: datasetId, data }),
  updateRecord: (id: number, data: object) =>
    api.put<DataRecord>(`/records/${id}`, { data }),
  deleteRecord: (id: number) => api.delete(`/records/${id}`),

  // Maker endpoints
  getMakers: (datasetId: number) =>
    api.get<Maker[]>('/makers', { params: { dataset_id: datasetId } }),

  // Column endpoints
  getColumns: (datasetId: number) =>
    api.get<ColumnDef[]>('/columns', { params: { dataset_id: datasetId } }),
  addColumn: (datasetId: number, name: string, dataType: string) =>
    api.post<ColumnDef>('/columns', { dataset_id: datasetId, name, data_type: dataType }),
  renameColumn: (columnId: number, newName: string) =>
    api.put<ColumnDef>(`/columns/${columnId}`, { name: newName }),
  deleteColumn: (columnId: number) => api.delete(`/columns/${columnId}`),

  // Stats endpoint
  getStats: (datasetId: number) =>
    api.get<Stats>('/stats', { params: { dataset_id: datasetId } })
};
