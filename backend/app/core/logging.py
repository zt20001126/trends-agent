import logging
import sys


def configure_logging() -> None:
    """配置应用基础日志，影响 FastAPI、Service、Repository 和 AI 调用边界。

    运维说明：当前 MVP 使用标准输出，后续可替换为结构化 JSON 日志或接入集中日志系统。
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

