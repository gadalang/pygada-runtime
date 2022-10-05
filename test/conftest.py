"""Common stuff for tests."""
from pathlib import Path

TEST_DIR = str(Path(__file__).parent.absolute())
FOO_DIR = str(Path(TEST_DIR) / "foo")
FOO_GADA_YML = str(Path(FOO_DIR) / "gada.yml")
BAR_DIR = str(Path(FOO_DIR) / "bar")
BAR_GADA_YML = str(Path(BAR_DIR) / "gada.yml")
