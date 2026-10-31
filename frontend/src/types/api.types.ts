export type TriState = 'yes' | 'no' | 'unknown';
export type ItemStatus = 'available' | 'missing' | 'needs_verification';
export interface Answers {
  businessType: 'company' | 'household' | 'unknown';
  goal: 'dissolution' | 'other' | 'unknown';
  establishedYear: number | null;
  revenueStatus: TriState;
  revenueStartedYear: number | null;
  filingStatus: 'complete' | 'incomplete' | 'never' | 'unknown';
  recordsStatus: 'complete' | 'partial' | 'missing' | 'unknown';
  taxNoticeStatus: TriState;
  laborInsuranceStatus: 'none' | 'obligations' | 'unknown';
  assetsInventoryStatus: TriState;
  receivablesPayablesStatus: TriState;
}
export interface Questionnaire {
  id: string;
  version: string;
  contentStatus: 'draft' | 'approved';
  questions: {
    id: keyof Answers;
    label: string;
    kind: 'choice' | 'year';
    required: boolean;
    options: { value: string; label: string }[];
  }[];
}
export interface ChecklistItem {
  id: string;
  code: string;
  label: string;
  status: ItemStatus;
  reviewStatus: 'draft' | 'approved';
  note: string | null;
}
export interface Assessment {
  id: string;
  questionnaireVersion: string;
  contentStatus: 'draft' | 'approved';
  answers: Answers;
  summary: {
    scope: 'b2' | 'out_of_scope' | 'needs_confirmation';
    knownFacts: string[];
    unknownFacts: string[];
    reviewReasons: string[];
    notice: string;
  };
  checklist: ChecklistItem[];
  createdAt: string;
  updatedAt: string;
  expiresAt: string;
}

export interface AssessmentListItem {
  id: string;
  scope: Assessment['summary']['scope'];
  counts: { available: number; missing: number; needsVerification: number };
  createdAt: string;
  updatedAt: string;
  expiresAt: string;
  expired: boolean;
}
export interface AssessmentPage {
  items: AssessmentListItem[];
  page: number;
  pageSize: number;
  total: number;
}

export interface Citation {
  sourceId: string;
  title: string;
  url: string;
  reviewedAt: string | null;
  kind: 'product' | 'legal';
  fetchedAt?: string | null;
  reviewStatus?: 'reviewed' | 'unreviewed';
}
export interface ChatReply {
  reply: string;
  disposition: 'answered' | 'insufficient_sources' | 'expert_review' | 'blocked_input';
  citations: Citation[];
  providerUsed: boolean;
}
