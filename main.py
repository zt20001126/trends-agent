from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    # 根目录启动入口：让 `uvicorn main:app` 可以找到 backend/app 包。
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402

