from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """系统配置类，集中管理应用、数据库、DeepSeek 和选品默认参数。

    运行说明：本类从环境变量或本地 .env 读取配置，禁止业务代码直接读取环境变量。
    """

    app_name: str = Field(default="trends-agent", description="应用名称")
    app_env: str = Field(default="development", description="应用运行环境")
    debug: bool = Field(default=True, description="是否开启调试模式")

    database_url: str = Field(
        default="postgresql+psycopg://trends_agent:trends_agent_dev_password@localhost:5432/trends_agent",
        description="PostgreSQL 数据库连接地址",
    )

    deepseek_api_key: str = Field(default="", description="DeepSeek API Key")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API 基础地址",
    )
    deepseek_model: str = Field(
        default="deepseek-v4-flash",
        description="DeepSeek 默认模型名称",
    )
    deepseek_timeout_seconds: int = Field(default=60, description="DeepSeek 请求超时时间")
    deepseek_temperature: float = Field(default=0.2, ge=0, le=2, description="DeepSeek 生成温度")
    deepseek_max_tokens: int = Field(default=3000, ge=256, description="DeepSeek 单次生成最大 token 数")
    deepseek_review_sample_limit: int = Field(default=50, ge=1, description="评论痛点总结的最大评论样本数")

    default_country: str = Field(default="US", description="默认分析站点国家代码")
    default_language: str = Field(default="zh-CN", description="默认用户语言")
    amazon_data_mode: str = Field(default="sample", description="Amazon 数据读取模式")
    google_trends_live: bool = Field(default=False, description="是否启用 pytrends 实时趋势获取")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """获取缓存后的系统配置，避免重复解析环境变量。"""
    return Settings()


settings = get_settings()
