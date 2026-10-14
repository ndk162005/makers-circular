export interface Dataset {
  id: number;
  filename: string;
  worksheet_name: string;
  uploaded_at: string;
  row_count: number;
  column_count: number;
  column_names: string[];
  status: string;
}

export interface DataRecord {
  id: number;
  dataset_id: number;
  data: { [key: string]: any };
  created_at: string;
  updated_at: string;
}

export interface Maker {
  maker: string;
  count: number;
}

export interface ColumnDef {
  id: number;
  dataset_id: number;
  name: string;
  data_type: string;
  position: number;
  is_active: boolean;
}

export interface UploadResponse {
  file_id: string;
  sheet_names: string[];
  original_filename: string;
}

export interface ImportPreview {
  file_id: string;
  filename: string;
  sheet_names: string[];
  columns: string[];
  row_count: number;
  preview_data: { [key: string]: any }[];
  duplicate_warning?: {
    existing_dataset_id: number;
    existing_filename: string;
  } | null;
}

export interface Stats {
  total_records: number;
  total_makers: number;
  docs_with_links: number;
  records_with_dms?: number;
  newly_added_records: number;
}

export interface PaginatedResponse {
  items: DataRecord[];
  total: number;
  page: number;
  page_size: number;
}

export interface DatasetListResponse {
  items: Dataset[];
  total: number;
}
