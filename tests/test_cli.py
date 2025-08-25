import pytest
from pathlib import Path
from click.testing import CliRunner
import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cli import load_project, cli


@pytest.fixture
def project_file_content():
    return """
service: my-service
provider: github
repository: my-org/my-repo
branches:
  - main
  - dev
"""


@pytest.fixture
def project_file(project_file_content):
    config_path = Path("test_project.yaml")
    config_path.write_text(project_file_content)
    yield str(config_path)
    config_path.unlink()


def test_load_project(project_file):
    """Tests the load_project function."""
    project = load_project(project_file)
    assert project["service"] == "my-service"
    assert project["provider"] == "github"
    assert project["repository"] == "my-org/my-repo"
    assert project["branches"] == ["main", "dev"]


@pytest.fixture
def runner():
    return CliRunner()


def test_init_command(runner, project_file_content):
    """Tests the init command with a dummy template."""
    with runner.isolated_filesystem():
        # Create project config file
        with open("project.yaml", "w") as f:
            f.write(project_file_content)

        # Create a dummy template directory and file
        # The `init` command expects a provider subdirectory, so we create `dummy_templates/github`
        template_dir = Path("dummy_templates/github")
        template_dir.mkdir(parents=True, exist_ok=True)
        with open(template_dir / "ci.yml.j2", "w") as f:
            f.write("Hello from a dummy template! Branches: {{ branches|join(', ') }}")

        # Run the init command with the dummy template
        result = runner.invoke(
            cli,
            [
                "init",
                "--config",
                "project.yaml",
                "--template-dir",
                str(template_dir.parent),  # Pass the parent directory
            ],
        )

        assert result.exit_code == 0
        assert "Rendered -> .github/workflows/ci.yml" in result.output

        # Check the content of the rendered file
        rendered_file = Path(".github/workflows/ci.yml")
        assert rendered_file.exists()
        content = rendered_file.read_text()
        assert "Hello from a dummy template!" in content
        assert "Branches: main, dev" in content


def test_render_pipeline():
    """Tests the render_pipeline function against a golden file."""
    from cli import render_pipeline

    project = {
        "service": "my-service",
        "provider": "github",
        "repository": "my-org/my-repo",
        "branches": ["main", "dev"],
    }
    template_dir = Path(__file__).parent.parent / "templates" / project["provider"]
    rendered_content = render_pipeline(project, template_dir)

    golden_file_path = Path(__file__).parent / "golden.yml"
    golden_content = golden_file_path.read_text()

    assert rendered_content == golden_content


def test_plan_command(runner, project_file_content):
    """Tests the plan command."""
    with runner.isolated_filesystem():
        # Create project config file
        with open("project.yaml", "w") as f:
            f.write(project_file_content)

        # Create a dummy template directory and file
        template_dir = Path("dummy_templates/github")
        template_dir.mkdir(parents=True, exist_ok=True)
        with open(template_dir / "ci.yml.j2", "w") as f:
            f.write("Hello from a dummy template! Branches: {{ branches|join(', ') }}")

        # Create an existing workflow file
        workflow_dir = Path(".github/workflows")
        workflow_dir.mkdir(parents=True, exist_ok=True)
        with open(workflow_dir / "ci.yml", "w") as f:
            f.write("Old content")

        # Run the plan command
        result = runner.invoke(
            cli,
            [
                "plan",
                "--config",
                "project.yaml",
                "--template-dir",
                str(template_dir.parent),
            ],
        )

        assert result.exit_code == 1
        assert "--- current" in result.output
        assert "+++ rendered" in result.output

        # Run the plan command again with the same content
        with open(workflow_dir / "ci.yml", "w") as f:
            f.write("Hello from a dummy template! Branches: main, dev")

        result = runner.invoke(
            cli,
            [
                "plan",
                "--config",
                "project.yaml",
                "--template-dir",
                str(template_dir.parent),
            ],
        )

        assert result.exit_code == 0
        assert "No changes." in result.output
