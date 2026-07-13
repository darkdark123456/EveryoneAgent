"""
记忆规则配置 importance值越高，表示该类型的记忆越重要，在检索时优先考虑
"""


MEMORY_IMPORTANCE_RULERS_DICT: dict[str, int] = {

    # 用户身份
    "name": 10,
    "nickname": 10,
    "姓名": 10,

    # 职业
    "job": 9,
    "company": 9,
    "职业": 9,
    "公司": 9,

    # 项目
    "project": 8,
    "项目": 8,

    # 技术栈
    "skill": 7,
    "技术栈": 7,

    # 兴趣爱好
    "interest": 6,
    "兴趣爱好": 6,
    
    #生涯目标
    "career_goal": 5,
    "目标": 5,
    
    # 用户偏好
    "preference": 5,
    "偏好": 5,
    
    # 个人简介
    "profile": 10,

    # 临时
    "temporary": 1,
    
    # 默认
    "other": 1
}



class ImportanceScorer:

    SCORE_RULES = {

        "profile": 10,

        "project": 8,

        "preference": 6,

        "temporary": 2
    }

    @classmethod
    def score(
        cls,
        memory_type: str
    ) -> int:

        return cls.SCORE_RULES.get(
            memory_type,
            30
        )