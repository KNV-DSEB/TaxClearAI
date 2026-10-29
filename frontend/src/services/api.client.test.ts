import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { Answers } from '@/types/api.types';

import { ApiError, apiData } from './api.client';
import { assessmentsService } from './assessments.service';
import { authService } from './auth.service';

const transport = vi.fn<typeof fetch>();
const answers: Answers = {
  businessType: 'company',
  goal: 'dissolution',
  establishedYear: null,
  revenueStatus: 'yes',
  revenueStartedYear: null,
  filingStatus: 'unknown',
  recordsStatus: 'unknown',
  taxNoticeStatus: 'unknown',
  laborInsuranceStatus: 'unknown',
  assetsInventoryStatus: 'unknown',
  receivablesPayablesStatus: 'unknown',
};

beforeEach(() => {
  transport.mockReset();
  vi.stubGlobal('fetch', transport);
});
afterEach(() => vi.unstubAllGlobals());

function success(data: unknown): Response {
  return Response.json({ data });
}

describe('Ranh giới API và phiên đăng nhập', () => {
  it('gửi cookie phiên và mở dữ liệu khảo sát từ response envelope', async () => {
    transport.mockResolvedValue(success({ id: 'b2', version: 'draft', questions: [] }));
    const result = await assessmentsService.questionnaire();
    expect(result.id).toBe('b2');
    expect(transport).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/questionnaires/b2'),
      expect.objectContaining({ credentials: 'include' }),
    );
  });

  it('gửi đúng dữ liệu tạo hồ sơ và cập nhật trạng thái được server xác nhận', async () => {
    transport
      .mockResolvedValueOnce(success({ id: 'case-1' }))
      .mockResolvedValueOnce(success({ id: 'item-1', status: 'available' }))
      .mockResolvedValueOnce(success({ id: 'case-1', checklist: [] }));
    expect((await assessmentsService.create('draft', answers)).id).toBe('case-1');
    expect(transport.mock.calls[0][1]?.body).toBe(
      JSON.stringify({ questionnaireVersion: 'draft', answers }),
    );
    expect((await assessmentsService.updateItem('case-1', 'item-1', 'available')).status).toBe(
      'available',
    );
    expect((await assessmentsService.get('case-1')).checklist).toEqual([]);
  });

  it('xử lý xóa hồ sơ và đăng xuất 204 mà không cố đọc JSON rỗng', async () => {
    transport.mockImplementation(async () => new Response(null, { status: 204 }));
    await expect(assessmentsService.remove('case-1')).resolves.toBeUndefined();
    await expect(authService.logout()).resolves.toBeUndefined();
  });

  it('thử refresh đúng một lần rồi tiếp tục yêu cầu khi access token hết hạn', async () => {
    transport
      .mockResolvedValueOnce(Response.json({ detail: 'Hết phiên' }, { status: 401 }))
      .mockResolvedValueOnce(success({ expiresAt: '' }))
      .mockResolvedValueOnce(success({ id: 'case-1' }));
    expect((await assessmentsService.get('case-1')).id).toBe('case-1');
    expect(transport).toHaveBeenCalledTimes(3);
    expect(String(transport.mock.calls[1][0])).toContain('/auth/refreshes');
  });

  it('chia sẻ một lần refresh cho các yêu cầu đồng thời', async () => {
    const attempts = new Map<string, number>();
    transport.mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/auth/refreshes')) return success({ expiresAt: '' });
      const attempt = (attempts.get(url) ?? 0) + 1;
      attempts.set(url, attempt);
      return attempt === 1 ? Response.json({ detail: 'Hết phiên' }, { status: 401 }) : success(url);
    });
    await Promise.all([apiData('/api/v1/one'), apiData('/api/v1/two')]);
    expect(
      transport.mock.calls.filter(([url]) => String(url).includes('/auth/refreshes')),
    ).toHaveLength(1);
  });

  it('không lặp refresh khi refresh token không còn hợp lệ', async () => {
    transport.mockResolvedValue(
      Response.json({ detail: 'Vui lòng đăng nhập lại.' }, { status: 401 }),
    );
    await expect(assessmentsService.get('case-1')).rejects.toMatchObject({ status: 401 });
    expect(transport).toHaveBeenCalledTimes(2);
  });

  it('không tự refresh sau đăng nhập sai', async () => {
    transport.mockResolvedValue(Response.json({ detail: 'Thông tin chưa đúng.' }, { status: 401 }));
    await expect(authService.login('demo', crypto.randomUUID())).rejects.toThrow(
      'Thông tin chưa đúng.',
    );
    expect(transport).toHaveBeenCalledTimes(1);
  });

  it('trả phiên đăng nhập đã được server xác nhận', async () => {
    transport.mockResolvedValue(success({ user: { id: 'u1', username: 'demo' }, expiresAt: '' }));
    expect((await authService.login('demo', crypto.randomUUID())).user.id).toBe('u1');
  });

  it('phân biệt mất mạng với yêu cầu đã chủ động hủy', async () => {
    transport.mockRejectedValue(new TypeError('network'));
    await expect(assessmentsService.get('case-1')).rejects.toMatchObject({ status: 0 });
    const controller = new AbortController();
    controller.abort();
    await expect(assessmentsService.get('case-1', controller.signal)).rejects.toBeInstanceOf(
      TypeError,
    );
  });

  it('không hiển thị HTML lỗi từ server trung gian', async () => {
    transport.mockResolvedValue(
      new Response('<html>internal upstream error</html>', { status: 503 }),
    );
    await expect(assessmentsService.get('case-1')).rejects.toBeInstanceOf(ApiError);
    await expect(assessmentsService.get('case-1')).rejects.not.toThrow('internal upstream');
  });

  it('không biến lỗi mạng trong refresh thành đăng nhập thành công', async () => {
    transport
      .mockResolvedValueOnce(Response.json({ detail: 'Hết phiên' }, { status: 401 }))
      .mockRejectedValueOnce(new TypeError('network'));
    await expect(assessmentsService.get('case-1')).rejects.toMatchObject({ status: 401 });
  });
});
