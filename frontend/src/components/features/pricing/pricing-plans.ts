export type PlanId = 'free' | 'support' | 'expert';

export interface PlanFeature {
  text: string;
  // Tính năng nêu trong đề án nhưng bản thử chưa có
  planned?: boolean;
}

export interface Plan {
  id: PlanId;
  step: 1 | 2 | 3;
  name: string;
  summary: string;
  price: string;
  priceNote: string;
  available: boolean;
  statusLabel: string;
  features: PlanFeature[];
}

// Giá và phạm vi lấy từ đề án (mục 4.2). Đây là giá dự kiến để kiểm chứng, bản thử chưa thu phí.
export const PLANS: Plan[] = [
  {
    id: 'free',
    step: 1,
    name: 'Tra cứu cơ bản',
    summary: 'Tự tìm hiểu tình trạng của mình và nguồn luật liên quan.',
    price: 'Miễn phí',
    priceNote: 'Không cần tài khoản để dùng thử',
    available: true,
    statusLabel: 'Đang mở trong bản thử',
    features: [
      { text: 'Khảo sát chẩn đoán tình trạng doanh nghiệp' },
      { text: 'Tổng hợp tình trạng và danh mục giấy tờ cần chuẩn bị' },
      { text: 'Thư viện pháp luật có dẫn nguồn văn bản gốc' },
      { text: 'Hỏi đáp AI có giới hạn lượt mỗi ngày (dự kiến 5 lượt/ngày)' },
    ],
  },
  {
    id: 'support',
    step: 2,
    name: 'Hỗ trợ hoàn thiện hồ sơ',
    summary: 'Một hồ sơ được theo dõi từ đầu đến khi đủ giấy tờ.',
    price: '250.000 đ',
    priceNote: 'mỗi hồ sơ, giá dự kiến',
    available: false,
    statusLabel: 'Sắp mở, chưa thu phí',
    features: [
      { text: 'Bản đồ thủ tục cá nhân hóa theo hồ sơ của bạn' },
      { text: 'Lưu hồ sơ và theo dõi tiến độ trong 90 ngày' },
      { text: 'Hỏi đáp AI không giới hạn lượt trong 90 ngày' },
      { text: 'Bản tổng hợp xuất ra để làm việc với chuyên gia' },
      { text: 'Cảnh báo thông tin thiếu hoặc không nhất quán', planned: true },
    ],
  },
  {
    id: 'expert',
    step: 3,
    name: 'Kết nối chuyên gia',
    summary: 'Chuyển hồ sơ phức tạp cho người làm thuế, kế toán hoặc luật sư.',
    price: 'Phí nền tảng 15%',
    priceNote: 'trên phí dịch vụ của chuyên gia',
    available: false,
    statusLabel: 'Sắp mở, chưa thu phí',
    features: [
      { text: 'Biết phạm vi công việc và mức phí trước khi đồng ý' },
      { text: 'Chuyển bản tổng hợp hồ sơ, chuyên gia đỡ phải hỏi lại' },
      { text: 'Bạn tự quyết định có chia sẻ dữ liệu hồ sơ hay không' },
      { text: 'Danh sách chuyên gia đã xác thực', planned: true },
    ],
  },
];

// Ví dụ lấy từ đề án: ca tư vấn trung bình 3.500.000 đ, nền tảng giữ 15%
export const EXPERT_FEE_EXAMPLE = {
  serviceFee: '3.500.000 đ',
  platformFee: '525.000 đ',
};

export const TRIAL_NOTICE =
  'Bản thử đang mở miễn phí mọi tính năng và chưa thu phí. Các mức giá dưới đây là kế hoạch dự kiến để nhóm kiểm chứng với người dùng.';

export const FAQ: { question: string; answer: string }[] = [
  {
    question: 'Tôi có phải trả tiền bây giờ không?',
    answer:
      'Không. Bản thử chưa có thanh toán và chưa thu bất kỳ khoản nào. Bạn có thể dùng đầy đủ khảo sát, danh mục giấy tờ, thư viện pháp luật và hỏi đáp AI.',
  },
  {
    question: 'Vì sao đã có giá mà chưa bán?',
    answer:
      'Nhóm cần biết mức giá nào người làm thủ tục giải thể thấy hợp lý trước khi mở bán. Giá hiện tại là dự kiến và có thể thay đổi sau khi lắng nghe người dùng.',
  },
  {
    question: 'Phí nền tảng 15% do ai trả?',
    answer: `Đó là phần nền tảng giữ lại từ phí dịch vụ của chuyên gia. Ví dụ ca tư vấn ${EXPERT_FEE_EXAMPLE.serviceFee} thì phần giữ lại là ${EXPERT_FEE_EXAMPLE.platformFee}. Bạn sẽ thấy tổng số tiền trước khi đồng ý, và con số này chỉ là ví dụ minh họa.`,
  },
  {
    question: 'Trợ lý AI có thay luật sư hay kế toán không?',
    answer:
      'Không. Trợ lý chỉ giải thích tổng quát và dẫn nguồn, không tính thuế hay tiền phạt và không kết luận về hồ sơ cụ thể. Trường hợp phức tạp nên trao đổi với chuyên gia.',
  },
];
