import os, subprocess, time, difflib
from pathlib import Path
import click, yaml, requests
from loguru import logger
from jinja2 import Environment, FileSystemLoader

# ---------- helpers ----------
def load_project(cfg_path: str):
    data = yaml.safe_load(Path(cfg_path).read_text(encoding="utf-8"))
    # tiny validation
    for k in ["service", "provider", "repository", "branches"]:
        if k not in data:
            raise click.ClickException(f"Missing '{k}' in {cfg_path}")
    return data

def render_pipeline(project: dict, template_dir: Path) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    tpl = env.get_template("ci.yml.j2")
    return tpl.render(
        service=project["service"],
        branches=project["branches"],
    )

def write_pipeline(text: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def git(*args):
    subprocess.run(["git", *args], check=True)

def gh_api(token: str, method: str, path: str, **kw):
    url = f"https://api.github.com{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept":"application/vnd.github+json"}
    return requests.request(method, url, headers=headers, **kw)

def slack_notify(text: str, webhook: str | None):
    if not webhook: return
    try:
        requests.post(webhook, json={"text": text}, timeout=5)
    except Exception as e:
        logger.warning(f"Slack notify failed: {e}")

# ---------- CLI ----------
@click.group()
def cli():
    logger.add("cicd.log", rotation="500 KB")

@cli.command()
@click.option("--config", default="examples/project.yaml")
@click.option("--template-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None)
def init(config, template_dir):
    """Render pipeline file locally (no git changes)."""
    proj = load_project(config)
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates" / proj["provider"]
    else:
        template_dir = template_dir / proj["provider"]
    out = render_pipeline(proj, template_dir)
    path = Path(".github/workflows/ci.yml")
    write_pipeline(out, path)
    click.echo(f"Rendered -> {path}")

@cli.command()
@click.option("--config", default="examples/project.yaml")
@click.option("--template-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None)
def plan(config, template_dir):
    """Show diff between rendered and current file."""
    proj = load_project(config)
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates" / proj["provider"]
    else:
        template_dir = template_dir / proj["provider"]
    new_text = render_pipeline(proj, template_dir)
    path = Path(".github/workflows/ci.yml")
    old_text = path.read_text(encoding="utf-8") if path.exists() else ""
    diff = difflib.unified_diff(
        old_text.splitlines(True),
        new_text.splitlines(True),
        fromfile="current",
        tofile="rendered",
    )
    out = "".join(diff)
    click.echo(out if out else "No changes.")

@cli.command()
@click.option("--config", default="examples/project.yaml")
@click.option("--branch", default="cicd-bootstrap")
@click.option("--base", default="main")
@click.option("--template-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None)
def push(config, branch, base, template_dir):
    """Commit rendered workflow to a branch and open a PR."""
    proj = load_project(config)
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates" / proj["provider"]
    else:
        template_dir = template_dir / proj["provider"]
    rendered = render_pipeline(proj, template_dir)
    path = Path(".github/workflows/ci.yml")
    write_pipeline(rendered, path)

    git("checkout", "-B", branch)
    git("add", ".github/workflows/ci.yml")
    git("commit", "-m", "chore: manage CI with tool")
    git("push", "-u", "origin", branch, "-f")

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        click.echo("Note: set GITHUB_TOKEN to auto-open a PR, or open it manually.")
        return
    r = gh_api(token, "POST", f"/repos/{proj['repository']}/pulls",
               json={"title":"Manage CI via tool","head":branch,"base":base})
    if r.status_code >= 300:
        raise click.ClickException(f"PR create failed: {r.status_code} {r.text}")
    click.echo(f"PR created: {r.json().get('html_url')}")

@cli.command()
@click.option("--config", default="examples/project.yaml")
@click.option("--branch", default="main")
@click.option("--watch/--no-watch", default=True)
def run(config, branch, watch):
    """Manually trigger the workflow on a branch and optionally watch status."""
    proj = load_project(config)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise click.ClickException("Set GITHUB_TOKEN (repo scope).")

    # trigger (workflow file must be named ci.yml)
    r = gh_api(token, "POST",
               f"/repos/{proj['repository']}/actions/workflows/ci.yml/dispatches",
               json={"ref": branch})
    if r.status_code not in (204, 201):
        raise click.ClickException(f"Dispatch failed: {r.status_code} {r.text}")
    click.echo("Triggered workflow_dispatch.")

    time.sleep(3)
    rr = gh_api(token, "GET", f"/repos/{proj['repository']}/actions/runs",
                params={"branch": branch})
    run = rr.json()["workflow_runs"][0]
    run_id, url = run["id"], run["html_url"]
    click.echo(f"Run: {run_id} -> {url}")

    if watch:
        _watch(proj, token, run_id)

def _watch(proj, token, run_id):
    last = ""
    while True:
        r = gh_api(token, "GET", f"/repos/{proj['repository']}/actions/runs/{run_id}")
        j = r.json()
        status = f"{j['status']}/{j.get('conclusion')}"
        if status != last:
            click.echo(f"[{time.strftime('%H:%M:%S')}] {status}")
            last = status
        if j["status"] == "completed":
            # Optional Slack
            webhook = (proj.get("notifications") or {}).get("slack_webhook", "")
            slack_notify(f"CI for {proj['repository']} finished: {j.get('conclusion')}", webhook)
            break
        time.sleep(5)

@cli.command()
@click.option("--config", default="examples/project.yaml")
@click.option("--last", default=5)
def status(config, last):
    """List recent runs with status + links."""
    proj = load_project(config)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise click.ClickException("Set GITHUB_TOKEN (repo scope).")
    r = gh_api(token, "GET", f"/repos/{proj['repository']}/actions/runs")
    runs = r.json().get("workflow_runs", [])[:last]
    for run in runs:
        click.echo(f"{run['id']}  {run['status']}/{run.get('conclusion')}  {run['html_url']}")

if __name__ == "__main__":
    cli()
