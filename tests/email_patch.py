from unittest.mock import patch
import pytest

@pytest.fixture(autouse=True)
def patch_send_enrollment_email():
    with patch("app.email_utils.send_enrollment_email") as mock_email:
        mock_email.return_value = None
        yield mock_email
