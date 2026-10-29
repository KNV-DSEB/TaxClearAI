import type { ChatReply } from '@/types/api.types';

import { apiData } from './api.client';

export const chatService = {
  async send(message: string): Promise<ChatReply> {
    return apiData<ChatReply>('/api/v1/chat/messages', {
      method: 'POST',
      body: JSON.stringify({ message, disclosureAccepted: true }),
    });
  },
};
