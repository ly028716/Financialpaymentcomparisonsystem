"""
对比引擎测试
测试目标：付款申请与实际付款的对比算法
"""
import pytest
from decimal import Decimal


class TestComparisonEngine:
    """对比引擎核心测试"""

    def test_account_exact_match(self):
        """测试账号完全匹配"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = {'账号': '6222021234567890123'}
        actual = {'账号': '6222021234567890123'}

        result = engine.compare_account(expected['账号'], actual['账号'])

        assert result['match'] is True
        assert result['difference'] is None

    def test_account_mismatch(self):
        """测试账号不匹配"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = {'账号': '6222021234567890123'}
        actual = {'账号': '6222021234567890132'}  # 末位错误

        result = engine.compare_account(expected['账号'], actual['账号'])

        assert result['match'] is False
        assert result['severity'] == 'CRITICAL'

    def test_name_fuzzy_match_high_similarity(self):
        """测试户名模糊匹配（相似度>95%）"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        # 空格差异
        expected = '北京XX科技有限公司'
        actual = '北京 XX 科技有限公司'

        result = engine.compare_name(expected, actual)

        assert result['match'] is True  # 相似度应该>95%

    def test_name_fuzzy_match_low_similarity(self):
        """测试户名模糊匹配（相似度<95%）"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = '北京XX科技有限公司'
        actual = '北京YY科技公司'  # 完全不同的公司

        result = engine.compare_name(expected, actual)

        assert result['match'] is False
        assert result['severity'] == 'HIGH'
        assert result['similarity'] < 0.95

    def test_name_normalize_removes_suffix(self):
        """测试户名标准化去除常见后缀"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        # "有限公司"后缀应该被忽略
        expected = '北京XX科技有限公司'
        actual = '北京XX科技'

        result = engine.compare_name(expected, actual)

        # 去除后缀后应该匹配
        assert result['match'] is True

    def test_amount_exact_match(self):
        """测试金额精确匹配"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = Decimal('50000.00')
        actual = Decimal('50000.00')

        result = engine.compare_amount(expected, actual)

        assert result['match'] is True

    def test_amount_within_tolerance(self):
        """测试金额在误差范围内"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = Decimal('50000.00')
        actual = Decimal('50000.005')  # 差异<0.01

        result = engine.compare_amount(expected, actual)

        assert result['match'] is True  # 误差≤0.01元视为匹配

    def test_amount_exceeds_tolerance(self):
        """测试金额超出误差范围"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = Decimal('50000.00')
        actual = Decimal('50000.02')  # 差异>0.01

        result = engine.compare_amount(expected, actual)

        assert result['match'] is False
        assert result['severity'] == 'CRITICAL'
        assert result['difference'] == Decimal('0.02')

    def test_bank_keyword_match(self):
        """测试开户行关键词匹配"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = '中国工商银行北京分行'
        actual = '工商银行北京支行'

        result = engine.compare_bank(expected, actual)

        assert result['match'] is True  # "工商银行"关键词匹配

    def test_bank_keyword_mismatch(self):
        """测试开户行关键词不匹配"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = '中国工商银行北京分行'
        actual = '中国建设银行北京分行'

        result = engine.compare_bank(expected, actual)

        assert result['match'] is False
        assert result['severity'] == 'MEDIUM'


class TestFullComparison:
    """完整对比测试"""

    def test_full_match(self):
        """测试完全匹配的场景"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        application = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': '6222021234567890123',
            'payee_bank': '中国工商银行北京分行',
            'amount': Decimal('50000.00')
        }

        payment = {
            'actual_payee_name': '北京XX科技有限公司',
            'actual_payee_account': '6222021234567890123',
            'actual_payee_bank': '中国工商银行北京分行',
            'actual_amount': Decimal('50000.00')
        }

        result = engine.compare(application, payment)

        assert result['is_match'] is True
        assert len(result['differences']) == 0

    def test_multiple_differences(self):
        """测试多个差异项"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        application = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': '6222021234567890123',
            'payee_bank': '中国工商银行北京分行',
            'amount': Decimal('50000.00')
        }

        payment = {
            'actual_payee_name': '北京YY公司',
            'actual_payee_account': '6222021234567890456',
            'actual_payee_bank': '中国建设银行北京分行',
            'actual_amount': Decimal('5000.00')
        }

        result = engine.compare(application, payment)

        assert result['is_match'] is False
        assert len(result['differences']) >= 3  # 账号、户名、金额至少3个差异

        # 检查严重程度
        severities = [d['severity'] for d in result['differences']]
        assert 'CRITICAL' in severities  # 账号和金额错误

    def test_name_only_difference(self):
        """测试仅有户名差异（可接受的差异）"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        application = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': '6222021234567890123',
            'payee_bank': '中国工商银行北京分行',
            'amount': Decimal('50000.00')
        }

        payment = {
            'actual_payee_name': '北京XX科技公司',  # 少"有限"二字
            'actual_payee_account': '6222021234567890123',
            'actual_payee_bank': '中国工商银行北京分行',
            'actual_amount': Decimal('50000.00')
        }

        result = engine.compare(application, payment)

        # 户名相似度应该很高，但由于有差异，is_match可能为False
        assert len(result['differences']) == 1
        assert result['differences'][0]['field'] == '户名'


class TestEdgeCases:
    """边界条件测试"""

    def test_empty_account(self):
        """测试空账号"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        result = engine.compare_account('', '')

        assert result['match'] is True

    def test_zero_amount(self):
        """测试零金额"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        result = engine.compare_amount(Decimal('0'), Decimal('0'))

        assert result['match'] is True

    def test_large_amount(self):
        """测试大金额"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = Decimal('999999999.99')
        actual = Decimal('999999999.99')

        result = engine.compare_amount(expected, actual)

        assert result['match'] is True

    def test_special_characters_in_name(self):
        """测试户名中的特殊字符"""
        from payment_comparison.apps.comparison.engine import ComparisonEngine

        engine = ComparisonEngine()

        expected = '北京（XX）科技有限公司'
        actual = '北京(XX)科技有限公司'  # 中英文括号差异

        result = engine.compare_name(expected, actual)

        # 应该能处理括号差异
        assert result['match'] is True