"""
账号校验工具测试
测试目标：银行卡号Luhn算法校验
"""
import pytest


class TestLuhnAlgorithm:
    """Luhn算法测试"""

    def test_valid_bank_card(self):
        """测试有效的银行卡号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        # 有效的银行卡号（符合Luhn算法）
        valid_account = '6222021234567890123'

        result = validate_bank_account(valid_account)

        assert result['valid'] is True

    def test_invalid_bank_card(self):
        """测试无效的银行卡号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        # 无效的银行卡号（末位错误）
        invalid_account = '6222021234567890124'

        result = validate_bank_account(invalid_account)

        assert result['valid'] is False

    def test_empty_account(self):
        """测试空账号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        result = validate_bank_account('')

        assert result['valid'] is False
        assert 'empty' in result['message'].lower() or '空' in result['message']

    def test_account_with_spaces(self):
        """测试带空格的账号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        account_with_spaces = '6222 0212 3456 7890 123'

        result = validate_bank_account(account_with_spaces)

        assert result['valid'] is True  # 应该自动去除空格

    def test_account_too_short(self):
        """测试过短的账号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        short_account = '123456'

        result = validate_bank_account(short_account)

        assert result['valid'] is False

    def test_account_too_long(self):
        """测试过长的账号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        long_account = '1' * 25

        result = validate_bank_account(long_account)

        assert result['valid'] is False

    def test_account_with_letters(self):
        """测试包含字母的账号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        account_with_letters = '6222ABCD34567890123'

        result = validate_bank_account(account_with_letters)

        assert result['valid'] is False

    def test_luhn_checksum_calculation(self):
        """测试Luhn校验和计算"""
        from payment_comparison.apps.applications.utils import calculate_luhn_checksum

        # 已知校验和
        checksum = calculate_luhn_checksum('7992739871')

        # Luhn算法预期校验和为3（使得完整卡号79927398713有效）
        assert checksum == 3


class TestAccountFormat:
    """账号格式测试"""

    def test_format_with_masking(self):
        """测试账号脱敏显示"""
        from payment_comparison.apps.applications.utils import mask_account

        account = '6222021234567890123'

        masked = mask_account(account)

        # 应该只显示前4位和后4位
        assert masked.startswith('6222')
        assert masked.endswith('0123')
        assert '*' in masked

    def test_format_account_display(self):
        """测试账号显示格式化"""
        from payment_comparison.apps.applications.utils import format_account_display

        account = '6222021234567890123'

        formatted = format_account_display(account)

        # 应该按4位分组显示
        assert '6222' in formatted
        assert '0123' in formatted