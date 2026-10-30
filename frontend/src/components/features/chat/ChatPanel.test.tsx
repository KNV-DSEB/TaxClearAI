import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { chatService } from '@/services/chat.service';

import { ChatPanel } from './ChatPanel';

vi.mock('@/services/chat.service', () => ({ chatService: { send: vi.fn() } }));
beforeEach(() => vi.resetAllMocks());

function ask(): void {
  fireEvent.change(screen.getByLabelText('Câu hỏi của bạn'), {
    target: { value: 'Tôi dùng checklist thế nào?' },
  });
  fireEvent.click(screen.getByRole('checkbox'));
  fireEvent.click(screen.getByRole('button', { name: 'Gửi câu hỏi' }));
}

describe('Trợ lý có nguồn', () => {
  it.each([
    ['product', 'javascript:alert(1)', false],
    ['legal', 'https://example.gov.vn/van-ban', true],
    ['legal', 'http://example.gov.vn/van-ban', false],
    ['legal', 'javascript:alert(1)', false],
  ] as const)('kiểm tra đường dẫn nguồn %s %s trước khi mở', async (kind, url, allowed) => {
    vi.mocked(chatService.send).mockResolvedValue({
      reply: 'Nội dung giải thích.',
      disposition: 'answered',
      providerUsed: true,
      citations: [
        { sourceId: 'source-1', title: 'Nguồn thử đường dẫn', url, reviewedAt: '2026-10-30', kind },
      ],
    });
    render(<ChatPanel />);
    ask();
    await screen.findByText('Nội dung giải thích.');
    if (allowed)
      expect(screen.getByRole('link', { name: 'Nguồn thử đường dẫn' })).toHaveAttribute(
        'href',
        url,
      );
    else
      expect(screen.queryByRole('link', { name: 'Nguồn thử đường dẫn' })).not.toBeInTheDocument();
  });

  it('không gửi câu hỏi chỉ có khoảng trắng', () => {
    render(<ChatPanel />);
    fireEvent.click(screen.getByRole('checkbox'));
    fireEvent.submit(screen.getByRole('form', { name: 'Đặt câu hỏi' }));
    expect(chatService.send).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('Vui lòng nhập câu hỏi.');
  });

  it('dùng thông báo an toàn khi lỗi không có kiểu Error', async () => {
    vi.mocked(chatService.send).mockRejectedValue(null);
    render(<ChatPanel />);
    ask();
    expect(await screen.findByRole('alert')).toHaveTextContent('Chưa nhận được phản hồi.');
  });

  it('chỉ gửi câu hỏi, nhận Gemini thật và phân biệt nguồn hướng dẫn sử dụng', async () => {
    vi.mocked(chatService.send).mockResolvedValue({
      reply: 'Bạn chọn Đã có cho giấy tờ đang giữ.',
      disposition: 'answered',
      providerUsed: true,
      citations: [
        {
          sourceId: 'product-guide',
          title: 'Hướng dẫn sử dụng Tax Clear AI',
          url: '/huong-dan',
          reviewedAt: '2026-10-30',
          kind: 'product',
        },
      ],
    });
    render(<ChatPanel />);
    ask();
    expect(await screen.findByText('Bạn chọn Đã có cho giấy tờ đang giữ.')).toBeInTheDocument();
    expect(screen.getByText('Gemini · Có gọi mô hình')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Hướng dẫn sử dụng Tax Clear AI' })).toHaveAttribute(
      'href',
      '/huong-dan',
    );
    expect(screen.getByText('Hướng dẫn sử dụng')).toBeInTheDocument();
    expect(chatService.send).toHaveBeenCalledWith('Tôi dùng checklist thế nào?');
  });

  it('không gọi thông báo chặn là phản hồi Gemini', async () => {
    vi.mocked(chatService.send).mockResolvedValue({
      reply: 'Vui lòng bỏ thông tin riêng tư.',
      disposition: 'blocked_input',
      providerUsed: false,
      citations: [],
    });
    render(<ChatPanel />);
    ask();
    expect(await screen.findByText('Vui lòng bỏ thông tin riêng tư.')).toBeInTheDocument();
    expect(screen.getByText('Kiểm tra nội dung · Chưa gọi mô hình')).toBeInTheDocument();
  });

  it('giữ câu hỏi khi hết hạn mức để người dùng thử lại sau', async () => {
    vi.mocked(chatService.send).mockRejectedValue(new Error('Đã chạm hạn mức trợ lý.'));
    render(<ChatPanel />);
    ask();
    expect(await screen.findByRole('alert')).toHaveTextContent('Đã chạm hạn mức trợ lý.');
    expect(screen.getByLabelText('Câu hỏi của bạn')).toHaveValue('Tôi dùng checklist thế nào?');
    expect(screen.getByRole('button', { name: 'Gửi câu hỏi' })).toBeEnabled();
  });

  it('yêu cầu xác nhận giới hạn dữ liệu trước khi gửi', () => {
    render(<ChatPanel />);
    fireEvent.change(screen.getByLabelText('Câu hỏi của bạn'), {
      target: { value: 'Cách dùng checklist?' },
    });
    fireEvent.submit(screen.getByRole('form', { name: 'Đặt câu hỏi' }));
    expect(chatService.send).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('Vui lòng xác nhận');
  });

  it('hiển thị trả lời dưới dạng chữ, không thực thi HTML của mô hình', async () => {
    vi.mocked(chatService.send).mockResolvedValue({
      reply: '<script>alert(1)</script>',
      disposition: 'answered',
      providerUsed: true,
      citations: [],
    });
    const view = render(<ChatPanel />);
    ask();
    expect(await screen.findByText('<script>alert(1)</script>')).toBeInTheDocument();
    expect(view.container.querySelector('script')).toBeNull();
  });
});
