export interface CommunityTopic {
  id: string;
  slug: string;
  name: string;
  orderIndex: number;
}

export interface CommunityQuestion {
  id: string;
  topic: CommunityTopic;
  authorName: string;
  title: string;
  questionContent: string;
  answerContent: string | null;
  answeredBy: string | null;
  answeredAt: string | null;
  createdAt: string;
}

export interface CommunityQuestionPage {
  items: CommunityQuestion[];
  page: number;
  pageSize: number;
  total: number;
}

export interface CreateCommunityQuestion {
  topicSlug: string;
  authorName?: string;
  title: string;
  questionContent: string;
}

export interface CommunityQuestionQuery {
  q?: string;
  topic?: string;
  page?: number;
  pageSize?: number;
}
