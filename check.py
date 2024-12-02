import re

def validate_regex(pattern):
    try:
        re.compile(pattern)
        print("正则表达式合法")
        return True
    except re.error as e:
        print(f"正则表达式不合法: {e}")
        return False

