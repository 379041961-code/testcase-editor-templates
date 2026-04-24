"""
数据验证模块
验证缺陷提交所需的所有信息
"""

import re
from typing import Dict, List, Tuple


class BugValidator:
    """缺陷信息验证"""
    
    REQUIRED_FIELDS = {
        'project_name': '项目名称',
        'title': '缺陷标题',
        'expected_result': '预期结果',
        'assignee_info': '负责人'
    }
    
    OPTIONAL_FIELDS = {
        'attachment_path': '附件路径'
    }
    
    VALID_PRIORITIES = ['P0', 'P1', 'P2', 'P3']
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    FIELD_CONSTRAINTS = {
        'title': {
            'min_length': 5,
            'max_length': 100,
            'description': '缺陷标题应在5-100字符之间'
        },
        'environment': {
            'valid_values': ['开发', '测试', '预发', '线上', 'DEV', 'TEST', 'UAT', 'PROD'],
            'description': '环境应为有效的环境名称'
        },
        'expected_result': {
            'min_length': 10,
            'description': '预期结果描述应至少10字符'
        },
        'actual_result': {
            'min_length': 10,
            'description': '实际结果描述应至少10字符'
        },
        'reproduction_steps': {
            'min_length': 10,
            'description': '重现步骤描述应至少10字符'
        },
        'frequency': {
            'valid_values': ['100%稳定复现', '90%以上', '50-90%', '50%以下', '稳定复现', '间歇性'],
            'description': '重现频率应为有效值'
        }
    }
    
    def validate(self, bug_info: Dict) -> Tuple[bool, List[str], Dict]:
        """完整验证缺陷信息
        
        Returns:
            (是否有效, 错误列表, 警告字典)
        """
        errors = []
        warnings = {}
        
        # 验证必填字段
        errors.extend(self._validate_required_fields(bug_info))
        
        # 验证具体字段值
        errors.extend(self._validate_field_values(bug_info))
        
        # 收集警告
        warnings = self._collect_warnings(bug_info)
        
        return len(errors) == 0, errors, warnings
    
    def _validate_required_fields(self, bug_info: Dict) -> List[str]:
        """验证必填字段"""
        errors = []
        
        for field, label in self.REQUIRED_FIELDS.items():
            value = bug_info.get(field, '').strip()
            if not value:
                errors.append(f"✗ 缺少必填项: {label}")
        
        return errors
    
    def _validate_field_values(self, bug_info: Dict) -> List[str]:
        """验证字段值的具体内容"""
        errors = []
        
        # 验证标题
        title = bug_info.get('title', '').strip()
        if title:
            if len(title) < 5:
                errors.append(f"✗ 缺陷标题过短 (最少5字符)")
            elif len(title) > 100:
                errors.append(f"✗ 缺陷标题过长 ({len(title)}/100字符)")
        
        # 验证负责人（邮箱或姓名）
        assignee_info = bug_info.get('assignee_info', '') or bug_info.get('assignee_email', '')
        assignee_info = assignee_info.strip()
        if assignee_info:
            # 检查是否是邮箱格式
            is_email = re.match(self.EMAIL_PATTERN, assignee_info)
            # 如果不是邮箱，假设它是姓名（允许中文）
            if not is_email and len(assignee_info) < 2:
                errors.append(f"✗ 负责人姓名过短，应至少2个字符")
        
        # 验证优先级
        priority = bug_info.get('priority', 'P2')
        if priority not in self.VALID_PRIORITIES:
            errors.append(f"✗ 优先级无效: {priority}，应为 {'/'.join(self.VALID_PRIORITIES)}")
        
        # 验证环境
        environment = bug_info.get('environment', '').strip()
        if environment:
            valid_envs = self.FIELD_CONSTRAINTS['environment']['valid_values']
            if environment not in valid_envs:
                errors.append(f"✗ 环境值无效: {environment}，应为 {'/'.join(valid_envs)}")
        
        # 验证重现频率
        frequency = bug_info.get('frequency', '')
        if frequency:
            valid_frequencies = self.FIELD_CONSTRAINTS['frequency']['valid_values']
            if frequency not in valid_frequencies:
                errors.append(f"✗ 重现频率无效: {frequency}")
        
        # 验证字段最小长度
        for field in ['expected_result', 'actual_result', 'reproduction_steps']:
            value = bug_info.get(field, '').strip()
            if value and len(value) < 10:
                errors.append(f"✗ {self.REQUIRED_FIELDS[field]}描述过短(最少10字符)")
        
        return errors
    
    def _collect_warnings(self, bug_info: Dict) -> Dict:
        """收集非致命警告"""
        warnings = {}
        
        # 检查是否提供了附件
        if not bug_info.get('attachment_path'):
            warnings['attachment'] = '⚠ 建议提供截图或记录，可加速问题解决'
        
        # 检查备注
        if not bug_info.get('notes'):
            warnings['notes'] = '⚠ 建议提供额外的背景信息或上下文'
        
        # 检查优先级和重现频率匹配度
        priority = bug_info.get('priority', 'P2')
        frequency = bug_info.get('frequency', '')
        
        if priority == 'P0' and frequency not in ['100%稳定复现', '稳定复现']:
            warnings['priority_frequency'] = '⚠ P0级别通常要求稳定复现'
        
        if priority == 'P1' and '稳定' not in frequency and frequency:
            warnings['priority_frequency'] = '⚠ P1级别建议选择高重现频率'
        
        return warnings
    
    def format_validation_report(self, bug_info: Dict) -> str:
        """生成验证报告"""
        is_valid, errors, warnings = self.validate(bug_info)
        
        report = "\n" + "="*60 + "\n"
        report += "缺陷信息验证报告\n"
        report += "="*60 + "\n"
        
        # 基本信息
        report += "\n【提交信息】\n"
        for field, label in self.REQUIRED_FIELDS.items():
            value = bug_info.get(field, '')[:50]  # 截断长值显示
            report += f"  {label}: {value}\n"
        
        # 验证结果
        if is_valid:
            report += "\n【验证结果】✓ 通过\n"
        else:
            report += "\n【验证结果】✗ 失败\n"
            report += "【错误信息】\n"
            for error in errors:
                report += f"  {error}\n"
        
        # 警告信息
        if warnings:
            report += "\n【警告信息】\n"
            for key, warning in warnings.items():
                report += f"  {warning}\n"
        
        report += "\n" + "="*60 + "\n"
        return report
    
    def get_field_hint(self, field_name: str) -> str:
        """获取字段的输入提示"""
        constraint = self.FIELD_CONSTRAINTS.get(field_name)
        if not constraint:
            return ""
        
        hints = []
        if 'min_length' in constraint:
            hints.append(f"最少{constraint['min_length']}字符")
        if 'max_length' in constraint:
            hints.append(f"最多{constraint['max_length']}字符")
        if 'valid_values' in constraint:
            hints.append(f"有效值: {', '.join(constraint['valid_values'])}")
        if 'description' in constraint:
            hints.append(constraint['description'])
        
        return "; ".join(hints)


def main():
    """测试验证功能"""
    validator = BugValidator()
    
    # 测试用例1: 完整有效的缺陷信息
    print("测试1: 有效的缺陷信息")
    valid_bug = {
        'title': '登录页面验证码无法正确显示',
        'environment': '测试',
        'expected_result': '验证码应显示清晰的数字和字母组合',
        'actual_result': '验证码显示为黑色方块，无法识别',
        'reproduction_steps': '1. 打开登录页面\n2. 查看验证码区域',
        'assignee_email': 'user@example.com',
        'priority': 'P1',
        'frequency': '100%稳定复现',
    }
    report = validator.format_validation_report(valid_bug)
    print(report)
    
    # 测试用例2: 缺少必填字段
    print("\n测试2: 缺少必填字段")
    invalid_bug = {
        'title': '缺陷',
        'environment': '测试',
    }
    report = validator.format_validation_report(invalid_bug)
    print(report)
    
    # 测试用例3: 字段值不合法
    print("\n测试3: 字段值不合法")
    invalid_value_bug = {
        'title': '缺陷',
        'environment': '无效环境',
        'expected_result': '预期',
        'actual_result': '实际',
        'reproduction_steps': '步骤',
        'assignee_email': 'invalid-email',
        'priority': 'P5'
    }
    report = validator.format_validation_report(invalid_value_bug)
    print(report)


if __name__ == "__main__":
    main()
