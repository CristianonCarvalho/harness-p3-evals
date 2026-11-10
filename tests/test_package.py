import evals


def test_package_has_version():
    assert isinstance(evals.__version__, str)
    assert evals.__version__.count(".") == 2
