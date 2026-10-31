import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError } from '@/services/api.client';
import { chatService } from '@/services/chat.service';

import { ChatWorkspace, formatReply } from './ChatWorkspace';

vi.mock('@/services/chat.service', () => ({ chatService: { send: vi.fn() } }));
const navigation = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation }));
beforeEach(() => vi.resetAllMocks());

function ask(): void {
  fireEvent.change(screen.getByLabelText('Câu hỏi của bạn'), {
    target: { value: 'Tôi dùng checklist thế nào?' },
  });
  fireEvent.click(screen.getByRole('checkbox'));
  fireEvent.click(screen.getByRole('button', { name: 'Gửi câu hỏi' }));
}

describe('Trợ lý có nguồn', () => {
  it('chọn chủ đề gợi ý điền sẵn câu hỏi, chưa gửi khi chưa xác nhận', () => {
    render(<ChatWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: /Hồ sơ cần chuẩn bị/ }));
    expect(screen.getByLabelText('Câu hỏi của bạn')).toHaveValue(
      'Hồ sơ giải thể doanh nghiệp gồm những giấy tờ gì?',
    );
    expect(chatService.send).not.toHaveBeenCalled();
  });

  it('giữ các lượt hỏi trước trong phiên và chuyển đăng nhập khi hết phiên', async () => {
    vi.mocked(chatService.send).mockResolvedValueOnce({
      reply: 'Trả lời thứ nhất.',
      disposition: 'answered',
      providerUsed: true,
      citations: [],
    });
    render(<ChatWorkspace />);
    ask();
    expect(await screen.findByText('Trả lời thứ nhất.')).toBeInTheDocument();
    vi.mocked(chatService.send).mockRejectedValueOnce(new ApiError(401, 'Phiên đã hết hạn.'));
    fireEvent.change(screen.getByLabelText('Câu hỏi của bạn'), {
      target: { value: 'Câu thứ hai?' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Gửi câu hỏi' }));
    await waitFor(() =>
      expect(navigation.replace).toHaveBeenCalledWith('/dang-nhap?returnTo=%2Fhoi-dap'),
    );
    expect(screen.getByText('Trả lời thứ nhất.')).toBeInTheDocument();
  });

  it.each([
    ['product', 'javascript:alert(1)', false],
    ['legal', 'https://example.gov.vn/van-ban', true],
    ['legal', 'https://congbao.chinhphu.vn/van-ban/luat-59.htm', true],
    ['legal', 'https://congbao.chinhphu.vn.attacker.example/van-ban', false],
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
    render(<ChatWorkspace />);
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
    render(<ChatWorkspace />);
    fireEvent.click(screen.getByRole('checkbox'));
    fireEvent.submit(screen.getByRole('form', { name: 'Đặt câu hỏi' }));
    expect(chatService.send).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('Vui lòng nhập câu hỏi.');
  });

  it('dùng thông báo an toàn khi lỗi không có kiểu Error', async () => {
    vi.mocked(chatService.send).mockRejectedValue(null);
    render(<ChatWorkspace />);
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
    render(<ChatWorkspace />);
    ask();
    expect(await screen.findByText('Bạn chọn Đã có cho giấy tờ đang giữ.')).toBeInTheDocument();
    expect(screen.getByText('Gemini · có gọi mô hình')).toBeInTheDocument();
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
    render(<ChatWorkspace />);
    ask();
    expect(await screen.findByText('Vui lòng bỏ thông tin riêng tư.')).toBeInTheDocument();
    expect(screen.getByText('Kiểm tra nội dung · chưa gọi mô hình')).toBeInTheDocument();
  });

  it('giữ câu hỏi khi hết hạn mức để người dùng thử lại sau', async () => {
    vi.mocked(chatService.send).mockRejectedValue(new Error('Đã chạm hạn mức trợ lý.'));
    render(<ChatWorkspace />);
    ask();
    expect(await screen.findByRole('alert')).toHaveTextContent('Đã chạm hạn mức trợ lý.');
    expect(screen.getByLabelText('Câu hỏi của bạn')).toHaveValue('Tôi dùng checklist thế nào?');
    expect(screen.getByRole('button', { name: 'Gửi câu hỏi' })).toBeEnabled();
  });

  it('yêu cầu xác nhận giới hạn dữ liệu trước khi gửi', () => {
    render(<ChatWorkspace />);
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
    const view = render(<ChatWorkspace />);
    ask();
    expect(await screen.findByText('<script>alert(1)</script>')).toBeInTheDocument();
    expect(view.container.querySelector('script')).toBeNull();
  });

  it('ghi rõ trích văn bản luật chưa được chuyên gia rà soát', async () => {
    vi.mocked(chatService.send).mockResolvedValue({
      reply: 'Theo Điều 210 khoản 1, hồ sơ gồm thông báo giải thể.',
      disposition: 'answered',
      providerUsed: true,
      citations: [
        {
          sourceId: 'L1',
          title: 'Luật Doanh nghiệp 59/2020/QH14 — Điều 210, Khoản 1',
          url: 'https://congbao.chinhphu.vn/van-ban/luat-59.htm',
          reviewedAt: null,
          kind: 'legal',
          fetchedAt: '2026-10-31T10:11:53Z',
          reviewStatus: 'unreviewed',
        },
      ],
    });
    render(<ChatWorkspace />);
    ask();
    expect(
      await screen.findByText(/chưa được chuyên gia rà soát, chưa xác minh hiệu lực/),
    ).toHaveTextContent('lấy ngày 31/10/2026');
  });

  it('tách danh sách đánh số trên một dòng thành từng dòng, giữ nguyên số hiệu điều khoản', () => {
    expect(formatReply('Hồ sơ gồm: 1. Thông báo giải thể. 2. Báo cáo thanh lý.')).toBe(
      'Hồ sơ gồm:\n1. Thông báo giải thể.\n2. Báo cáo thanh lý.',
    );
    expect(formatReply('Theo Điều 210 khoản 1, hồ sơ gồm thông báo.')).toBe(
      'Theo Điều 210 khoản 1, hồ sơ gồm thông báo.',
    );
  });
});
