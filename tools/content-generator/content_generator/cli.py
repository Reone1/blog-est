"""
Content Generator CLI

콘텐츠 생성 명령줄 인터페이스
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .generator import ContentGenerator, ContentType

app = typer.Typer(
    name="generate",
    help="AI 기반 투자정보 블로그 콘텐츠 생성기",
)
console = Console()


@app.command()
def generate(
    content_type: str = typer.Option(
        "daily_briefing",
        "--type", "-t",
        help="콘텐츠 유형 (daily_briefing, std_analysis, sector_analysis, weekly_review, monthly_review, stock_report)",
    ),
    output: Path = typer.Option(
        Path("posts"),
        "--output", "-o",
        help="출력 디렉토리",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="ANTHROPIC_API_KEY",
        help="Anthropic API 키 (없으면 Claude CLI 모드로 자동 전환)",
    ),
    context: Optional[str] = typer.Option(
        None,
        "--context", "-c",
        help="추가 컨텍스트 (예: 특정 섹터, 종목 지정)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="실제 파일 저장 없이 미리보기만",
    ),
):
    """
    AI 기반 투자정보 콘텐츠 생성

    Examples:
        generate --type daily_briefing
        generate --type std_analysis --output posts/
        generate --type sector_analysis --context "반도체 섹터"
    """
    # 콘텐츠 유형 파싱
    try:
        ctype = ContentType(content_type)
    except ValueError:
        console.print(f"[red]❌ 알 수 없는 콘텐츠 유형: {content_type}[/red]")
        console.print("사용 가능한 유형: daily_briefing, std_analysis, sector_analysis, weekly_review, monthly_review, stock_report")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold blue]📝 콘텐츠 생성 시작[/bold blue]\n"
        f"유형: {ctype.value}\n"
        f"출력: {output}",
        title="Content Generator",
    ))

    try:
        generator = ContentGenerator(api_key=api_key)
    except ValueError as e:
        console.print(f"[red]❌ 초기화 실패: {e}[/red]")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # 1. 데이터 수집
        task = progress.add_task("📊 시장 데이터 수집 중...", total=None)
        progress.update(task, description="📊 시장 데이터 수집 중...")

        # 2. 콘텐츠 생성
        progress.update(task, description="🤖 AI 콘텐츠 생성 중...")
        post = generator.generate(ctype, additional_context=context)

        progress.update(task, description="✅ 완료!")

    # 결과 출력
    console.print("\n[bold green]✅ 생성 완료![/bold green]")
    console.print(f"제목: {post.title}")
    console.print(f"파일명: {post.filename}")
    console.print(f"태그: {', '.join(post.tags)}")

    if dry_run:
        console.print("\n[yellow]📝 Dry run 모드 - 콘텐츠 미리보기:[/yellow]")
        console.print(Panel(post.content[:1000] + "...", title="Content Preview"))
    else:
        # 파일 저장
        output_path = generator.save_post(post, output)
        console.print(f"\n[green]📁 저장됨: {output_path}[/green]")

    return post


@app.command()
def regenerate(
    content_type: str = typer.Option(
        ...,
        "--type", "-t",
        help="콘텐츠 유형 (daily_briefing, std_analysis, sector_analysis, weekly_review, monthly_review)",
    ),
    target_date: str = typer.Option(
        ...,
        "--date", "-d",
        help="재생성 대상 날짜 (YYYY-MM-DD 형식)",
    ),
    output: Path = typer.Option(
        Path("posts"),
        "--output", "-o",
        help="출력 디렉토리",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="ANTHROPIC_API_KEY",
        help="Anthropic API 키",
    ),
    context: Optional[str] = typer.Option(
        None,
        "--context", "-c",
        help="추가 컨텍스트",
    ),
):
    """
    과거 날짜의 콘텐츠를 실제 시장 데이터 기반으로 재생성

    FinanceDataReader를 사용하여 해당 날짜의 실제 주가 데이터를 수집하고,
    콘텐츠 유형별 프롬프트 템플릿을 적용하여 재생성합니다.

    Examples:
        regenerate --type daily_briefing --date 2026-03-30
        regenerate --type sector_analysis --date 2026-03-31
    """
    from datetime import date as date_type

    # 날짜 파싱
    try:
        parts = target_date.split("-")
        parsed_date = date_type(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        console.print(f"[red]날짜 형식 오류: {target_date} (YYYY-MM-DD 필요)[/red]")
        raise typer.Exit(1)

    # 콘텐츠 유형 파싱
    try:
        ctype = ContentType(content_type)
    except ValueError:
        console.print(f"[red]알 수 없는 콘텐츠 유형: {content_type}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold blue]콘텐츠 재생성[/bold blue]\n"
        f"유형: {ctype.value}\n"
        f"날짜: {parsed_date}\n"
        f"출력: {output}",
        title="Regenerate",
    ))

    try:
        generator = ContentGenerator(api_key=api_key)
    except ValueError as e:
        console.print(f"[red]초기화 실패: {e}[/red]")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"과거 시장 데이터 수집 중 ({parsed_date})...", total=None
        )
        progress.update(
            task,
            description=f"AI 콘텐츠 재생성 중 ({ctype.value}, {parsed_date})...",
        )
        post = generator.generate(
            ctype,
            additional_context=context,
            target_date=parsed_date,
        )
        progress.update(task, description="완료!")

    console.print(f"\n[bold green]재생성 완료![/bold green]")
    console.print(f"제목: {post.title}")
    console.print(f"파일명: {post.filename}")

    output_path = generator.save_post(post, output)
    console.print(f"[green]저장됨: {output_path}[/green]")

    return post


@app.command()
def list_types():
    """사용 가능한 콘텐츠 유형 목록"""
    console.print("[bold]사용 가능한 콘텐츠 유형:[/bold]\n")

    types = [
        ("daily_briefing", "시장 데일리 브리핑", "매일 장마감 후"),
        ("std_analysis", "표준편차 매매 분석", "매일"),
        ("sector_analysis", "섹터/테마 분석", "주 2-3회"),
        ("weekly_review", "주간 리뷰", "매주 금요일"),
        ("monthly_review", "월간 리뷰", "매월 첫째 주"),
        ("stock_report", "개별 종목 리포트", "이벤트 시"),
    ]

    for type_id, name, schedule in types:
        console.print(f"  [cyan]{type_id:20}[/cyan] {name} ({schedule})")


@app.command()
def test_connection():
    """Claude 연결 테스트 (CLI 모드 또는 API Key 모드)"""
    try:
        from .claude_client import ClaudeClient

        client = ClaudeClient()
        console.print(f"[blue]🔗 인증 모드: {client.mode}[/blue]")
        response = client.generate("Say 'Hello, connection test successful!' in Korean.")

        console.print("[green]✅ Claude 연결 성공![/green]")
        console.print(f"응답: {response}")
    except Exception as e:
        console.print(f"[red]❌ 연결 실패: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
