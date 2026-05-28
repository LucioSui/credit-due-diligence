"""尽调任务管理服务."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import Company
from models.task import Task, TaskStatus

logger = logging.getLogger(__name__)

# ── 扫描步骤定义 ──────────────────────────────────────

SCAN_STEPS = [
    {"step": "company_info", "label": "企业基本信息核查", "progress_pct": 10},
    {"step": "risk_scan", "label": "司法风险扫描", "progress_pct": 25},
    {"step": "equity_scan", "label": "股权结构穿透", "progress_pct": 40},
    {"step": "financial_scan", "label": "财务报表采集", "progress_pct": 55},
    {"step": "bank_scan", "label": "银行流水分析", "progress_pct": 65},
    {"step": "credit_scan", "label": "信贷征信查询", "progress_pct": 75},
    {"step": "rating_calc", "label": "六维评级计算", "progress_pct": 90},
    {"step": "report_gen", "label": "报告生成", "progress_pct": 100},
]


def _generate_task_no() -> str:
    """生成尽调编号 DD-YYYYMMDD-XXXX"""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = str(uuid4().int)[:4].upper()
    return f"DD-{today}-{suffix}"


class TaskService:
    """尽调任务管理服务"""

    def __init__(self) -> None:
        pass

    async def create_task(
        self,
        db: AsyncSession,
        company_name: str,
        unified_social_credit_code: str | None,
        creator_id: str,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """创建尽调任务"""
        task = Task(
            id=uuid4(),
            task_no=_generate_task_no(),
            company_name=company_name,
            unified_credit_code=unified_social_credit_code,
            status=TaskStatus.PENDING,
            progress=0.0,
            creator_id=uuid4() if creator_id is None else UUID(creator_id),
            remark=remark,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return self._task_to_dict(task)

    async def get_task(
        self, db: AsyncSession, task_id: str
    ) -> dict[str, Any]:
        """获取单个任务详情"""
        stmt = select(Task).where(Task.id == UUID(task_id))
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        return self._task_to_dict(task)

    async def list_tasks(
        self,
        db: AsyncSession,
        status: TaskStatus | None = None,
        creator_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """任务列表（支持筛选和分页）"""
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status == status)
        if creator_id:
            stmt = stmt.where(Task.creator_id == UUID(creator_id))
        stmt = stmt.order_by(Task.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        tasks = list(result.scalars().all())

        # 统计总数
        count_stmt = select(Task)
        if status:
            count_stmt = count_stmt.where(Task.status == status)
        if creator_id:
            count_stmt = count_stmt.where(Task.creator_id == UUID(creator_id))
        count_result = await db.execute(count_stmt)
        total = len(list(count_result.scalars().all()))

        return {
            "items": [self._task_summary(t) for t in tasks],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def update_progress(
        self, db: AsyncSession, task_id: str, progress: float, status: TaskStatus | None = None
    ) -> dict[str, Any]:
        """更新任务进度"""
        stmt = select(Task).where(Task.id == UUID(task_id))
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        task.progress = min(max(progress, 0.0), 100.0)
        if status:
            task.status = status
        task.updated_at = datetime.now(timezone.utc)

        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(task)
        return self._task_to_dict(task)

    async def get_scan_progress(self, db: AsyncSession, task_id: str) -> dict[str, Any]:
        """获取扫描步骤进度"""
        task = await self.get_task(db, task_id)
        current_progress = task["progress"]

        steps = []
        for step_def in SCAN_STEPS:
            done = current_progress >= step_def["progress_pct"]
            steps.append({
                "step": step_def["step"],
                "label": step_def["label"],
                "done": done,
                "progress_pct": step_def["progress_pct"],
            })

        return {
            "task_id": task_id,
            "status": task["status"],
            "progress": current_progress,
            "steps": steps,
        }

    async def start_scan(
        self, db: AsyncSession, task_id: str
    ) -> dict[str, Any]:
        """启动扫描（将任务状态改为 RUNNING）"""
        return await self.update_progress(
            db, task_id, progress=0.0, status=TaskStatus.RUNNING
        )

    @staticmethod
    def _task_to_dict(task: Task) -> dict[str, Any]:
        return {
            "id": str(task.id),
            "task_no": task.task_no,
            "company_name": task.company_name,
            "unified_social_credit_code": task.unified_credit_code,
            "status": task.status.value,
            "progress": task.progress,
            "created_by": str(task.creator_id),
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }

    @staticmethod
    def _task_summary(task: Task) -> dict[str, Any]:
        return {
            "id": str(task.id),
            "task_no": task.task_no,
            "company_name": task.company_name,
            "unified_social_credit_code": task.unified_credit_code,
            "status": task.status.value,
            "progress": task.progress,
            "created_by": str(task.creator_id),
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }
