import time
import sys
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.core.database.v3_schema import ExecutionRequest, AuditLog, MasterUser, FunctionCatalog
from src.core.database.v3_campaigns import Campaign
from src.core.database.v3_extensions import TgSession

console = Console()

def fetch_data():
    db: Session = SessionLocal()
    try:
        # 1. 시스템 요약
        user_count = db.query(MasterUser).count()
        session_count = db.query(TgSession).count()
        active_session = db.query(TgSession).filter_by(status="ACTIVE").count()
        
        # 2. 최근 실행 요청 (Active Jobs)
        active_jobs = db.query(ExecutionRequest).order_by(ExecutionRequest.created_at.desc()).limit(5).all()
        
        # 3. 최근 감사 로그 (Audit Logs)
        audit_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(5).all()
        
        # 4. 캠페인 현황
        campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).limit(3).all()
        
        return {
            "stats": (user_count, session_count, active_session),
            "jobs": active_jobs,
            "logs": audit_logs,
            "campaigns": campaigns
        }
    finally:
        db.close()

def make_layout():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    layout["left"].split(
        Layout(name="jobs", ratio=1),
        Layout(name="campaigns", ratio=1)
    )
    return layout

def generate_dashboard():
    data = fetch_data()
    user_cnt, sess_cnt, act_sess = data["stats"]
    
    # Header
    header_content = Table.grid(expand=True)
    header_content.add_column(justify="center", ratio=1)
    header_content.add_column(justify="right")
    header_content.add_row(
        f"[bold cyan]TG-SYSTEM ENTERPRISE V3.1[/bold cyan] | [green]KERNEL: ONLINE[/green]",
        f"[white]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/white]"
    )
    
    # Jobs Table
    job_table = Table(title="[bold]Real-time Execution Queue[/bold]", expand=True, border_style="blue")
    job_table.add_column("Req ID", style="cyan", no_wrap=True)
    job_table.add_column("Function", style="magenta")
    job_table.add_column("Status", justify="center")
    job_table.add_column("Time(ms)", justify="right")
    
    for job in data["jobs"]:
        status_color = "green" if job.status == "COMPLETED" else "yellow" if job.status == "PROCESSING" else "red"
        job_table.add_row(
            job.req_id[:8], 
            job.function_code, 
            f"[{status_color}]{job.status}[/{status_color}]",
            str(job.execution_time_ms or "-")
        )

    # Audit Logs
    log_table = Table(title="[bold]Legal Audit Trail[/bold]", expand=True, border_style="yellow")
    log_table.add_column("Time", style="dim")
    log_table.add_column("Actor", style="bold")
    log_table.add_column("Action")
    log_table.add_column("Details")
    
    for log in data["logs"]:
        log_table.add_row(
            log.created_at.strftime("%H:%M:%S"),
            log.actor_id[:8],
            log.action,
            log.snapshot_data[:30] + "..."
        )

    # Campaigns
    camp_table = Table(title="[bold]Campaign Status[/bold]", expand=True, border_style="green")
    camp_table.add_column("Name")
    camp_table.add_column("Status")
    camp_table.add_column("Progress")
    
    for camp in data["campaigns"]:
        progress = f"{camp.sent_count}/{camp.total_targets}"
        camp_table.add_row(camp.name, camp.status, progress)

    # Stats Panel
    stats_text = Text()
    stats_text.append(f"\n👥 Total Users: {user_cnt}\n", style="bold white")
    stats_text.append(f"📱 Total Sessions: {sess_cnt}\n", style="bold white")
    stats_text.append(f"🟢 Active Sessions: {act_sess}\n", style="bold green")
    
    stats_panel = Panel(stats_text, title="System Resource", border_style="white")

    layout = make_layout()
    layout["header"].update(Panel(header_content, style="white on black"))
    layout["jobs"].update(Panel(job_table))
    layout["campaigns"].update(Panel(camp_table))
    layout["right"].update(Panel(log_table))
    layout["footer"].update(stats_panel)
    
    return layout

def run_monitor():
    with Live(generate_dashboard(), refresh_per_second=1, screen=True) as live:
        while True:
            time.sleep(1)
            live.update(generate_dashboard())

if __name__ == "__main__":
    try:
        run_monitor()
    except KeyboardInterrupt:
        print("Monitor Stopped.")