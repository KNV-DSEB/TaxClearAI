from src.modules.chatbot.schemas import ChatResponse

EXPERT_TEMPLATES: dict[str, str] = {
    "bi_co_quan_lien_he": (
        "Bạn cho biết đã có liên hệ/yêu cầu từ cơ quan thuế. Trường hợp này cần chuyên gia "
        "xem xét thông báo và hồ sơ cụ thể; chatbot không đánh giá vi phạm hay hướng dẫn "
        "xử lý thay chuyên gia."
    ),
    "sai_lech_so_lieu": (
        "Bạn nêu có chênh lệch giữa số liệu kê khai và thực tế. Cần chuyên gia đối chiếu "
        "chứng từ, hóa đơn và dữ liệu liên quan; chatbot không kết luận mức độ sai lệch."
    ),
    "no_ton_dong": (
        "Thông tin có nghĩa vụ thuế, hóa đơn, tài sản hoặc lao động còn tồn. Cần chuyên gia "
        "rà soát hồ sơ và nghĩa vụ cụ thể trước khi xác định lộ trình."
    ),
    "ne_thue": (
        "Chatbot không hỗ trợ né thuế, che giấu doanh thu hoặc làm sai lệch hồ sơ. Với vướng "
        "mắc tuân thủ, chuyên gia có thể rà soát phương án thực hiện đúng quy định."
    ),
    "chuyen_nhuong_phuc_tap": (
        "Tình huống có yếu tố chuyển nhượng, tranh chấp hoặc nhiều bên cần được chuyên gia "
        "xem xét hợp đồng và hồ sơ cụ thể."
    ),
    "khong_chac_chan": (
        "Chưa thể xác định căn cứ an toàn từ thông tin hiện có. Câu hỏi cần được chuyên gia "
        "chuyên gia rà soát."
    ),
    "ngoai_pham_vi": (
        "Câu hỏi nằm ngoài phạm vi giải thích thủ tục thuế, đăng ký và chấm dứt hoạt động "
        "kinh doanh. Chatbot chưa thể hỗ trợ nội dung này."
    ),
}

MONEY_TEMPLATE = (
    "Chatbot không tính hoặc ước lượng thuế, tiền phạt, phí. Có thể tra cứu nghĩa vụ trên "
    "cổng Thuế điện tử hoặc hỏi cơ quan thuế; dữ liệu cụ thể cần đối chiếu theo hồ sơ và "
    "có thể được chuyên gia rà soát."
)
SERVICE_FEE_TEMPLATE = (
    "Chatbot không ước lượng phí dịch vụ. Khung phí tham khảo có thể được "
    "tra cứu tại POST /cases/brief; khoản này tách biệt với tiền nộp ngân sách nhà nước."
)
PENALTY_PRINCIPLE_EXPERT_NOTE = (
    "Câu trả lời này chỉ giải thích nguyên tắc chung; bạn có thể kết nối chuyên gia để rà soát "
    "hồ sơ cụ thể."
)
DECISION_BOUNDARY_TEMPLATE = (
    "Hệ thống chỉ mô tả các hướng; quyết định thuộc về bạn, có thể tham khảo chuyên gia."
)
NO_SOURCE_TEMPLATE = "Chưa tìm thấy căn cứ pháp lý đủ điều kiện từ nguồn nhà nước."
SAFE_FALLBACK_TEMPLATE = (
    "Chưa thể tạo câu trả lời an toàn từ căn cứ hiện có. Câu hỏi cần chuyên gia rà soát."
)


def fixed_response(
    answer: str,
    *,
    mode: int = 3,
    reason: str,
) -> ChatResponse:
    """Build a fixed safety response without sending it through the LLM."""
    return ChatResponse(
        answer=answer,
        citations=[],
        sources=[],
        needs_expert=mode == 3,
        mode=mode,
        block_reason=reason,
    )
