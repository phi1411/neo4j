"""Không ghi thông tin kết nối vào lỗi CLI, kể cả khi driver đưa nó vào exception."""
from scripts.phase2 import report_failure


def test_phase2_error_does_not_disclose_private_details(capsys):
    report_failure(RuntimeError("private-password-at-bolt://private-server:7687"))
    result = capsys.readouterr()
    assert "RuntimeError" in result.err
    assert "private-password" not in result.err
    assert "private-server" not in result.err
    assert not result.out
