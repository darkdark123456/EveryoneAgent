"""
初始化数据库
"""
from pathlib import Path
import sys
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))


from Infrastructure.Storage.database import (
    engine
)

from Infrastructure.Storage.models import (
    Base
)


def init_database() -> None:
    """
    创建所有表
    """

    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":
    init_database()


    print(
        "数据库初始化完成"
    )


    import sys
    print(sys.executable)
    print(sys.prefix)