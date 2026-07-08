import pytest

from app.ai.clients.deepseek_client import DeepSeekClient
from app.ai.schemas import SelectionReportInput
from app.common.exceptions import BusinessException


class FakeDeepSeekClient(DeepSeekClient):
    """测试用 DeepSeek 客户端，通过覆写模型调用避免访问真实 API。"""

    def __init__(self, response: str) -> None:
        self.response = response
        self.model = "fake-model"
        self.temperature = 0.2
        self.max_tokens = 1000
        self.timeout_seconds = 1
        self._client = object()

    def _chat_json(self, messages: list[dict[str, str]]) -> str:
        return self.response


def test_normalize_keyword_parses_structured_result() -> None:
    """验证关键词归一化可以解析模型 JSON 输出。"""
    client = FakeDeepSeekClient(
        '{"normalized_keyword":"smart fitness band","detected_language":"zh-CN","search_terms":["smart fitness band","fitness tracker"]}'
    )

    result = client.normalize_keyword(keyword="智能手环", country="US", language="zh-CN")

    assert result.normalized_keyword == "smart fitness band"
    assert result.search_terms == ["smart fitness band", "fitness tracker"]


def test_generate_selection_report_parses_report_dto() -> None:
    """验证报告生成可以解析为 ReportDTO。"""
    client = FakeDeepSeekClient(
        '{"title":"选品分析报告：智能手环","markdown_content":"# 选品分析报告：智能手环","summary":"适合进一步调研","recommendation":"cautiously_recommended"}'
    )
    report_input = SelectionReportInput(keyword="智能手环", normalized_keyword="smart fitness band")

    result = client.generate_selection_report(report_input)

    assert result.title == "选品分析报告：智能手环"
    assert result.recommendation == "cautiously_recommended"


def test_parse_json_model_raises_business_exception_on_invalid_json() -> None:
    """验证模型返回非 JSON 时会转成业务异常。"""
    client = FakeDeepSeekClient("not-json")

    with pytest.raises(BusinessException) as exception_info:
        client.normalize_keyword(keyword="智能手环", country="US", language="zh-CN")

    assert exception_info.value.code == "DEEPSEEK_PARSE_FAILED"

