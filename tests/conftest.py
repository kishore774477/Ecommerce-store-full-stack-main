import os
import sys
import tempfile

# Point all data files at a throwaway folder BEFORE any project module is imported.
_TMP = tempfile.mkdtemp(prefix="ecom-test-")
os.environ["ECOM_DATA_DIR"] = _TMP
os.environ.setdefault("SECRET_KEY", "test-secret")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil  # noqa: E402

import pytest  # noqa: E402

from config import settings  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_data():
    """Each test starts from the seed catalogue with no users/orders/reviews."""
    shutil.rmtree(settings.RAW_DATA_DIR, ignore_errors=True)
    os.makedirs(settings.RAW_DATA_DIR, exist_ok=True)
    yield
