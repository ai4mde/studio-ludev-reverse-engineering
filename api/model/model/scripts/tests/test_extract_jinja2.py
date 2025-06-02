import pytest
import zipfile
import pathlib
import shutil
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))
from api.model.model.scripts.src.extract_jinja2 import get_arguments, extract_zip, get_project_root, projects_folder

# Start testing method with test_

# Install by:
#   pip install pytest pytest-cov

# Run test by:
#   coverage run --source=<package> -m pytest -v tests && coverage report -m
# Example:
#   coverage run --source=scripts.src.extract_jinja2 -m pytest -v tests && coverage report -m

# For nicer report, run:
#   coverage html
# And open htmlcov/index.html

# Fixture to temporary change sys.argv
@pytest.fixture
def fake_sys_argv(monkeypatch):
    def _set_args(args):
        monkeypatch.setattr(sys, "argv", ["prog"] + args)
    return _set_args


# Fixture voor temporary zipfile
@pytest.fixture
def dummy_zip_file(tmp_path):
    project_name = "my_project"
    project_dir = tmp_path / project_name
    inner_dir = project_dir / project_name
    inner_dir.mkdir(parents=True)

    (project_dir / "manage.py").write_text("print('manage')")
    (inner_dir / "__init__.py").write_text("")
    (inner_dir / "settings.py").write_text("SECRET_KEY = 'dummy'")

    zip_path = tmp_path / "project.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file_path in project_dir.rglob("*"):
            zf.write(file_path, arcname=file_path.relative_to(tmp_path))

    yield zip_path

    # Clean up
    if os.path.exists(projects_folder):
        shutil.rmtree(projects_folder)


# Fixture voor tijdelijke zipfile
@pytest.fixture
def dummy_empty_zip_file(tmp_path):
    project_name = "my_project"
    project_dir = tmp_path / project_name
    inner_dir = project_dir / project_name
    inner_dir.mkdir(parents=True)

    (project_dir / "manage.py").write_text("print('manage')")
    (inner_dir / "__init__.py").write_text("")
    (inner_dir / "settings.py").write_text("")

    zip_path = tmp_path / "project.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file_path in project_dir.rglob("*"):
            zf.write(file_path, arcname=file_path.relative_to(tmp_path))

    yield zip_path

    # Clean up
    if os.path.exists(projects_folder):
        shutil.rmtree(projects_folder)


# --- Tests ---
# Succesful test
def test_get_arguments_success(fake_sys_argv):
    fake_sys_argv(["--zip_file", "dummy.zip"])
    args = get_arguments()
    assert args.zip_file == "dummy.zip"


# Empty argument
def test_get_arguments_no_zip_file(fake_sys_argv):
    fake_sys_argv(["--zip_file", ""])
    with pytest.raises(Exception):  # argparse exits if required arg is missing
        get_arguments()


# Argument with lower than possible argument length
def test_get_arguments_smaller_length(fake_sys_argv):
    fake_sys_argv(["--zip_file", "xyz"])
    with pytest.raises(Exception):  # argparse exits if required arg is missing
        get_arguments()


# Missing argument
def test_get_arguments_missing(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog"])
    with pytest.raises(SystemExit):  # argparse exits if required arg is missing
        get_arguments()


# Non-existing argument
def test_get_other_argument(fake_sys_argv):
    fake_sys_argv(["-t", "test"])
    with pytest.raises(SystemExit):  # argparse exits if required arg is missing
        get_arguments()


def test_extract_zip_creates_folder(dummy_zip_file):
    extract_zip(str(dummy_zip_file))
    extracted_folders = os.listdir(projects_folder)
    assert any(os.path.isdir(os.path.join(projects_folder, name)) for name in extracted_folders)

def test_extract_real_zip(fake_sys_argv):
    zip_path = "api/model/model/scripts/test_prototype.zip"
    fake_sys_argv(["--zip_file", zip_path])
    args = get_arguments()

    extract_zip(args.zip_file)
    assert os.path.exists(projects_folder)

    extracted = os.listdir(projects_folder)
    assert len(extracted) > 0

@pytest.mark.usefixtures("dummy_zip_file")
def test_extract_zip(dummy_zip_file):
    extract_zip(str(dummy_zip_file))
    # Should not raise or re-extract if already done
    extract_zip(str(dummy_zip_file))
    extracted_folders = os.listdir(projects_folder)
    assert any(os.path.isdir(os.path.join(projects_folder, name)) for name in extracted_folders)


@pytest.mark.usefixtures("dummy_empty_zip_file")
def test_extract_empty_zip(dummy_empty_zip_file):
    extract_zip(str(dummy_empty_zip_file))  # Extract zip

    with pytest.raises(Exception):  # get_project_root should throw exception if settings is empty
        get_project_root(str(dummy_empty_zip_file))


def test_get_project_info_creates_path(tmp_path, monkeypatch):
    # Create test structure
    test_root = tmp_path / "test_prototype" / "my_project"
    test_root.mkdir(parents=True)
    settings_path = test_root / "settings.py"
    settings_path.write_text("DEBUG = True")

    monkeypatch.setattr(pathlib, "Path", lambda _: tmp_path / "test_prototype")
    result = get_project_root('my_project')
    assert result.name == "test_prototype"
