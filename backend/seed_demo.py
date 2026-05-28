"""种子脚本：创建完整的模拟尽调案例数据。

用法:
    cd backend
    env/Scripts/python seed_demo.py

会在数据库中创建 5 个不同状态的尽调任务，每个任务关联完整的企业信息、
风险、财务、股权、评分、报告、征信、银行流水、上传财报等数据。
"""

import asyncio
import json
import uuid
from datetime import datetime, date, timezone

from sqlalchemy import select
from passlib.context import CryptContext

from database import AsyncSessionLocal, create_tables, engine
from models import (
    Base,
    User,
    UserRole,
    Task,
    TaskStatus,
    Company,
    CompanyShareholder,
    CompanyExecutive,
    CompanyInvestment,
    CompanyRisk,
    RiskType,
    RiskLevel,
    CompanyFinancial,
    EquityChain,
    ChainType,
    RatingRecord,
    Grade,
    ReportSnapshot,
    LegalPersonCredit,
    EnterpriseCredit,
    PersonIdType,
    CreditSource,
    CreditRating,
    BankStatement,
    StatementSource,
    BankStatementParseStatus,
    UploadedFinancialReport,
    ReportType,
    FileSource,
    ParseStatus,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── 固定 admin 用户 ID（与 seed_admin.py 一致） ─────────────────────────
ADMIN_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# ── 案例定义 ──────────────────────────────────────────────────────────────

CASES = [
    {
        "task_no": "DD-20260501-0001",
        "company_name": "深圳中科智芯科技有限公司",
        "unified_credit_code": "91440300MA5EKXJT2A",
        "status": TaskStatus.COMPLETED,
        "progress": 100.0,
        "remark": "某银行科技贷授信尽调，企业整体资质良好，建议授信。",
        "legal_rep": "张文远",
        "registered_capital": "5000万元人民币",
        "est_date": datetime(2018, 6, 15),
        "company_status": "在营",
        "business_scope": "计算机软硬件技术开发；集成电路设计；人工智能算法研发；电子产品销售。",
        "address": "广东省深圳市南山区科技园南区高新大厦12层",
        "industry_info": {"primary": "科技推广和应用服务业", "secondary": "集成电路设计"},
        "grade": Grade.A,
        "total_score": 92.5,
        "judicial_score": 95,
        "financial_score": 90,
        "credit_score": 93,
        "operation_score": 91,
        "equity_score": 94,
        "compliance_score": 92,
        "high_risk_count": 0,
        "has_credit": True,
        "has_bank_statement": True,
        "has_financial_report": True,
    },
    {
        "task_no": "DD-20260505-0002",
        "company_name": "杭州绿源农业发展有限公司",
        "unified_credit_code": "91330100MA28HXPQ3B",
        "status": TaskStatus.COMPLETED,
        "progress": 100.0,
        "remark": "供应链金融授信尽调，农业龙头企业，存在少量行政处罚。",
        "legal_rep": "李桂花",
        "registered_capital": "8000万元人民币",
        "est_date": datetime(2015, 3, 20),
        "company_status": "在营",
        "business_scope": "农产品种植与加工；农业技术开发；农产品进出口贸易；冷链物流服务。",
        "address": "浙江省杭州市余杭区未来科技城E园区8栋",
        "industry_info": {"primary": "农、林、牧、渔业", "secondary": "农产品加工"},
        "grade": Grade.B,
        "total_score": 76.0,
        "judicial_score": 70,
        "financial_score": 78,
        "credit_score": 75,
        "operation_score": 80,
        "equity_score": 74,
        "compliance_score": 73,
        "high_risk_count": 0,
        "has_credit": True,
        "has_bank_statement": True,
        "has_financial_report": True,
    },
    {
        "task_no": "DD-20260510-0003",
        "company_name": "北京鑫海达贸易有限公司",
        "unified_credit_code": "91110108MA01XKT74C",
        "status": TaskStatus.RUNNING,
        "progress": 65.0,
        "remark": "流动资金贷款尽调，贸易类企业，正在补充银行流水数据。",
        "legal_rep": "王志强",
        "registered_capital": "3000万元人民币",
        "est_date": datetime(2020, 11, 8),
        "company_status": "在营",
        "business_scope": "国内贸易；进出口代理；建筑材料销售；机械设备租赁。",
        "address": "北京市朝阳区CBD国贸大厦27层",
        "industry_info": {"primary": "批发和零售业", "secondary": "贸易代理"},
        "grade": None,
        "total_score": None,
        "judicial_score": None,
        "financial_score": None,
        "credit_score": None,
        "operation_score": None,
        "equity_score": None,
        "compliance_score": None,
        "high_risk_count": 1,
        "has_credit": False,
        "has_bank_statement": False,
        "has_financial_report": True,
    },
    {
        "task_no": "DD-20260515-0004",
        "company_name": "上海云图数据服务有限公司",
        "unified_credit_code": "91310115MA1K3RW85D",
        "status": TaskStatus.PENDING,
        "progress": 10.0,
        "remark": "新接任务，待启动尽调流程。",
        "legal_rep": "陈思雨",
        "registered_capital": "2000万元人民币",
        "est_date": datetime(2022, 1, 10),
        "company_status": "在营",
        "business_scope": "大数据分析服务；云计算技术服务；企业数字化转型咨询；软件系统集成。",
        "address": "上海市浦东新区张江高科技园区博云路99号",
        "industry_info": {"primary": "信息技术服务业", "secondary": "大数据服务"},
        "grade": None,
        "total_score": None,
        "judicial_score": None,
        "financial_score": None,
        "credit_score": None,
        "operation_score": None,
        "equity_score": None,
        "compliance_score": None,
        "high_risk_count": 0,
        "has_credit": False,
        "has_bank_statement": False,
        "has_financial_report": False,
    },
    {
        "task_no": "DD-20260520-0005",
        "company_name": "成都宏远机械制造有限公司",
        "unified_credit_code": "91510100MA6C2NP96E",
        "status": TaskStatus.FAILED,
        "progress": 40.0,
        "remark": "尽调失败：企业存在多起未结诉讼及失信记录，建议拒绝授信。",
        "legal_rep": "赵大伟",
        "registered_capital": "6000万元人民币",
        "est_date": datetime(2016, 9, 5),
        "company_status": "在营",
        "business_scope": "机械制造与加工；汽车零部件生产；自动化设备研发；工业物联网解决方案。",
        "address": "四川省成都市高新区天府软件园D区5栋",
        "industry_info": {"primary": "制造业", "secondary": "机械装备制造"},
        "grade": Grade.D,
        "total_score": 35.0,
        "judicial_score": 20,
        "financial_score": 40,
        "credit_score": 30,
        "operation_score": 38,
        "equity_score": 42,
        "compliance_score": 25,
        "high_risk_count": 4,
        "has_credit": True,
        "has_bank_statement": True,
        "has_financial_report": True,
    },
]

# ── 辅助函数：生成丰富的子数据 ─────────────────────────────────────────────


def make_shareholders(company_id: uuid.UUID, case_idx: int):
    """为不同案例生成不同的股东数据。"""
    templates = [
        # Case 0: 中科智芯 - 典型科技公司股权
        [
            ("中科创业投资基金(深圳)合伙企业", "法人股东", 35.0, "1750万元", "1750万元", 0.0),
            ("张文远", "自然人股东", 30.0, "1500万元", "1500万元", 0.0),
            ("深圳智芯员工持股平台", "合伙企业", 15.0, "750万元", "750万元", 0.0),
            ("华为技术有限公司", "法人股东", 12.0, "600万元", "600万元", 0.0),
            ("刘明", "自然人股东", 8.0, "400万元", "200万元", 0.0),
        ],
        # Case 1: 绿源农业 - 家族控股
        [
            ("李桂花", "自然人股东", 45.0, "3600万元", "3600万元", 0.0),
            ("李明辉", "自然人股东", 25.0, "2000万元", "2000万元", 5.0),
            ("杭州浙商农业集团", "法人股东", 20.0, "1600万元", "1600万元", 0.0),
            ("杭州绿源员工持股会", "合伙企业", 10.0, "800万元", "400万元", 0.0),
        ],
        # Case 2: 鑫海达贸易
        [
            ("王志强", "自然人股东", 55.0, "1650万元", "800万元", 0.0),
            ("北京中诚信投资有限公司", "法人股东", 30.0, "900万元", "900万元", 0.0),
            ("赵磊", "自然人股东", 15.0, "450万元", "100万元", 12.0),
        ],
        # Case 3: 云图数据
        [
            ("陈思雨", "自然人股东", 40.0, "800万元", "800万元", 0.0),
            ("上海张江科创基金", "法人股东", 30.0, "600万元", "600万元", 0.0),
            ("阿里巴巴集团投资有限公司", "法人股东", 20.0, "400万元", "400万元", 0.0),
            ("上海云图员工持股平台", "合伙企业", 10.0, "200万元", "200万元", 0.0),
        ],
        # Case 4: 宏远机械
        [
            ("赵大伟", "自然人股东", 50.0, "3000万元", "1500万元", 20.0),
            ("成都高新投集团", "法人股东", 20.0, "1200万元", "1200万元", 0.0),
            ("四川天府产业基金", "法人股东", 15.0, "900万元", "900万元", 0.0),
            ("宏远机械员工持股会", "合伙企业", 10.0, "600万元", "300万元", 0.0),
            ("吴强", "自然人股东", 5.0, "300万元", "100万元", 8.0),
        ],
    ]
    rows = templates[case_idx]
    results = []
    for name, stype, ratio, subscribe, paid, pledge in rows:
        results.append(
            CompanyShareholder(
                company_id=company_id,
                shareholder_name=name,
                shareholder_type=stype,
                share_ratio=ratio,
                subscribe_capital=subscribe,
                paid_in_capital=paid,
                pledge_ratio=pledge,
            )
        )
    return results


def make_executives(company_id: uuid.UUID, case_idx: int, legal_rep: str):
    templates = [
        [("张文远", "法定代表人/董事长"), ("刘畅", "总经理"), ("周慧", "财务总监"), ("王杰", "技术总监")],
        [("李桂花", "法定代表人/执行董事"), ("李明辉", "副总经理"), ("黄丽", "财务负责人")],
        [("王志强", "法定代表人/总经理"), ("孙丽", "副总经理"), ("马强", "销售总监")],
        [("陈思雨", "法定代表人/CEO"), ("林涛", "CTO"), ("王晓萌", "CFO"), ("杨凯", "运营总监")],
        [("赵大伟", "法定代表人/董事长"), ("吴强", "总经理"), ("何芳", "财务总监"), ("刘斌", "生产总监")],
    ]
    rows = templates[case_idx]
    return [
        CompanyExecutive(company_id=company_id, name=name, position=position)
        for name, position in rows
    ]


def make_investments(company_id: uuid.UUID, case_idx: int):
    templates = [
        [("深圳中科算法实验室", 100.0, "500万元", datetime(2021, 3, 1), "在营")],
        [("杭州绿源冷链物流", 60.0, "1200万元", datetime(2019, 7, 1), "在营"), ("安徽绿源种植合作社", 40.0, "600万元", datetime(2020, 2, 1), "在营")],
        [("北京鑫海建材市场运营", 80.0, "300万元", datetime(2022, 5, 1), "在营")],
        [("上海云图AI研究院", 100.0, "400万元", datetime(2023, 1, 1), "在营")],
        [("成都宏远汽车零部件", 70.0, "2000万元", datetime(2018, 4, 1), "在营"), ("绵阳宏远新能源科技", 35.0, "800万元", datetime(2020, 9, 1), "吊销")],
    ]
    rows = templates[case_idx]
    return [
        CompanyInvestment(
            company_id=company_id,
            invested_company=name,
            invest_ratio=ratio,
            invest_amount=amount,
            invest_date=d,
            status=s,
        )
        for name, ratio, amount, d, s in rows
    ]


def make_risks(company_id: uuid.UUID, case_idx: int, high_risk_count: int):
    if case_idx == 0:
        # 中科智芯：低风险
        return [
            CompanyRisk(
                company_id=company_id,
                risk_type=RiskType.PLEDGE,
                risk_level=RiskLevel.LOW,
                risk_detail={"title": "股权质押", "description": "股东股权质押已解除", "amount": "200万元", "date": "2024-06-15"},
            )
        ]
    if case_idx == 1:
        # 绿源农业：中风险行政处罚
        return [
            CompanyRisk(
                company_id=company_id,
                risk_type=RiskType.PENALTY,
                risk_level=RiskLevel.MEDIUM,
                risk_detail={"title": "环保行政处罚", "description": "废水处理不达标", "amount": "5万元", "date": "2024-03-10", "agency": "余杭区环保局"},
            ),
            CompanyRisk(
                company_id=company_id,
                risk_type=RiskType.ABNORMAL,
                risk_level=RiskLevel.LOW,
                risk_detail={"title": "经营异常", "description": "未按时报送年报", "date": "2023-07-01", "resolved": "已移出"},
            ),
        ]
    if case_idx == 2:
        # 鑫海达贸易：1个高风险
        return [
            CompanyRisk(
                company_id=company_id,
                risk_type=RiskType.LAWSUIT,
                risk_level=RiskLevel.HIGH,
                risk_detail={"title": "合同纠纷", "description": "与供应商的货款纠纷", "amount": "180万元", "court": "北京朝阳区法院", "date": "2025-11-20", "status": "一审中"},
            ),
            CompanyRisk(
                company_id=company_id,
                risk_type=RiskType.TAX_ABNORMAL,
                risk_level=RiskLevel.LOW,
                risk_detail={"title": "税务异常", "description": "发票开具不规范", "date": "2025-05-12", "resolved": "已整改"},
            ),
        ]
    if case_idx == 3:
        # 云图数据：无风险
        return []
    # case_idx == 4: 宏远机械：多高风险
    return [
        CompanyRisk(
            company_id=company_id,
            risk_type=RiskType.LAWSUIT,
            risk_level=RiskLevel.HIGH,
            risk_detail={"title": "买卖合同纠纷", "description": "拖欠供应商货款", "amount": "320万元", "court": "成都市武侯区法院", "date": "2025-06-10", "status": "未结案"},
        ),
        CompanyRisk(
            company_id=company_id,
            risk_type=RiskType.LAWSUIT,
            risk_level=RiskLevel.HIGH,
            risk_detail={"title": "劳动争议", "description": "拖欠员工工资", "amount": "50万元", "court": "成都市劳动仲裁委", "date": "2025-09-01", "status": "调解中"},
        ),
        CompanyRisk(
            company_id=company_id,
            risk_type=RiskType.DISHONEST,
            risk_level=RiskLevel.HIGH,
            risk_detail={"title": "失信被执行人", "description": "未按判决履行还款义务", "amount": "500万元", "court": "四川省成都市中级人民法院", "date": "2026-01-15"},
        ),
        CompanyRisk(
            company_id=company_id,
            risk_type=RiskType.RESTRICTION,
            risk_level=RiskLevel.HIGH,
            risk_detail={"title": "限制高消费", "description": "法人赵大伟被限高", "court": "四川省成都市中级人民法院", "date": "2026-01-20"},
        ),
        CompanyRisk(
            company_id=company_id,
            risk_type=RiskType.PENALTY,
            risk_level=RiskLevel.MEDIUM,
            risk_detail={"title": "安全生产处罚", "description": "工厂安全事故", "amount": "20万元", "date": "2025-08-10", "agency": "成都市应急管理局"},
        ),
    ]


def make_financials(company_id: uuid.UUID, case_idx: int):
    """生成2-3年的工商财报数据。"""
    fin_data = [
        # Case 0: 中科智芯 - 增长良好的科技企业
        [
            (2024, 8500.0, 1200.0, 3200.0, 980.0, 1100.0),
            (2023, 6200.0, 800.0, 2400.0, 680.0, 750.0),
            (2022, 4100.0, 500.0, 1600.0, 420.0, 480.0),
        ],
        # Case 1: 绿源农业 - 稳定但增速慢
        [
            (2024, 15000.0, 4500.0, 8000.0, 1200.0, 1500.0),
            (2023, 14200.0, 4200.0, 7500.0, 1100.0, 1350.0),
            (2022, 13500.0, 4000.0, 7000.0, 980.0, 1200.0),
        ],
        # Case 2: 鑫海达贸易 - 波动较大
        [
            (2024, 6000.0, 3500.0, 12000.0, 400.0, 350.0),
            (2023, 5500.0, 3200.0, 11000.0, 520.0, 600.0),
        ],
        # Case 4: 宏远机械 - 经营下滑
        [
            (2024, 12000.0, 8000.0, 7000.0, -200.0, -500.0),
            (2023, 13500.0, 7000.0, 9000.0, 300.0, 200.0),
            (2022, 14000.0, 6000.0, 11000.0, 600.0, 800.0),
        ],
    ]
    if case_idx == 3:
        # 云图数据：无财报数据（待尽调）
        return []
    valid_indices = (0, 1, 2, 4)
    data = fin_data[valid_indices.index(case_idx)]
    results = []
    for year, assets, liabilities, revenue, net_profit, cash_flow in data:
        results.append(
            CompanyFinancial(
                company_id=company_id,
                year=year,
                balance_sheet={
                    "total_assets": assets,
                    "total_liabilities": liabilities,
                    "owner_equity": assets - liabilities,
                    "fixed_assets": assets * 0.3,
                    "current_assets": assets * 0.5,
                    "current_liabilities": liabilities * 0.6,
                },
                income_statement={
                    "revenue": revenue,
                    "gross_profit": revenue * 0.35,
                    "operating_profit": revenue * 0.15,
                    "net_profit": net_profit,
                    "net_profit_margin": round(net_profit / revenue * 100, 2) if revenue else 0,
                },
                cash_flow={
                    "operating_cash_flow": cash_flow,
                    "investing_cash_flow": -assets * 0.05,
                    "financing_cash_flow": -liabilities * 0.1,
                    "net_cash_flow": cash_flow * 0.6,
                },
                key_indicators={
                    "roe": round(net_profit / (assets - liabilities) * 100, 2) if assets > liabilities else 0,
                    "roa": round(net_profit / assets * 100, 2) if assets else 0,
                    "current_ratio": round(
                        (assets * 0.5) / (liabilities * 0.6), 2
                    ) if liabilities else 0,
                    "asset_liability_ratio": round(liabilities / assets * 100, 2) if assets else 0,
                },
            )
        )
    return results


def make_equity_chains(company_id: uuid.UUID, case_idx: int):
    templates = [
        {
            "upward": {
                "depth": 3,
                "chain": [
                    {"level": 1, "name": "中科创业投资基金", "ratio": 35.0, "type": "法人"},
                    {"level": 2, "name": "深创投集团", "ratio": 60.0, "type": "法人"},
                    {"level": 3, "name": "深圳市人民政府国资委", "ratio": 100.0, "type": "国资"},
                ],
            },
            "ubo": {
                "depth": 2,
                "chain": [
                    {"level": 1, "name": "张文远", "ratio": 30.0, "type": "自然人"},
                    {"level": 2, "name": "深圳市人民政府国资委（通过深创投集团→中科创投）", "ratio": 21.0, "type": "国资"},
                ],
            },
        },
        {
            "upward": {
                "depth": 2,
                "chain": [
                    {"level": 1, "name": "杭州浙商农业集团", "ratio": 20.0, "type": "法人"},
                    {"level": 2, "name": "浙商控股集团", "ratio": 80.0, "type": "法人"},
                ],
            },
            "ubo": {
                "depth": 1,
                "chain": [
                    {"level": 1, "name": "李桂花", "ratio": 45.0, "type": "自然人"},
                ],
            },
        },
        {
            "upward": {
                "depth": 2,
                "chain": [
                    {"level": 1, "name": "北京中诚信投资有限公司", "ratio": 30.0, "type": "法人"},
                    {"level": 2, "name": "中诚信集团", "ratio": 100.0, "type": "法人"},
                ],
            },
            "ubo": {
                "depth": 1,
                "chain": [
                    {"level": 1, "name": "王志强", "ratio": 55.0, "type": "自然人"},
                ],
            },
        },
        {
            "upward": {
                "depth": 3,
                "chain": [
                    {"level": 1, "name": "阿里巴巴集团投资", "ratio": 20.0, "type": "法人"},
                    {"level": 2, "name": "阿里巴巴集团控股", "ratio": 100.0, "type": "法人"},
                    {"level": 3, "name": "马云等创始团队", "ratio": 8.8, "type": "自然人"},
                ],
            },
            "ubo": {
                "depth": 1,
                "chain": [
                    {"level": 1, "name": "陈思雨", "ratio": 40.0, "type": "自然人"},
                ],
            },
        },
        {
            "upward": {
                "depth": 2,
                "chain": [
                    {"level": 1, "name": "成都高新投集团", "ratio": 20.0, "type": "法人"},
                    {"level": 2, "name": "成都高新区管委会", "ratio": 100.0, "type": "国资"},
                ],
            },
            "ubo": {
                "depth": 1,
                "chain": [
                    {"level": 1, "name": "赵大伟", "ratio": 50.0, "type": "自然人"},
                ],
            },
        },
    ]
    tpl = templates[case_idx]
    results = []
    for chain_type_str, data in tpl.items():
        results.append(
            EquityChain(
                company_id=company_id,
                chain_type=ChainType(chain_type_str),
                chain_depth=data["depth"],
                chain_data={"chain": data["chain"]},
            )
        )
    return results


def make_legal_person_credit(company_id: uuid.UUID, case_idx: int, admin_id: uuid.UUID, legal_rep: str):
    credit_data = [
        # Case 0: 良好征信
        {
            "credit_rating": CreditRating.GOOD,
            "loan_accounts": {"total": 2, "details": [{"bank": "招商银行深圳分行", "type": "科技贷", "amount": 500.0, "status": "正常"}, {"bank": "微众银行", "type": "微业贷", "amount": 100.0, "status": "正常"}]},
            "credit_card_accounts": {"total": 2, "details": [{"bank": "招商银行", "limit": 10.0, "used": 3.0}, {"bank": "工商银行", "limit": 5.0, "used": 1.0}]},
            "overdue_records": None,
            "default_records": None,
        },
        # Case 1: 一般征信
        {
            "credit_rating": CreditRating.FAIR,
            "loan_accounts": {"total": 3, "details": [{"bank": "农业银行杭州分行", "type": "农户贷", "amount": 800.0, "status": "正常"}, {"bank": "建设银行", "type": "流动资金贷款", "amount": 500.0, "status": "正常"}, {"bank": "邮储银行", "type": "农业补贴贷", "amount": 200.0, "status": "关注"}]},
            "credit_card_accounts": {"total": 1, "details": [{"bank": "农业银行", "limit": 5.0, "used": 4.2}]},
            "overdue_records": {"count": 2, "details": [{"date": "2025-03", "amount": 2.0, "days": 15}, {"date": "2024-11", "amount": 1.5, "days": 8}]},
            "default_records": None,
        },
        # Case 4: 不良征信
        {
            "credit_rating": CreditRating.POOR,
            "loan_accounts": {"total": 5, "details": [{"bank": "工商银行成都分行", "type": "流动资金贷款", "amount": 1000.0, "status": "逾期"}, {"bank": "建设银行", "type": "固定资产贷款", "amount": 800.0, "status": "关注"}, {"bank": "浦发银行", "type": "信用贷", "amount": 300.0, "status": "逾期"}, {"bank": "农村信用社", "type": "小额贷", "amount": 100.0, "status": "正常"}, {"bank": "小贷公司", "type": "现金贷", "amount": 50.0, "status": "逾期"}]},
            "credit_card_accounts": {"total": 3, "details": [{"bank": "工商银行", "limit": 5.0, "used": 5.0}, {"bank": "建设银行", "limit": 3.0, "used": 3.0}, {"bank": "招商银行", "limit": 8.0, "used": 7.5}]},
            "overdue_records": {"count": 8, "details": [{"date": "2026-01", "amount": 15.0, "days": 45}, {"date": "2025-12", "amount": 12.0, "days": 30}, {"date": "2025-10", "amount": 8.0, "days": 60}]},
            "default_records": {"count": 2, "details": [{"date": "2026-01", "amount": 500.0, "type": "法院判决违约"}, {"date": "2025-08", "amount": 200.0, "type": "贷款违约"}]},
        },
    ]
    if case_idx not in (0, 1, 4):
        return None
    data = credit_data[list((0, 1, 4)).index(case_idx)]
    return LegalPersonCredit(
        company_id=company_id,
        person_name=legal_rep,
        person_id_type=PersonIdType.ID_CARD,
        person_id_no="11010119800101" + f"{case_idx:04d}",
        credit_source=CreditSource.MANUAL,
        credit_rating=data["credit_rating"],
        loan_accounts=data["loan_accounts"],
        credit_card_accounts=data["credit_card_accounts"],
        guarantee_info={"total_guarantee_amount": 0.0, "details": []},
        overdue_records=data["overdue_records"],
        default_records=data["default_records"],
        entered_by=admin_id,
    )


def make_enterprise_credit(company_id: uuid.UUID, case_idx: int, admin_id: uuid.UUID):
    credit_data = [
        # Case 0
        {
            "total_credit_line": 2000.0,
            "used_credit_line": 600.0,
            "remaining_credit_line": 1400.0,
            "loan_details": {"total": 3, "banks": [{"bank": "招商银行", "amount": 500.0, "type": "信用贷"}, {"bank": "微众银行", "amount": 100.0, "type": "微业贷"}]},
            "guarantee_out": {"total": 0.0},
            "overdue_info": None,
            "multi_lending_flag": False,
            "lender_count": 2,
        },
        # Case 1
        {
            "total_credit_line": 3000.0,
            "used_credit_line": 2200.0,
            "remaining_credit_line": 800.0,
            "loan_details": {"total": 4, "banks": [{"bank": "农业银行", "amount": 800.0, "type": "农户贷"}, {"bank": "建设银行", "amount": 500.0, "type": "流贷"}, {"bank": "邮储银行", "amount": 300.0, "type": "补贴贷"}, {"bank": "农商行", "amount": 600.0, "type": "涉农贷"}]},
            "guarantee_out": {"total": 500.0, "details": [{"counterparty": "杭州三农农业", "amount": 300.0}, {"counterparty": "余杭种植合作社", "amount": 200.0}]},
            "overdue_info": {"count": 1, "details": [{"date": "2025-06", "amount": 10.0, "days": 20}]},
            "multi_lending_flag": True,
            "lender_count": 4,
        },
        # Case 4
        {
            "total_credit_line": 5000.0,
            "used_credit_line": 4800.0,
            "remaining_credit_line": 200.0,
            "loan_details": {"total": 7, "banks": [{"bank": "工商银行", "amount": 1000.0, "type": "流贷", "status": "逾期"}, {"bank": "建设银行", "amount": 800.0, "type": "固贷", "status": "关注"}, {"bank": "浦发银行", "amount": 500.0, "type": "信用贷", "status": "逾期"}, {"bank": "民生银行", "amount": 400.0, "type": "贸易贷"}, {"bank": "农村信用社", "amount": 300.0, "type": "小额贷"}, {"bank": "小贷公司A", "amount": 200.0, "type": "现金贷", "status": "逾期"}, {"bank": "小贷公司B", "amount": 100.0, "type": "现金贷"}]},
            "guarantee_out": {"total": 1500.0, "details": [{"counterparty": "成都宏远汽车", "amount": 800.0}, {"counterparty": "绵阳宏远新能源", "amount": 700.0}]},
            "guarantee_in": {"total": 200.0},
            "overdue_info": {"count": 5, "details": [{"date": "2026-02", "amount": 30.0, "days": 60}, {"date": "2026-01", "amount": 25.0, "days": 45}, {"date": "2025-12", "amount": 18.0, "days": 30}]},
            "attention_list": {"count": 3, "items": ["连续三个月利润为负", "涉诉金额累计超800万元", "实控人被限高"]},
            "multi_lending_flag": True,
            "lender_count": 7,
        },
    ]
    if case_idx not in (0, 1, 4):
        return None
    data = credit_data[list((0, 1, 4)).index(case_idx)]
    kwargs = {
        "company_id": company_id,
        "credit_source": CreditSource.MANUAL,
        "total_credit_line": data["total_credit_line"],
        "used_credit_line": data["used_credit_line"],
        "remaining_credit_line": data["remaining_credit_line"],
        "loan_details": data["loan_details"],
        "guarantee_out": data.get("guarantee_out"),
        "guarantee_in": data.get("guarantee_in"),
        "overdue_info": data.get("overdue_info"),
        "attention_list": data.get("attention_list"),
        "multi_lending_flag": data["multi_lending_flag"],
        "lender_count": data["lender_count"],
        "entered_by": admin_id,
    }
    return EnterpriseCredit(**kwargs)


def make_bank_statement(company_id: uuid.UUID, case_idx: int, admin_id: uuid.UUID):
    stmt_data = [
        # Case 0
        {
            "account_no": "6222****8888",
            "bank_name": "招商银行深圳分行",
            "start_date": date(2025, 7, 1),
            "end_date": date(2025, 12, 31),
            "total_inflow": 1850.0,
            "total_outflow": 1620.0,
            "avg_daily_balance": 280.0,
            "ending_balance": 350.0,
            "transaction_count": 1256,
            "transaction_summary": {"inflow_count": 420, "outflow_count": 836, "avg_inflow": 4.4, "avg_outflow": 1.9},
            "anomaly_flags": None,
            "parse_status": BankStatementParseStatus.PARSED,
        },
        # Case 1
        {
            "account_no": "6228****6666",
            "bank_name": "农业银行杭州余杭支行",
            "start_date": date(2025, 7, 1),
            "end_date": date(2025, 12, 31),
            "total_inflow": 3200.0,
            "total_outflow": 3050.0,
            "avg_daily_balance": 150.0,
            "ending_balance": 180.0,
            "transaction_count": 890,
            "transaction_summary": {"inflow_count": 310, "outflow_count": 580, "avg_inflow": 10.3, "avg_outflow": 5.3},
            "anomaly_flags": None,
            "parse_status": BankStatementParseStatus.PARSED,
        },
        # Case 4
        {
            "account_no": "6217****3333",
            "bank_name": "工商银行成都高新支行",
            "start_date": date(2025, 7, 1),
            "end_date": date(2025, 12, 31),
            "total_inflow": 2800.0,
            "total_outflow": 3500.0,
            "avg_daily_balance": 45.0,
            "ending_balance": 12.0,
            "transaction_count": 2100,
            "transaction_summary": {"inflow_count": 680, "outflow_count": 1420, "avg_inflow": 4.1, "avg_outflow": 2.5},
            "anomaly_flags": {
                "cash_outflow_exceeds_inflow": True,
                "large_night_transactions": 15,
                "frequent_small_transfers": True,
                "description": "流入小于流出，存在大额夜间交易，疑似经营异常",
            },
            "parse_status": BankStatementParseStatus.PARSED,
        },
    ]
    if case_idx not in (0, 1, 4):
        return None
    data = stmt_data[list((0, 1, 4)).index(case_idx)]
    return BankStatement(
        company_id=company_id,
        account_no=data["account_no"],
        bank_name=data["bank_name"],
        statement_source=StatementSource.UPLOADED,
        file_name=f"银行流水_{data['bank_name'][:4]}_{data['start_date'].year}H2.xlsx",
        start_date=data["start_date"],
        end_date=data["end_date"],
        total_inflow=data["total_inflow"],
        total_outflow=data["total_outflow"],
        avg_daily_balance=data["avg_daily_balance"],
        ending_balance=data["ending_balance"],
        transaction_count=data["transaction_count"],
        transaction_summary=data["transaction_summary"],
        anomaly_flags=data["anomaly_flags"],
        parse_status=data["parse_status"],
        uploaded_by=admin_id,
    )


def make_uploaded_report(company_id: uuid.UUID, case_idx: int, admin_id: uuid.UUID):
    report_data = [
        # Case 0
        {
            "report_type": ReportType.AUDIT,
            "report_period": "2024",
            "file_name": "中科智芯2024年度审计报告.pdf",
            "file_source": FileSource.PDF,
            "total_assets": 8500.0,
            "total_liabilities": 1200.0,
            "revenue": 3200.0,
            "net_profit": 980.0,
            "operating_cash_flow": 1100.0,
            "parse_status": ParseStatus.PARSED,
        },
        # Case 1
        {
            "report_type": ReportType.TAX,
            "report_period": "2024",
            "file_name": "绿源农业2024纳税申报表.xlsx",
            "file_source": FileSource.EXCEL,
            "total_assets": 15000.0,
            "total_liabilities": 4500.0,
            "revenue": 8000.0,
            "net_profit": 1200.0,
            "operating_cash_flow": 1500.0,
            "parse_status": ParseStatus.PARSED,
        },
        # Case 2
        {
            "report_type": ReportType.QUARTERLY,
            "report_period": "2025Q3",
            "file_name": "鑫海达2025Q3财务报表.xlsx",
            "file_source": FileSource.EXCEL,
            "total_assets": 5800.0,
            "total_liabilities": 3300.0,
            "revenue": 2800.0,
            "net_profit": 120.0,
            "operating_cash_flow": 80.0,
            "parse_status": ParseStatus.PARSED,
        },
        # Case 4
        {
            "report_type": ReportType.AUDIT,
            "report_period": "2024",
            "file_name": "宏远机械2024审计报告.pdf",
            "file_source": FileSource.PDF,
            "total_assets": 12000.0,
            "total_liabilities": 8000.0,
            "revenue": 7000.0,
            "net_profit": -200.0,
            "operating_cash_flow": -500.0,
            "parse_status": ParseStatus.PARSED,
        },
    ]
    if case_idx == 3:
        return None
    valid_indices = (0, 1, 2, 4)
    data = report_data[valid_indices.index(case_idx)]
    return UploadedFinancialReport(
        company_id=company_id,
        report_type=data["report_type"],
        report_period=data["report_period"],
        file_name=data["file_name"],
        file_path=f"uploads/financial/{data['file_name']}",
        file_source=data["file_source"],
        total_assets=data["total_assets"],
        total_liabilities=data["total_liabilities"],
        revenue=data["revenue"],
        net_profit=data["net_profit"],
        operating_cash_flow=data["operating_cash_flow"],
        parsed_data={"parse_summary": "文件已成功解析"},
        parse_status=data["parse_status"],
        uploaded_by=admin_id,
    )


# ── 主逻辑 ─────────────────────────────────────────────────────────────────


async def _create_admin(session) -> User:
    """创建 admin 用户。"""
    print("[*] Admin 用户不存在，自动创建...")
    admin = User(
        id=ADMIN_USER_ID,
        username="admin",
        email="admin@demo.com",
        password_hash=pwd_context.hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(admin)
    await session.flush()
    print("[OK] Admin 用户已创建 (admin / admin123)")
    return admin


async def seed():
    """创建模拟案例数据。"""
    # 1. 确保表已创建
    await create_tables()

    # 2. 清理旧数据（保留 users 表），避免重复
    async with AsyncSessionLocal() as clear_session:
        from models.task import Task
        from models.company import Company, CompanyShareholder, CompanyExecutive, CompanyInvestment
        from models.company_risk import CompanyRisk
        from models.company_financial import CompanyFinancial
        from models.equity import EquityChain
        from models.rating import RatingRecord
        from models.report import ReportSnapshot
        from models.credit import LegalPersonCredit, EnterpriseCredit
        from models.bank_statement import BankStatement
        from models.financial_report import UploadedFinancialReport
        for model in [UploadedFinancialReport, BankStatement, EnterpriseCredit, LegalPersonCredit,
                      ReportSnapshot, RatingRecord, EquityChain, CompanyFinancial, CompanyRisk,
                      CompanyInvestment, CompanyExecutive, CompanyShareholder, Company, Task]:
            await clear_session.execute(model.__table__.delete())
        await clear_session.commit()
    print("[OK] 旧数据已清理")

    async with AsyncSessionLocal() as session:
        # 3. 确认 admin 用户存在，不存在则自动创建
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = await _create_admin(session)
        else:
            print(f"[OK] 找到 admin 用户: {admin.username}")

        created_count = 0
        for idx, case in enumerate(CASES):
            print(f"\n--- 创建案例 {idx + 1}/5: {case['company_name']} ---")

            # Task — 显式生成 id，避免 SQLAlchemy default 延迟导致 task.id 为 None
            task = Task(
                id=uuid.uuid4(),
                task_no=case["task_no"],
                company_name=case["company_name"],
                unified_credit_code=case["unified_credit_code"],
                status=case["status"],
                progress=case["progress"],
                creator_id=admin.id,
                remark=case["remark"],
            )
            if case["status"] in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                task.completed_at = datetime.now(timezone.utc)
            session.add(task)

            # Company — 显式生成 id，避免 SQLAlchemy default 延迟导致 company.id 为 None
            company = Company(
                id=uuid.uuid4(),
                company_name=case["company_name"],
                unified_credit_code=case["unified_credit_code"],
                legal_rep=case["legal_rep"],
                registered_capital=case["registered_capital"],
                est_date=case["est_date"],
                company_status=case["company_status"],
                business_scope=case["business_scope"],
                address=case["address"],
                industry_info=case["industry_info"],
            )
            session.add(company)

            # Shareholders
            for sh in make_shareholders(company.id, idx):
                session.add(sh)

            # Executives
            for ex in make_executives(company.id, idx, case["legal_rep"]):
                session.add(ex)

            # Investments
            for inv in make_investments(company.id, idx):
                session.add(inv)

            # Risks
            for r in make_risks(company.id, idx, case["high_risk_count"]):
                session.add(r)

            # Financials (工商财报)
            for f in make_financials(company.id, idx):
                session.add(f)

            # Equity Chains
            for e in make_equity_chains(company.id, idx):
                session.add(e)

            # Rating (仅已完成或失败的任务)
            if case["grade"] is not None:
                rating = RatingRecord(
                    task_id=task.id,
                    grade=case["grade"],
                    total_score=case["total_score"],
                    judicial_score=case["judicial_score"],
                    financial_score=case["financial_score"],
                    credit_score=case["credit_score"],
                    operation_score=case["operation_score"],
                    equity_score=case["equity_score"],
                    compliance_score=case["compliance_score"],
                    detail_breakdown={
                        "judicial": "司法风险维度评分详情",
                        "financial": "财务风险维度评分详情",
                        "credit": "信用风险维度评分详情",
                        "operation": "经营风险维度评分详情",
                        "equity": "股权风险维度评分详情",
                        "compliance": "合规风险维度评分详情",
                    },
                )
                session.add(rating)

            # Report Snapshot (仅已完成的任务)
            if case["status"] == TaskStatus.COMPLETED:
                report = ReportSnapshot(
                    task_id=task.id,
                    report_content=f"""# 授信尽调报告

## 一、企业概况
**企业名称：** {case['company_name']}
**统一社会信用代码：** {case['unified_credit_code']}
**法定代表人：** {case['legal_rep']}
**注册资本：** {case['registered_capital']}
**成立日期：** {case['est_date'].strftime('%Y-%m-%d')}
**经营范围：** {case['business_scope']}
**企业地址：** {case['address']}

## 二、工商信息
企业登记状态为 **{case['company_status']}**，所属行业为 {case['industry_info']['primary']}。

## 三、股权结构
企业股权结构清晰，实际控制人明确。

## 四、风险分析
经企查查数据核查，企业对授信决策的影响已在六维评分中体现。

## 五、财务分析
企业近期财务数据已在财务模块展示，经营现金流稳定。

## 六、六维评分
综合评分：**{case['total_score']}分**，评级：**{case['grade']}级**

| 维度 | 得分 |
|------|------|
| 司法风险 | {case['judicial_score']} |
| 财务风险 | {case['financial_score']} |
| 信用风险 | {case['credit_score']} |
| 经营风险 | {case['operation_score']} |
| 股权风险 | {case['equity_score']} |
| 合规风险 | {case['compliance_score']} |

## 七、授信建议
{case['remark']}
""",
                    report_version="v1.0",
                )
                session.add(report)

            # Legal Person Credit
            lpc = make_legal_person_credit(company.id, idx, admin.id, case["legal_rep"])
            if lpc:
                session.add(lpc)

            # Enterprise Credit
            ec = make_enterprise_credit(company.id, idx, admin.id)
            if ec:
                session.add(ec)

            # Bank Statement
            bs = make_bank_statement(company.id, idx, admin.id)
            if bs:
                session.add(bs)

            # Uploaded Financial Report
            ufr = make_uploaded_report(company.id, idx, admin.id)
            if ufr:
                session.add(ufr)

            await session.flush()
            created_count += 1
            print(f"  [OK] Task={case['task_no']}, Status={case['status'].value}, Progress={case['progress']}%")
            if case["grade"]:
                print(f"  [OK] Rating: {case['grade']}级 ({case['total_score']}分)")
            print(f"  [OK] 股东({len(make_shareholders(company.id, idx))}) 高管({len(make_executives(company.id, idx, case['legal_rep']))}) 投资({len(make_investments(company.id, idx))}) 风险({len(make_risks(company.id, idx, case['high_risk_count']))})")
    
        await session.commit()
        print(f"\n{'='*60}")
        print(f"[SUCCESS] 模拟数据创建完成！共创建 {created_count} 个尽调任务")
        print(f"{'='*60}")
        print("\n数据概览：")
        print("  案例1: 深圳中科智芯科技 - 已完成 - A级 (92.5分) - 优质科技贷案例")
        print("  案例2: 杭州绿源农业发展 - 已完成 - B级 (76.0分) - 农业供应链案例")
        print("  案例3: 北京鑫海达贸易   - 进行中 - 65%   - 贸易流贷案例（补充数据中）")
        print("  案例4: 上海云图数据服务 - 待处理 - 10%   - 新接任务（未启动）")
        print("  案例5: 成都宏远机械     - 失败   - D级 (35.0分) - 高风险拒贷案例")
        print("\n每个案例包含：")
        print("  - 工商注册信息、股东、高管、对外投资")
        print("  - 风险信息（诉讼/失信/处罚等）")
        print("  - 工商财报（2-3年）")
        print("  - 股权穿透链（向上+UBO）")
        print("  - 六维评分（已完成/失败的任务）")
        print("  - 尽调报告快照（已完成的任务）")
        print("  - 法人/企业征信（部分案例）")
        print("  - 银行流水（部分案例）")
        print("  - 上传财报（部分案例）")


if __name__ == "__main__":
    asyncio.run(seed())
