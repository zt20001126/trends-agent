class BusinessException(Exception):
    """业务异常，用于表达可预期的业务失败。"""

    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_ERROR",
        http_status: int = 400,
    ) -> None:
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)

