"""企查查 MCP API 客户端 — MVP 阶段使用模拟数据."""

from __future__ import annotations

import copy
import random
from typing import Any

# ---------------------------------------------------------------------------
# 模拟数据源
# ---------------------------------------------------------------------------

_MOCK_COMPANIES: list[dict[str, Any]] = [
    {
        "company_name": "阿里巴巴集团控股有限公司",
        "unified_credit_code": "91330000706806620U",
        "registration_no": "330000000045678",
        "legal_rep": "蔡崇信",
        "company_status": "存续",
        "establish_date": "1999-04-04",
        "registered_capital": "2785297.18万元",
        "business_scope": "互联网软件和服务、国内贸易和物资供销业、投资",
        "address": "浙江省杭州市余杭区文一西路969号",
        "industry": "互联网和相关服务",
    },
    {
        "company_name": "腾讯科技（深圳）有限公司",
        "unified_credit_code": "91440300618815490Q",
        "registration_no": "440301503004052",
        "legal_rep": "马化腾",
        "company_status": "存续",
        "establish_date": "2000-02-24",
        "registered_capital": "60666.09万元",
        "business_scope": "计算机软、硬件及通讯产品",
        "address": "广东省深圳市南山区科技中一路腾讯大厦",
        "industry": "互联网和相关服务",
    },
    {
        "company_name": "北京字节跳动网络技术有限公司",
        "unified_credit_code": "91110108350011078D",
        "registration_no": "110108018083888",
        "legal_rep": "张利东",
        "company_status": "存续",
        "establish_date": "2015-01-09",
        "registered_capital": "35513.76万元",
        "business_scope": "技术研究与开发；技术咨询、技术服务、技术转让",
        "address": "北京市海淀区中关村南大街甲12号",
        "industry": "互联网和相关服务",
    },
]

_MOCK_SHAREHOLDERS: dict[str, list[dict[str, Any]]] = {
    "阿里巴巴集团控股有限公司": [
        {"name": "杭州阿里巴巴数字娱乐有限公司", "ratio": "60.0%", "amount": "1671178.31万元"},
        {"name": "DALI TECHNOLOGY PTY. LIMITED", "ratio": "35.5%", "amount": "988780.45万元"},
        {"name": "蔡崇信", "ratio": "2.5%", "amount": "69632.43万元"},
        {"name": "其他", "ratio": "2.0%", "amount": "55705.94万元"},
    ],
    "腾讯科技（深圳）有限公司": [
        {"name": "香港腾讯控股有限公司", "ratio": "88.0%", "amount": "53386.16万元"},
        {"name": "马化腾", "ratio": "6.0%", "amount": "3639.97万元"},
        {"name": "其他", "ratio": "6.0%", "amount": "3639.96万元"},
    ],
    "北京字节跳动网络技术有限公司": [
        {"name": "开曼字节跳动有限公司", "ratio": "75.0%", "amount": "26635.32万元"},
        {"name": "张一鸣", "ratio": "15.0%", "amount": "5327.06万元"},
        {"name": "梁汝波", "ratio": "5.0%", "amount": "1775.69万元"},
        {"name": "其他", "ratio": "5.0%", "amount": "1775.69万元"},
    ],
}

_MOCK_EXECUTIVES: dict[str, list[dict[str, Any]]] = {
    "阿里巴巴集团控股有限公司": [
        {"name": "蔡崇信", "title": "董事长", "start_date": "2023-09-10"},
        {"name": "吴泳铭", "title": "CEO", "start_date": "2023-09-10"},
        {"name": "童文红", "title": "董事会主席", "start_date": "2017-01-01"},
    ],
    "腾讯科技（深圳）有限公司": [
        {"name": "马化腾", "title": "董事局主席", "start_date": "2000-02-24"},
        {"name": "刘炽平", "title": "CEO", "start_date": "2009-12-17"},
        {"name": "程武", "title": "首席运营官", "start_date": "2014-01-01"},
    ],
    "北京字节跳动网络技术有限公司": [
        {"name": "张利东", "title": "法定代表人", "start_date": "2015-01-09"},
        {"name": "张一鸣", "title": "实际控制人", "start_date": "2012-03-01"},
        {"name": "梁汝波", "title": "副总裁", "start_date": "2015-06-01"},
    ],
}

_MOCK_INVESTMENTS: dict[str, list[dict[str, Any]]] = {
    "阿里巴巴集团控股有限公司": [
        {"company_name": "浙江淘宝网络有限公司", "ratio": "100.0%", "status": "存续"},
        {"company_name": "杭州阿里云技术有限公司", "ratio": "100.0%", "status": "存续"},
    ],
    "腾讯科技（深圳）有限公司": [
        {"company_name": "深圳市腾讯信息技术有限公司", "ratio": "100.0%", "status": "存续"},
    ],
    "北京字节跳动网络技术有限公司": [
        {"company_name": "北京微播视界科技有限公司", "ratio": "100.0%", "status": "存续"},
        {"company_name": "上海川陀因科技有限公司", "ratio": "80.0%", "status": "存续"},
    ],
}

_MOCK_RISKS: dict[str, dict[str, list[dict[str, Any]]]] = {
    "阿里巴巴集团控股有限公司": {
        "lawsuits": [
            {
                "case_no": "(2023)浙01民终1234号",
                "cause": "合同纠纷",
                "court": "杭州市中级人民法院",
                "role": "被告",
                "amount": "500万元",
                "date": "2023-06-15",
            },
        ],
        "dishonest": [],
        "restrictions": [],
        "penalties": [
            {
                "penalty_no": "杭市监处字〔2022〕123号",
                "reason": "不正当竞争",
                "amount": "100万元",
                "authority": "杭州市市场监督管理局",
                "date": "2022-08-20",
            },
        ],
    },
    "腾讯科技（深圳）有限公司": {
        "lawsuits": [],
        "dishonest": [],
        "restrictions": [],
        "penalties": [
            {
                "penalty_no": "深市监处字〔2021〕456号",
                "reason": "虚假宣传",
                "amount": "50万元",
                "authority": "深圳市市场监督管理局",
                "date": "2021-12-10",
            },
        ],
    },
    "北京字节跳动网络技术有限公司": {
        "lawsuits": [
            {
                "case_no": "(2023)京0105民初5678号",
                "cause": "名誉权纠纷",
                "court": "北京市海淀区人民法院",
                "role": "原告",
                "amount": "100万元",
                "date": "2023-03-22",
            },
        ],
        "dishonest": [],
        "restrictions": [],
        "penalties": [],
    },
}

_MOCK_FINANCIALS: dict[str, list[dict[str, Any]]] = {
    "阿里巴巴集团控股有限公司": [
        {
            "year": 2023,
            "total_assets": "29845.6亿元",
            "total_liabilities": "16789.2亿元",
            "net_assets": "13056.4亿元",
            "revenue": "8686.6亿元",
            "net_profit": "792.8亿元",
            "total_revenue": "8686.6亿元",
        },
        {
            "year": 2022,
            "total_assets": "27123.4亿元",
            "total_liabilities": "15234.1亿元",
            "net_assets": "11889.3亿元",
            "revenue": "8530.4亿元",
            "net_profit": "674.2亿元",
            "total_revenue": "8530.4亿元",
        },
    ],
    "腾讯科技（深圳）有限公司": [
        {
            "year": 2023,
            "total_assets": "12345.8亿元",
            "total_liabilities": "5678.9亿元",
            "net_assets": "6666.9亿元",
            "revenue": "6090.2亿元",
            "net_profit": "1577.0亿元",
            "total_revenue": "6090.2亿元",
        },
    ],
    "北京字节跳动网络技术有限公司": [
        {
            "year": 2023,
            "total_assets": "4567.2亿元",
            "total_liabilities": "1234.5亿元",
            "net_assets": "3332.7亿元",
            "revenue": "3500.0亿元",
            "net_profit": "500.0亿元",
            "total_revenue": "3500.0亿元",
        },
    ],
}

_MOCK_EQUITY_CHAIN: dict[str, dict[str, Any]] = {
    "阿里巴巴集团控股有限公司": {
        "company_name": "阿里巴巴集团控股有限公司",
        "chain_type": "向上穿透",
        "levels": [
            {"level": 0, "name": "阿里巴巴集团控股有限公司", "ratio": "100%"},
            {"level": 1, "name": "DALI TECHNOLOGY PTY. LIMITED", "ratio": "35.5%"},
            {"level": 2, "name": "蔡崇信", "ratio": "35.5%", "type": "自然人"},
        ],
    },
    "腾讯科技（深圳）有限公司": {
        "company_name": "腾讯科技（深圳）有限公司",
        "chain_type": "向上穿透",
        "levels": [
            {"level": 0, "name": "腾讯科技（深圳）有限公司", "ratio": "100%"},
            {"level": 1, "name": "香港腾讯控股有限公司", "ratio": "88.0%"},
            {"level": 2, "name": "马化腾", "ratio": "51.0%", "type": "自然人"},
        ],
    },
    "北京字节跳动网络技术有限公司": {
        "company_name": "北京字节跳动网络技术有限公司",
        "chain_type": "向上穿透",
        "levels": [
            {"level": 0, "name": "北京字节跳动网络技术有限公司", "ratio": "100%"},
            {"level": 1, "name": "开曼字节跳动有限公司", "ratio": "75.0%"},
            {"level": 2, "name": "张一鸣", "ratio": "60.0%", "type": "自然人"},
        ],
    },
}

_MOCK_CONTROLLERS: dict[str, dict[str, Any]] = {
    "阿里巴巴集团控股有限公司": {
        "name": "蔡崇信",
        "type": "自然人",
        "control_ratio": "35.5%",
        "control_path": "杭州阿里巴巴 → DALI TECHNOLOGY → 蔡崇信",
    },
    "腾讯科技（深圳）有限公司": {
        "name": "马化腾",
        "type": "自然人",
        "control_ratio": "51.0%",
        "control_path": "腾讯科技 → 香港腾讯控股 → 马化腾",
    },
    "北京字节跳动网络技术有限公司": {
        "name": "张一鸣",
        "type": "自然人",
        "control_ratio": "60.0%",
        "control_path": "字节跳动 → 开曼字节跳动 → 张一鸣",
    },
}

_MOCK_UBO: dict[str, list[dict[str, Any]]] = {
    "阿里巴巴集团控股有限公司": [
        {"name": "蔡崇信", "id_type": "身份证", "benefit_ratio": "35.5%", "benefit_type": "股权控制"},
    ],
    "腾讯科技（深圳）有限公司": [
        {"name": "马化腾", "id_type": "身份证", "benefit_ratio": "51.0%", "benefit_type": "股权控制"},
    ],
    "北京字节跳动网络技术有限公司": [
        {"name": "张一鸣", "id_type": "身份证", "benefit_ratio": "60.0%", "benefit_type": "股权控制"},
    ],
}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _fuzzy_match(keyword: str, items: list[str]) -> list[str]:
    """Return items whose name contains *keyword*, sorted by match quality."""
    matched = [name for name in items if keyword in name]
    unmatched = [name for name in items if keyword not in name]
    return matched + unmatched


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class QCCClient:
    """企查查 MCP API 客户端 — MVP 阶段使用模拟数据。

    在生产环境中应替换为调用企查查 MCP 工具的真实实现。
    """

    async def search_company(self, keyword: str) -> list[dict[str, Any]]:
        """模糊搜索企业，返回最多 5 个候选。"""
        company_names = [c["company_name"] for c in _MOCK_COMPANIES]
        matched_names = _fuzzy_match(keyword, company_names)
        results = []
        for name in matched_names[:5]:
            for c in _MOCK_COMPANIES:
                if c["company_name"] == name:
                    results.append(
                        {
                            "company_name": c["company_name"],
                            "unified_credit_code": c["unified_credit_code"],
                            "registration_no": c["registration_no"],
                            "legal_rep": c["legal_rep"],
                            "company_status": c["company_status"],
                        }
                    )
                    break
        return results

    async def get_company_info(
        self, company_name: str, credit_code: str | None = None
    ) -> dict[str, Any]:
        """企业基本信息。"""
        for c in _MOCK_COMPANIES:
            if company_name in c["company_name"] or (
                credit_code and credit_code == c["unified_credit_code"]
            ):
                return copy.deepcopy(c)
        raise ValueError(f"企业不存在: {company_name}")

    async def get_shareholders(self, company_name: str) -> list[dict[str, Any]]:
        """股东信息。"""
        for key in _MOCK_SHAREHOLDERS:
            if company_name in key:
                return copy.deepcopy(_MOCK_SHAREHOLDERS[key])
        return []

    async def get_executives(self, company_name: str) -> list[dict[str, Any]]:
        """高管信息。"""
        for key in _MOCK_EXECUTIVES:
            if company_name in key:
                return copy.deepcopy(_MOCK_EXECUTIVES[key])
        return []

    async def get_investments(self, company_name: str) -> list[dict[str, Any]]:
        """对外投资。"""
        for key in _MOCK_INVESTMENTS:
            if company_name in key:
                return copy.deepcopy(_MOCK_INVESTMENTS[key])
        return []

    async def get_risks(self, company_name: str) -> dict[str, list[dict[str, Any]]]:
        """风险汇总。"""
        for key in _MOCK_RISKS:
            if company_name in key:
                return copy.deepcopy(_MOCK_RISKS[key])
        return {"lawsuits": [], "dishonest": [], "restrictions": [], "penalties": []}

    async def get_financials(self, company_name: str) -> list[dict[str, Any]]:
        """工商财报数据。"""
        for key in _MOCK_FINANCIALS:
            if company_name in key:
                return copy.deepcopy(_MOCK_FINANCIALS[key])
        return []

    async def get_equity_chain(self, company_name: str) -> dict[str, Any]:
        """股权穿透路径。"""
        for key in _MOCK_EQUITY_CHAIN:
            if company_name in key:
                return copy.deepcopy(_MOCK_EQUITY_CHAIN[key])
        return {"company_name": company_name, "chain_type": "向上穿透", "levels": []}

    async def get_actual_controller(self, company_name: str) -> dict[str, Any]:
        """实际控制人。"""
        for key in _MOCK_CONTROLLERS:
            if company_name in key:
                return copy.deepcopy(_MOCK_CONTROLLERS[key])
        return {"name": None, "type": None, "control_ratio": None, "control_path": None}

    async def get_beneficial_owners(self, company_name: str) -> list[dict[str, Any]]:
        """受益所有人。"""
        for key in _MOCK_UBO:
            if company_name in key:
                return copy.deepcopy(_MOCK_UBO[key])
        return []


# Module-level singleton for convenience
qcc_client = QCCClient()
