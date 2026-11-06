"""Nạp câu hỏi cộng đồng MẪU (người hỏi minh họa, không phải doanh nghiệp thật) để phát triển và trình diễn."""

# Dữ liệu mẫu giữ nguyên câu văn tự nhiên để nội dung hiển thị dễ đọc.
# ruff: noqa: E501

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select

from src.core.database import _session_factory
from src.models.community import CommunityQuestion, CommunityTopic

TOPICS_DATA = [
    ("giai-the-pha-san", "Về tổ chức lại, giải thể và phá sản doanh nghiệp"),
    ("tam-ngung-kinh-doanh", "Tạm ngừng kinh doanh & Khôi phục hoạt động"),
    ("thay-doi-nguoi-dai-dien", "Thay đổi người đại diện theo pháp luật"),
    ("chuyen-doi-loai-hinh", "Chuyển đổi loại hình doanh nghiệp"),
    ("cham-dut-dia-diem", "Chấm dứt văn phòng đại diện, địa điểm kinh doanh"),
]

_LEGAL_NOTE = (
    "Thông tin tham khảo, không thay thế việc rà soát hồ sơ và nghĩa vụ thuế cụ thể. "
    "Căn cứ cần đối chiếu theo thời điểm thực hiện, gồm Luật Doanh nghiệp 59/2020/QH14 "
    "được sửa đổi bởi Luật 76/2025/QH15; Nghị định 168/2025/NĐ-CP được sửa đổi bởi "
    "Nghị định 296/2026/NĐ-CP; và Luật Quản lý thuế 108/2025/QH15 (thay Luật 38/2019/QH14 từ 01/07/2026) "
    "cùng văn bản hướng dẫn. Hiệu lực các văn bản chưa được chuyên gia xác minh."
)

_QUESTION_TEMPLATES = [
    {
        "topic_slug": "chuyen-doi-loai-hinh",
        "title": "Chuyển đổi loại hình doanh nghiệp",
        "author_name": "Người hỏi mẫu 1",
        "question_content": "Công ty tôi muốn chuyển từ TNHH một thành viên sang công ty cổ phần. Chủ sở hữu hiện tại chưa có người góp vốn mới. Có phương án nào để đáp ứng điều kiện về cổ đông và cần rà soát những nội dung nào?",
        "answer_content": (
            "Luật Doanh nghiệp quy định công ty TNHH có thể chuyển đổi thành công ty cổ phần theo các phương thức luật định, "
            "trong đó có chuyển nhượng một phần vốn góp để hình thành thêm cổ đông. Công ty cổ phần cần có tối thiểu ba cổ đông. "
            "Doanh nghiệp nên rà soát phương án vốn, điều lệ, danh sách cổ đông, hồ sơ đăng ký chuyển đổi và nghĩa vụ thuế phát sinh.\n\n"
            + _LEGAL_NOTE
        ),
    },
    {
        "topic_slug": "tam-ngung-kinh-doanh",
        "title": "Về việc tạm ngừng kinh doanh",
        "author_name": "Người hỏi mẫu 2",
        "question_content": "Doanh nghiệp dự định tạm ngừng hoạt động. Cần thông báo với cơ quan nào và việc tạm ngừng có làm mất các nghĩa vụ thuế đã phát sinh không?",
        "answer_content": (
            "Doanh nghiệp cần thực hiện thủ tục thông báo tạm ngừng theo quy định đăng ký doanh nghiệp đang có hiệu lực và kiểm tra thời hạn, biểu mẫu tại thời điểm nộp. "
            "Tạm ngừng không tự động xóa các khoản thuế, nợ hoặc nghĩa vụ đã phát sinh trước thời điểm tạm ngừng; trách nhiệm kê khai trong thời gian tạm ngừng phụ thuộc tình trạng và quy định áp dụng cho doanh nghiệp.\n\n"
            + _LEGAL_NOTE
        ),
    },
    {
        "topic_slug": "giai-the-pha-san",
        "title": "Về việc hủy bỏ nghị quyết, quyết định giải thể doanh nghiệp",
        "author_name": "Người hỏi mẫu 3",
        "question_content": "Doanh nghiệp đã thông qua và gửi thông báo giải thể nhưng sau đó muốn tiếp tục hoạt động. Có thể hủy quyết định này không, và cần kiểm tra tình trạng nào trước?",
        "answer_content": (
            "Khả năng tiếp tục hoạt động phụ thuộc vào giai đoạn giải thể và việc doanh nghiệp đã hoàn tất các thủ tục chấm dứt hay chưa. "
            "Cần kiểm tra tình trạng hồ sơ trên hệ thống đăng ký doanh nghiệp, nghị quyết/quyết định đã ban hành, tình trạng mã số thuế và các nghĩa vụ với chủ nợ, người lao động. "
            "Không nên mặc định chỉ cần rút thông báo là doanh nghiệp được hoạt động lại; hãy xác nhận thủ tục với cơ quan đăng ký kinh doanh và cơ quan thuế quản lý trực tiếp.\n\n"
            + _LEGAL_NOTE
        ),
    },
    {
        "topic_slug": "thay-doi-nguoi-dai-dien",
        "title": "Thay đổi người đại diện theo pháp luật",
        "author_name": "Người hỏi mẫu 4",
        "question_content": "Người đại diện theo pháp luật của công ty qua đời khi công ty đang làm thủ tục giải thể. Công ty có thể thay người đại diện để tiếp tục xử lý hồ sơ không?",
        "answer_content": (
            "Cần xác định doanh nghiệp đang ở bước nào và còn tư cách hoạt động hay đã hoàn tất chấm dứt tồn tại. "
            "Nếu doanh nghiệp còn phải thực hiện thủ tục, cơ quan có thẩm quyền trong nội bộ công ty cần xử lý việc thay đổi người đại diện theo điều lệ và Luật Doanh nghiệp, sau đó đăng ký thay đổi theo quy định hiện hành. "
            "Hồ sơ cụ thể có thể khác theo loại hình doanh nghiệp và tình trạng giải thể; cần xác nhận với cơ quan đăng ký kinh doanh trước khi nộp.\n\n"
            + _LEGAL_NOTE
        ),
    },
    {
        "topic_slug": "cham-dut-dia-diem",
        "title": "Chấm dứt hoạt động văn phòng đại diện tại nước ngoài",
        "author_name": "Người hỏi mẫu 5",
        "question_content": "Công ty muốn chấm dứt một văn phòng đại diện ở nước ngoài. Cần làm thủ tục đăng ký nào tại Việt Nam và phải đối chiếu nghĩa vụ thuế ra sao?",
        "answer_content": (
            "Doanh nghiệp cần thông báo chấm dứt hoạt động địa điểm kinh doanh với cơ quan đăng ký kinh doanh có thẩm quyền theo quy định hiện hành. "
            "Đồng thời cần rà soát hồ sơ khai thuế, hóa đơn, khoản phải nộp và việc sử dụng mã số thuế phụ (nếu có) với cơ quan thuế quản lý. "
            "Nghĩa vụ cụ thể phụ thuộc cách đăng ký và tình trạng hoạt động của địa điểm; không nên suy ra đã hoàn tất nghĩa vụ chỉ từ việc ngừng hoạt động thực tế.\n\n"
            + _LEGAL_NOTE
        ),
    },
    {
        "topic_slug": "cham-dut-dia-diem",
        "title": "Chấm dứt hoạt động địa điểm kinh doanh",
        "author_name": "Người hỏi mẫu 5",
        "question_content": "Công ty đã ngừng hoạt động một địa điểm kinh doanh nhưng chưa hoàn tất thông báo. Cần rà soát thủ tục đăng ký và nghĩa vụ liên quan nào?",
        "answer_content": (
            "Doanh nghiệp cần thông báo chấm dứt hoạt động địa điểm kinh doanh với cơ quan đăng ký kinh doanh có thẩm quyền theo quy định hiện hành. "
            "Đồng thời cần rà soát hồ sơ khai thuế, hóa đơn, khoản phải nộp và việc sử dụng mã số thuế phụ (nếu có) với cơ quan thuế quản lý. "
            "Thời hạn và hồ sơ cần đối chiếu theo quy định đang có hiệu lực tại thời điểm nộp; việc ngừng hoạt động thực tế không tự hoàn tất thủ tục.\n\n"
            + _LEGAL_NOTE
        ),
    },
]


async def seed() -> None:
    async with _session_factory() as session:
        topics = list((await session.scalars(select(CommunityTopic))).all())
        topic_map = {topic.slug: topic for topic in topics}
        for order_index, (slug, name) in enumerate(TOPICS_DATA, start=1):
            topic = topic_map.get(slug)
            if topic is None:
                topic = CommunityTopic(
                    id=uuid4(), slug=slug, name=name, order_index=order_index, is_active=True
                )
                session.add(topic)
                topic_map[slug] = topic
            else:
                topic.name = name
                topic.order_index = order_index
                topic.is_active = True
        await session.flush()

        questions = list((await session.scalars(select(CommunityQuestion))).all())
        seeded_by_title = {question.title: question for question in questions}
        seeded_at = datetime(2026, 10, 15, 9, 0, tzinfo=UTC)
        for data in _QUESTION_TEMPLATES:
            question = seeded_by_title.get(data["title"])
            if question is None:
                question = CommunityQuestion(id=uuid4(), created_at=seeded_at)
                session.add(question)
                seeded_by_title[data["title"]] = question
            question.topic_id = topic_map[data["topic_slug"]].id
            question.author_name = data["author_name"]
            question.author_id = None
            question.title = data["title"]
            question.question_content = data["question_content"]
            question.answer_content = data["answer_content"]
            question.answered_by = "Tax Clear · Nội dung mẫu"
            question.answered_at = seeded_at
            question.is_published = True
        await session.commit()
        print("Đã nạp dữ liệu cộng đồng mẫu.")


if __name__ == "__main__":
    asyncio.run(seed())
