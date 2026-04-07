"""
账号校验工具
实现银行卡号Luhn算法校验
"""


def validate_bank_account(account):
    """
    校验银行卡号有效性

    使用Luhn算法校验银行卡号格式

    Args:
        account: 银行卡号字符串

    Returns:
        dict: {
            'valid': bool,      # 是否有效
            'message': str,     # 提示信息
            'masked': str       # 脱敏显示
        }
    """
    if not account:
        return {
            'valid': False,
            'message': '账号不能为空',
            'masked': ''
        }

    # 去除空格
    account = str(account).replace(' ', '')

    # 检查是否全为数字
    if not account.isdigit():
        return {
            'valid': False,
            'message': '账号只能包含数字',
            'masked': account
        }

    # 检查长度（银行卡号通常为16-19位）
    if len(account) < 15:
        return {
            'valid': False,
            'message': '账号长度过短，应为15-19位',
            'masked': account
        }

    if len(account) > 19:
        return {
            'valid': False,
            'message': '账号长度过长，应为15-19位',
            'masked': account
        }

    # Luhn算法校验
    if not _luhn_check(account):
        return {
            'valid': False,
            'message': '账号校验失败，请检查账号是否正确',
            'masked': mask_account(account)
        }

    return {
        'valid': True,
        'message': '账号格式正确',
        'masked': mask_account(account)
    }


def _luhn_check(account):
    """
    Luhn算法校验

    Args:
        account: 银行卡号

    Returns:
        bool: 是否通过校验
    """
    digits = [int(d) for d in account]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    total = sum(odd_digits)

    for d in even_digits:
        doubled = d * 2
        if doubled > 9:
            doubled = doubled - 9
        total += doubled

    return total % 10 == 0


def calculate_luhn_checksum(partial_account):
    """
    计算Luhn校验位

    Args:
        partial_account: 不含校验位的账号

    Returns:
        int: 校验位（0-9）
    """
    digits = [int(d) for d in partial_account]

    # 在末尾添加一个0用于计算
    digits.append(0)

    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    total = sum(odd_digits)

    for d in even_digits:
        doubled = d * 2
        if doubled > 9:
            doubled = doubled - 9
        total += doubled

    checksum = (10 - (total % 10)) % 10

    return checksum


def mask_account(account, show_first=4, show_last=4):
    """
    账号脱敏显示

    Args:
        account: 银行卡号
        show_first: 显示前几位
        show_last: 显示后几位

    Returns:
        str: 脱敏后的账号
    """
    if not account:
        return ''

    account = str(account).replace(' ', '')

    if len(account) <= show_first + show_last:
        return account

    first = account[:show_first]
    last = account[-show_last:]
    middle = '*' * (len(account) - show_first - show_last)

    return f"{first}{middle}{last}"


def format_account_display(account, group_size=4):
    """
    格式化账号显示（按4位分组）

    Args:
        account: 银行卡号
        group_size: 分组大小

    Returns:
        str: 格式化后的账号
    """
    if not account:
        return ''

    account = str(account).replace(' ', '')

    groups = [account[i:i+group_size] for i in range(0, len(account), group_size)]

    return ' '.join(groups)


def get_bank_name_from_account(account):
    """
    根据账号识别银行（简化版）

    Args:
        account: 银行卡号

    Returns:
        str: 银行名称（未知则返回None）
    """
    if not account or len(account) < 6:
        return None

    # 常见银行卡号前缀
    bank_prefixes = {
        '622202': '中国工商银行',
        '622203': '中国工商银行',
        '622848': '中国农业银行',
        '622700': '中国建设银行',
        '621661': '中国银行',
        '622588': '招商银行',
        '622622': '中国民生银行',
        '622521': '兴业银行',
        '622155': '平安银行',
        '622580': '浦发银行',
    }

    prefix = account[:6]

    return bank_prefixes.get(prefix)