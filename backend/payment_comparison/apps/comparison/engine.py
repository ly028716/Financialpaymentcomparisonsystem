"""
对比引擎核心算法
实现付款申请与实际付款的智能对比
"""
from decimal import Decimal
from difflib import SequenceMatcher
import re


class ComparisonEngine:
    """
    对比引擎

    对比会计申请表和出纳实际付款，发现差异并预警
    """

    # 金额误差阈值（元）
    AMOUNT_TOLERANCE = Decimal('0.01')

    # 户名相似度阈值
    NAME_SIMILARITY_THRESHOLD = 0.95

    # 银行关键词映射
    BANK_KEYWORDS = {
        '工商': ['工商', 'icbc'],
        '建设': ['建设', 'ccb'],
        '农业': ['农业', 'abc'],
        '中国银行': ['中国银行', '中行', 'boc'],
        '交通': ['交通', 'bcm'],
        '招商': ['招商', 'cmb'],
        '浦发': ['浦发', 'spdb'],
        '民生': ['民生', 'cmbc'],
        '兴业': ['兴业', 'cib'],
        '平安': ['平安', 'pab'],
        '光大': ['光大', 'ceb'],
        '华夏': ['华夏', 'hxb'],
        '中信': ['中信', 'citic'],
    }

    def compare(self, application, payment):
        """
        执行完整对比

        Args:
            application: 付款申请数据（dict）
            payment: 实际付款数据（dict）

        Returns:
            dict: 对比结果
        """
        result = {
            'is_match': True,
            'differences': []
        }

        # 1. 账号对比（完全匹配）
        account_result = self.compare_account(
            application.get('payee_account', ''),
            payment.get('actual_payee_account', '')
        )
        if not account_result['match']:
            result['is_match'] = False
            result['differences'].append({
                'field': '账号',
                'expected': application.get('payee_account'),
                'actual': payment.get('actual_payee_account'),
                'severity': account_result['severity'],
                'description': '账号不一致，属于严重错误'
            })

        # 2. 户名对比（模糊匹配）
        name_result = self.compare_name(
            application.get('payee_name', ''),
            payment.get('actual_payee_name', '')
        )
        if not name_result['match']:
            result['is_match'] = False
            result['differences'].append({
                'field': '户名',
                'expected': application.get('payee_name'),
                'actual': payment.get('actual_payee_name'),
                'similarity': name_result.get('similarity'),
                'severity': name_result['severity'],
                'description': f"户名相似度{name_result.get('similarity', 0)*100:.1f}%，低于95%阈值"
            })

        # 3. 金额对比（精确匹配，误差≤0.01元）
        amount_result = self.compare_amount(
            application.get('amount', Decimal('0')),
            payment.get('actual_amount', Decimal('0'))
        )
        if not amount_result['match']:
            result['is_match'] = False
            result['differences'].append({
                'field': '金额',
                'expected': str(application.get('amount')),
                'actual': str(payment.get('actual_amount')),
                'difference': str(amount_result.get('difference', Decimal('0'))),
                'severity': amount_result['severity'],
                'description': f"金额差异{amount_result.get('difference', Decimal('0'))}元"
            })

        # 4. 开户行对比（关键词匹配）
        bank_result = self.compare_bank(
            application.get('payee_bank', ''),
            payment.get('actual_payee_bank', '')
        )
        if not bank_result['match']:
            result['differences'].append({
                'field': '开户行',
                'expected': application.get('payee_bank'),
                'actual': payment.get('actual_payee_bank'),
                'severity': bank_result['severity'],
                'description': '开户行关键词不匹配'
            })

        return result

    def compare_account(self, expected, actual):
        """
        账号对比（完全匹配）

        Args:
            expected: 预期账号
            actual: 实际账号

        Returns:
            dict: 对比结果
        """
        # 去除空格
        expected_clean = str(expected).replace(' ', '')
        actual_clean = str(actual).replace(' ', '')

        if expected_clean == actual_clean:
            return {'match': True, 'difference': None}

        return {
            'match': False,
            'severity': 'CRITICAL',
            'difference': f"预期: {expected_clean}, 实际: {actual_clean}"
        }

    def compare_name(self, expected, actual):
        """
        户名对比（模糊匹配）

        Args:
            expected: 预期户名
            actual: 实际户名

        Returns:
            dict: 对比结果
        """
        # 标准化处理
        expected_normalized = self._normalize_name(expected)
        actual_normalized = self._normalize_name(actual)

        if expected_normalized == actual_normalized:
            return {'match': True, 'similarity': 1.0}

        # 计算相似度
        similarity = SequenceMatcher(
            None,
            expected_normalized,
            actual_normalized
        ).ratio()

        if similarity >= self.NAME_SIMILARITY_THRESHOLD:
            return {'match': True, 'similarity': similarity}

        return {
            'match': False,
            'similarity': similarity,
            'severity': 'HIGH'
        }

    def compare_amount(self, expected, actual):
        """
        金额对比（精确匹配，误差≤0.01元）

        Args:
            expected: 预期金额
            actual: 实际金额

        Returns:
            dict: 对比结果
        """
        expected_decimal = Decimal(str(expected))
        actual_decimal = Decimal(str(actual))

        difference = abs(expected_decimal - actual_decimal)

        if difference <= self.AMOUNT_TOLERANCE:
            return {'match': True, 'difference': Decimal('0')}

        return {
            'match': False,
            'severity': 'CRITICAL',
            'difference': actual_decimal - expected_decimal
        }

    def compare_bank(self, expected, actual):
        """
        开户行对比（关键词匹配）

        Args:
            expected: 预期开户行
            actual: 实际开户行

        Returns:
            dict: 对比结果
        """
        expected_keywords = self._extract_bank_keywords(expected)
        actual_keywords = self._extract_bank_keywords(actual)

        if not expected_keywords and not actual_keywords:
            return {'match': True}

        if expected_keywords & actual_keywords:
            return {'match': True}

        return {
            'match': False,
            'severity': 'MEDIUM'
        }

    def _normalize_name(self, name):
        """
        标准化户名

        - 去除空格
        - 去除常见后缀
        - 统一括号格式
        """
        if not name:
            return ''

        name = str(name)

        # 去除空格
        name = name.replace(' ', '')

        # 统一括号为英文括号
        name = name.replace('（', '(').replace('）', ')')

        # 去除常见后缀
        suffixes = [
            '有限责任公司',
            '有限公司',
            '股份有限公司',
            '股份公司',
            '公司'
        ]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break

        return name

    def _extract_bank_keywords(self, bank_name):
        """
        提取银行关键词

        Args:
            bank_name: 银行名称

        Returns:
            set: 关键词集合
        """
        if not bank_name:
            return set()

        bank_name = str(bank_name).lower()
        keywords = set()

        for bank, patterns in self.BANK_KEYWORDS.items():
            for pattern in patterns:
                if pattern in bank_name:
                    keywords.add(bank)
                    break

        return keywords


# 创建全局实例
comparison_engine = ComparisonEngine()


def compare_payment(application, payment):
    """
    便捷函数：对比付款

    Args:
        application: 付款申请
        payment: 实际付款

    Returns:
        dict: 对比结果
    """
    return comparison_engine.compare(application, payment)