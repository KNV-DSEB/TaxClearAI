from src.modules.conversion_planner.repository import ConversionPlannerRepository
from src.modules.conversion_planner.schemas import (
    BusinessModel,
    ConversionKind,
    ConversionPlanRequest,
    ConversionPlanResponse,
    HardStop,
    TaskState,
    WorkflowLane,
    WorkflowTask,
)

LEGAL_BASIS_PLACEHOLDER = "Chưa xác định căn cứ trong nguồn đã đồng bộ"


class ConversionPlannerService:
    def __init__(self, repository: ConversionPlannerRepository) -> None:
        self._repository = repository

    def plan(self, request: ConversionPlanRequest) -> ConversionPlanResponse:
        kind = self._conversion_kind(request)
        completed = set(request.completed_task_ids)
        self._add_legacy_completions(request, completed)
        needs_expert = any(
            (
                request.has_multiple_members,
                request.has_large_capital_contribution,
                request.has_dispute,
            )
        )

        if kind == ConversionKind.COMPANY_TYPE_CHANGE:
            return self._company_type_change_plan(request, completed, kind, needs_expert)

        close_tasks = self._hkd_closing_tasks(completed)
        new_tasks = self._new_model_tasks(request, completed, kind)
        if kind == ConversionKind.HKD_TO_HKD:
            hard_stops = [self._hkd_to_hkd_stop(request)]
            legal_note = (
                "Luồng HKD→HKD: các việc chuẩn bị hồ sơ mới có thể thực hiện song song. "
                "Chốt nộp hồ sơ mới "
                "chỉ được gỡ khi trạng thái thuế và đăng ký HKD cũ đã được xác nhận hoàn tất. "
                "Đây là kế hoạch kiểm soát, không thay thế xác nhận của cơ quan có thẩm quyền."
            )
        else:
            hard_stops = [self._hkd_to_company_stop(request)]
            legal_note = (
                "Có thể chuẩn bị hồ sơ công ty mới trong khi xử lý HKD cũ. Thư viện legal_library "
                "hiện chưa có căn cứ chuyên biệt xác nhận điều kiện chặn HKD→công ty; chốt kiểm "
                "soát dùng placeholder và cần chuyên gia xác nhận trước khi nộp/kích hoạt mô hình "
                "mới. Không coi đây là kết luận rằng pháp luật bắt buộc đóng HKD trước khi "
                "lập công ty."
            )

        lanes = [
            self._lane("close_old", "Luồng 1 — Đóng HKD cũ", close_tasks),
            self._lane(
                "open_new",
                "Luồng 2 — Chuẩn bị "
                + ("HKD mới" if kind == ConversionKind.HKD_TO_HKD else "công ty mới")
                + " song song",
                new_tasks,
            ),
        ]
        next_action = self._hkd_next_action(request, kind, hard_stops[0], new_tasks)
        return ConversionPlanResponse(
            current_model=request.current_model,
            desired_model=request.desired_model,
            conversion_kind=kind,
            lanes=lanes,
            hard_stops=hard_stops,
            next_action=next_action,
            legal_note=legal_note,
            needs_expert=needs_expert
            or (kind == ConversionKind.HKD_TO_COMPANY and hard_stops[0].active),
        )

    def _company_type_change_plan(
        self,
        request: ConversionPlanRequest,
        completed: set[str],
        kind: ConversionKind,
        needs_expert: bool,
    ) -> ConversionPlanResponse:
        if request.conversion_legal_review_confirmed:
            completed.add("change_review")
        tasks = [
            self._task(
                "change_review",
                "Xác minh điều kiện, trình tự và danh mục hồ sơ chuyển đổi với chuyên gia.",
                [],
                completed,
            ),
            self._task(
                "conversion_resolution",
                "Chuẩn bị nghị quyết/quyết định chuyển đổi phù hợp với cơ cấu công ty.",
                ["change_review"],
                completed,
            ),
            self._task(
                "conversion_documents",
                "Chuẩn bị hồ sơ đăng ký thay đổi loại hình theo danh mục đã được xác minh.",
                ["conversion_resolution"],
                completed,
            ),
            self._task(
                "submit_company_change",
                "Nộp hồ sơ đăng ký thay đổi loại hình và theo dõi kết quả.",
                ["conversion_documents"],
                completed,
            ),
            self._task(
                "update_company_records",
                "Sau khi có kết quả, rà soát và cập nhật thông tin thuế, BHXH, hóa đơn "
                "và hồ sơ liên quan.",
                ["submit_company_change"],
                completed,
            ),
        ]
        legal_basis = self._repository.get_transition_legal_basis(kind.value)
        stop_active = not request.conversion_legal_review_confirmed
        hard_stop = HardStop(
            code="COMPANY_TYPE_CHANGE_REQUIRES_VERIFICATION",
            active=stop_active,
            blocks="Nộp hồ sơ đăng ký thay đổi loại hình công ty",
            reason=(
                "Chưa xác minh căn cứ và trình tự chuyển đổi trong thư viện pháp lý; cần chuyên "
                "gia rà soát trước khi nộp hồ sơ."
                if stop_active
                else "Đã khai báo hoàn tất bước chuyên gia xác minh lộ trình chuyển đổi."
            ),
            legal_basis=legal_basis or LEGAL_BASIS_PLACEHOLDER,
            legal_scope_note=(
                "Đây là chốt xác minh quy trình, không phải thủ tục giải thể hay chấm dứt mã số "
                "thuế. Mô tả chỉ ở mức quy trình chung; cần đối chiếu hồ sơ và nguồn hiện hành."
            ),
        )
        next_action = self._company_change_next_action(tasks, stop_active)
        return ConversionPlanResponse(
            current_model=request.current_model,
            desired_model=request.desired_model,
            conversion_kind=kind,
            lanes=[self._lane("company_type_change", "Luồng đổi loại hình công ty", tasks)],
            hard_stops=[hard_stop],
            next_action=next_action,
            legal_note=(
                "Đây là luồng đăng ký thay đổi loại hình, không phải giải thể: không tạo bước đóng "
                "MST hoặc chấm dứt đăng ký công ty cũ. Trình tự và căn cứ cụ thể cần được xác "
                "minh từ legal_library hoặc chuyên gia; hiện không có căn cứ chuyên biệt nên "
                f"dùng {LEGAL_BASIS_PLACEHOLDER}."
            ),
            needs_expert=needs_expert or stop_active,
        )

    @staticmethod
    def _conversion_kind(request: ConversionPlanRequest) -> ConversionKind:
        if request.current_model == BusinessModel.HKD:
            return (
                ConversionKind.HKD_TO_HKD
                if request.desired_model == BusinessModel.HKD
                else ConversionKind.HKD_TO_COMPANY
            )
        return ConversionKind.COMPANY_TYPE_CHANGE

    @staticmethod
    def _add_legacy_completions(request: ConversionPlanRequest, completed: set[str]) -> None:
        if request.old_tax_obligations_settled or request.old_tax_id_termination_confirmed:
            completed.update({"old_tax_review", "old_tax_settlement"})
        if (
            request.old_tax_id_termination_confirmed
            or request.old_registration_termination_confirmed
        ):
            completed.add("old_tax_close")
        if request.old_registration_termination_confirmed:
            completed.add("old_registration_close")
        if request.new_name_prepared:
            completed.add("new_name")
        if request.new_address_prepared:
            completed.add("new_address")
        if request.new_industry_prepared:
            completed.add("new_industry")

    @staticmethod
    def _hkd_closing_tasks(completed: set[str]) -> list[WorkflowTask]:
        return [
            ConversionPlannerService._task(
                "old_tax_review",
                "Đối chiếu nghĩa vụ thuế của HKD cũ và thông tin chủ hộ.",
                [],
                completed,
            ),
            ConversionPlannerService._task(
                "old_tax_settlement",
                "Đối chiếu và xử lý các nghĩa vụ thuế còn được cơ quan thuế xác định.",
                ["old_tax_review"],
                completed,
            ),
            ConversionPlannerService._task(
                "old_tax_close",
                "Thực hiện thủ tục thuế liên quan đến chấm dứt HKD cũ và theo dõi trạng thái.",
                ["old_tax_settlement"],
                completed,
            ),
            ConversionPlannerService._task(
                "old_registration_close",
                "Nộp hồ sơ chấm dứt đăng ký HKD cũ và nhận kết quả cập nhật trạng thái.",
                ["old_tax_close"],
                completed,
            ),
        ]

    @staticmethod
    def _new_model_tasks(
        request: ConversionPlanRequest,
        completed: set[str],
        kind: ConversionKind,
    ) -> list[WorkflowTask]:
        new_model_label = "HKD" if kind == ConversionKind.HKD_TO_HKD else "công ty"
        return [
            ConversionPlannerService._task(
                "new_name", f"Chuẩn bị tên dự kiến cho {new_model_label} mới.", [], completed
            ),
            ConversionPlannerService._task(
                "new_address",
                f"Chuẩn bị địa chỉ cho {new_model_label} mới và thông tin liên quan.",
                [],
                completed,
            ),
            ConversionPlannerService._task(
                "new_industry",
                "Chuẩn bị ngành nghề dự kiến và thông tin cần rà soát.",
                [],
                completed,
            ),
            ConversionPlannerService._task(
                "new_file",
                "Soạn hồ sơ đăng ký mô hình mới; chỉ nộp sau khi qua chốt chặn áp dụng.",
                ["new_name", "new_address", "new_industry"],
                completed,
            ),
        ]

    @staticmethod
    def _hkd_to_hkd_stop(request: ConversionPlanRequest) -> HardStop:
        return HardStop(
            code="OLD_HKD_STATUS_NOT_CLOSED",
            active=not (
                request.old_tax_id_termination_confirmed
                and request.old_registration_termination_confirmed
            ),
            blocks="Nộp hồ sơ HKD mới cùng cá nhân đứng tên",
            reason=(
                "Chưa xác nhận hoàn tất trạng thái thuế và đăng ký của HKD cũ; "
                "giữ hồ sơ mới ở trạng thái chuẩn bị."
            ),
            legal_basis="Nghị định 168/2025/NĐ-CP, khoản 1 Điều 83 và khoản 1 Điều 104.",
            legal_scope_note=(
                "Điều 83 giới hạn mỗi cá nhân/thành viên hộ gia đình đăng ký một HKD trên toàn "
                "quốc; Điều 104 quy định xử lý nghĩa vụ và thủ tục chấm dứt HKD. Văn bản không "
                "quy định giấy xác nhận đóng MST riêng là điều kiện chung trước mọi hồ sơ HKD mới. "
                "Đây là chốt kiểm soát vận hành cho trường hợp HKD→HKD; cần đối chiếu trạng thái "
                "hồ sơ và hướng dẫn của cơ quan đăng ký cấp xã."
            ),
        )

    def _hkd_to_company_stop(self, request: ConversionPlanRequest) -> HardStop:
        closed = (
            request.old_tax_id_termination_confirmed
            and request.old_registration_termination_confirmed
        )
        reviewed = request.conversion_legal_review_confirmed
        basis = self._repository.get_transition_legal_basis(ConversionKind.HKD_TO_COMPANY.value)
        return HardStop(
            code="OLD_HKD_TO_COMPANY_STATUS_REQUIRES_REVIEW",
            active=not (closed and reviewed),
            blocks="Nộp/kích hoạt hồ sơ công ty mới",
            reason=(
                "Cần chuyên gia xác nhận căn cứ áp dụng và tình trạng HKD cũ trước khi nộp hoặc "
                "kích hoạt mô hình mới."
                if not (closed and reviewed)
                else "Đã xác nhận trạng thái HKD cũ và rà soát lộ trình với chuyên gia."
            ),
            legal_basis=basis or LEGAL_BASIS_PLACEHOLDER,
            legal_scope_note=(
                "legal_library hiện không có căn cứ chuyên biệt kết luận việc đóng HKD là điều "
                "kiện pháp lý để thành lập công ty. Chốt này là kiểm soát tạm thời để chuyên gia "
                "xác minh; không được trình bày như quy định pháp luật đã xác nhận."
            ),
        )

    @staticmethod
    def _hkd_next_action(
        request: ConversionPlanRequest,
        kind: ConversionKind,
        stop: HardStop,
        tasks: list[WorkflowTask],
    ) -> str:
        if stop.active:
            if kind == ConversionKind.HKD_TO_COMPANY:
                return (
                    "Tiếp tục chuẩn bị tên, địa chỉ, ngành nghề và hồ sơ công ty; đồng thời hoàn "
                    "tất toán/chấm dứt HKD cũ và chuyển chuyên gia xác nhận chốt áp dụng trước "
                    "khi nộp hoặc kích hoạt công ty."
                )
            return (
                "Tiếp tục chuẩn bị HKD mới; hoàn tất và xác nhận trạng thái thuế cùng đăng ký "
                "HKD cũ trước khi nộp hồ sơ HKD mới."
            )
        file_task = next(task for task in tasks if task.task_id == "new_file")
        if file_task.status == TaskState.READY:
            return (
                "Rà soát hồ sơ mô hình mới đã chuẩn bị và nộp theo hướng dẫn của cơ quan tiếp nhận."
            )
        return "Hoàn thiện tên, địa chỉ và ngành nghề để soạn hồ sơ mô hình mới."

    @staticmethod
    def _company_change_next_action(tasks: list[WorkflowTask], stop_active: bool) -> str:
        if stop_active:
            return (
                "Chuyển chuyên gia xác minh trình tự và căn cứ áp dụng; chưa nộp hồ sơ thay đổi "
                "loại hình. Không thực hiện đóng MST/giải thể công ty cũ trong luồng này."
            )
        next_task = next((task for task in tasks if task.status != TaskState.COMPLETED), None)
        if next_task is None:
            return "Theo dõi kết quả và rà soát cập nhật thông tin thuế, BHXH, hóa đơn liên quan."
        return next_task.action

    @staticmethod
    def _task(
        task_id: str,
        action: str,
        dependencies: list[str],
        completed: set[str],
    ) -> WorkflowTask:
        if task_id in completed:
            status = TaskState.COMPLETED
        elif any(dependency not in completed for dependency in dependencies):
            status = TaskState.BLOCKED
        else:
            status = TaskState.READY
        return WorkflowTask(
            task_id=task_id,
            action=action,
            status=status,
            depends_on=dependencies,
            responsible_party="Khách hàng + chuyên gia",
            note=(
                "Chỉ rà soát danh mục/thông tin khai báo; không gửi giấy tờ gốc nhạy cảm "
                "qua bước này."
            ),
        )

    @staticmethod
    def _lane(lane_id: str, title: str, tasks: list[WorkflowTask]) -> WorkflowLane:
        completed = sum(task.status == TaskState.COMPLETED for task in tasks)
        return WorkflowLane(
            lane_id=lane_id,
            title=title,
            progress_percentage=round(completed * 100 / len(tasks)),
            tasks=tasks,
        )
