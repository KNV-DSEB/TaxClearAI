export type TriState = 'yes' | 'no' | 'unknown';
export type ItemStatus = 'available' | 'missing' | 'needs_verification';
// Backend là nguồn duy nhất của danh sách câu hỏi; câu trả lời là bản đồ id → giá trị
export type Answers = Record<string, string | number | null>;
export interface Question {
  id: string;
  label: string;
  kind: 'choice' | 'year' | 'text' | 'number';
  required: boolean;
  options: { value: string; label: string }[];
  help?: string | null;
  unit?: string | null;
  // Chỉ hỏi khi mọi câu trả lời trước đó nằm trong danh sách cho phép; thiếu = luôn hỏi
  showIf?: Record<string, string[]> | null;
}
export interface Questionnaire {
  id: string;
  version: string;
  contentStatus: 'draft' | 'approved';
  questions: Question[];
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
    scope: 'a1' | 'a2' | 'a3' | 'b1' | 'b2' | 'household' | 'out_of_scope' | 'needs_confirmation';
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

export type CaseStatus = 'in_progress' | 'ready' | 'expired';
export type CaseFilter = 'all' | 'in_progress' | 'ready';
export interface StatusCounts {
  all: number;
  inProgress: number;
  ready: number;
}
export interface AssessmentListItem {
  id: string;
  scope: Assessment['summary']['scope'];
  status: CaseStatus;
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
  statusCounts: StatusCounts;
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
