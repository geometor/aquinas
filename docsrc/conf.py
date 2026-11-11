from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photon_platform.publish.global_conf import *  # noqa: E402, F403
import geometor.aquinas as module  # noqa: E402

version = module.__version__

org = "geometor"
org_name = "GEOMETOR"

repo = "aquinas"
repo_name = "aquinas"

setup_globals(org, org_name, repo, repo_name)  # noqa: F405

project = "GEOMETOR • aquinas"
author = "Sanctus Thomas de Aquino, O.P."
copyright = "Public Domain Latin Editions • Digital Codex & Translations GEOMETOR"

intersphinx_mapping = {}
