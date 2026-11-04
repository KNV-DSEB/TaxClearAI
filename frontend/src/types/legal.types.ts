export type LegalCategory =
  | 'household'
  | 'company_dissolution'
  | 'tax_closure'
  | 'guidance';

export interface LegalSource {
  label: string;
  url: string;
  sourceType: 'official' | 'reference';
}

export interface LegalStep {
  title: string;
  description: string;
  authority: string | null;
  timing: string | null;
}

export interface LegalDocument {
  slug: string;
  categories: LegalCategory[];
  documentType: string;
  documentNumber: string;
  documentTitle: string;
  authority: string;
  summary: string;
  appliesTo: string[];
  overview: string;
  legalBasis: string[];
  processSteps: LegalStep[];
  checklist: string[];
  timeline: string;
  notes: string[];
  sources: LegalSource[];
}

export interface LegalDocumentList {
  items: LegalDocument[];
  total: number;
}
