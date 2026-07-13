from enum import Enum
class WorkFlowToolType(str, Enum):

    WEATHER = "weather"

    MAP = "map"

    FILE = "file"

    SEARCH = "search"

    COMMON = "common"