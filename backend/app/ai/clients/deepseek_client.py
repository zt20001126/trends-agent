import json
import logging
from collections.abc import Sequence
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from app.ai.schemas import (
    KeywordNormalizationResult,
    ReviewPainPointSummary,
    SelectionReportInput,
)
from app.common.exceptions import BusinessException
from app.core.settings import settings
from app.schemas.selection import ReportDTO

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek AI 客户端，统一封装模型调用、Prompt 构造和结构化输出解析。

    业务边界：API route 和普通业务服务不得直接调用模型供应商，只能通过该客户端或后续 AI 节点调用。
    """

    def __init__(self) -> None:
        self.model = settings.deepseek_model
        self.temperature = settings.deepseek_temperature
        self.max_tokens = settings.deepseek_max_tokens
        self.timeout_seconds = settings.deepseek_timeout_seconds
        self._client = self._create_client()

    def normalize_keyword(
        self,
        keyword: str,
        country: str,
        language: str,
    ) -> KeywordNormalizationResult:
        """归一化商品关键词。

        Step 1: 构造只返回 JSON 的关键词归一化 Prompt。
        Step 2: 调用 DeepSeek 获取结构化文本。
        Step 3: 校验模型输出，避免脏数据进入 Tool 检索层。
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "你是跨境电商选品关键词专家。只返回 JSON，不要返回 Markdown。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请将商品关键词归一化为适合美国站 Google Trends 和 Amazon 检索的英文关键词。"
                    f"原始关键词：{keyword}\n"
                    f"目标国家：{country}\n"
                    f"输入语言：{language}\n"
                    '返回 JSON 格式：{"normalized_keyword":"...","detected_language":"...","search_terms":["..."]}'
                ),
            },
        ]
        content = self._chat_json(messages)
        return self._parse_json_model(content, KeywordNormalizationResult)

    def summarize_review_pain_points(
        self,
        keyword: str,
        reviews: Sequence[str],
    ) -> ReviewPainPointSummary:
        """总结评论痛点和产品改进建议。"""
        safe_reviews = list(reviews)[: settings.deepseek_review_sample_limit]
        messages = [
            {
                "role": "system",
                "content": "你是跨境电商评论分析专家。只返回 JSON，不要返回 Markdown。",
            },
            {
                "role": "user",
                "content": (
                    "请基于以下 Amazon 评论提取用户痛点和产品改进建议。"
                    f"商品关键词：{keyword}\n"
                    f"评论样本：{json.dumps(safe_reviews, ensure_ascii=False)}\n"
                    '返回 JSON 格式：{"pain_points":[{"name":"...","evidence":"..."}],'
                    '"improvements":[{"name":"...","reason":"..."}],"sentiment_summary":"..."}'
                ),
            },
        ]
        content = self._chat_json(messages)
        return self._parse_json_model(content, ReviewPainPointSummary)

    def generate_selection_report(self, report_input: SelectionReportInput) -> ReportDTO:
        """生成 Markdown 选品报告。"""
        messages = [
            {
                "role": "system",
                "content": (
                    "你是跨境电商选品分析师。请基于工具结果生成谨慎、可执行的 Markdown 报告。"
                    "必须声明公开数据限制，不得编造销量、利润或实时 Amazon 指标。只返回 JSON。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请生成选品报告。输入数据如下：\n"
                    f"{report_input.model_dump_json()}\n"
                    '返回 JSON 格式：{"title":"...","markdown_content":"# ...","summary":"...","recommendation":"..."}'
                ),
            },
        ]
        content = self._chat_json(messages)
        return self._parse_json_model(content, ReportDTO)

    def _create_client(self) -> OpenAI | None:
        """创建 OpenAI 兼容客户端，未配置 Key 时保留为空以便测试和降级。"""
        if not settings.deepseek_api_key:
            logger.info("DeepSeek API key is not configured; model calls will fail fast.")
            return None

        return OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout=settings.deepseek_timeout_seconds,
        )

    def _chat_json(self, messages: list[dict[str, str]]) -> str:
        """调用 DeepSeek 并返回文本内容。

        安全说明：日志只记录模型和消息数量，不记录 API Key 或完整 Prompt。
        """
        if self._client is None:
            raise BusinessException(message="DeepSeek API Key 未配置", code="DEEPSEEK_API_KEY_MISSING", http_status=500)

        logger.info("Calling DeepSeek model=%s message_count=%s", self.model, len(messages))
        try:
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise BusinessException(message="DeepSeek 调用失败", code="DEEPSEEK_CALL_FAILED", http_status=502) from exc

        content = completion.choices[0].message.content
        if not content:
            raise BusinessException(message="DeepSeek 返回内容为空", code="DEEPSEEK_EMPTY_RESPONSE", http_status=502)
        return content

    @staticmethod
    def _parse_json_model(content: str, model_type: type[Any]) -> Any:
        """解析模型 JSON 输出并做 Pydantic 结构校验。"""
        try:
            payload = json.loads(content)
            return model_type.model_validate(payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise BusinessException(message="DeepSeek 结构化输出解析失败", code="DEEPSEEK_PARSE_FAILED", http_status=502) from exc

