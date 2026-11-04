export interface Expert {
  id: string;
  fullName: string;
  title: string;
  organization: string;
  avatarUrl: string | null;
  bio: string;
  specializations: string[];
  partnerType: 'accounting_firm' | 'accountant' | 'tax_consultant';
  servicesOffered: string[];
  location: string;
  experienceYears: number;
  consultationFeeText: string;
  isVerified: boolean;
}

export interface RecommendedExpert {
  expert: Expert;
  match_reason: string;
}

export interface ConsultationFormValues {
  expertId: string;
  assessmentId?: string;
  contactName: string;
  contactPhone: string;
  contactEmail?: string;
  businessType?: string;
  serviceNeeded?: string;
  shareDataConsent: boolean;
  consultationMethod: 'online' | 'in_person';
  notes: string;
}

export interface ConsultationResponse {
  id: string;
  expertId: string;
  status: string;
  createdAt: string;
}

export interface ExpertQuery {
  q?: string;
  specialization?: string;
  location?: string;
  partnerType?: Expert['partnerType'] | '';
}
