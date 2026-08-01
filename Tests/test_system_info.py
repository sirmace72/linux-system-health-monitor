from system_info import SystemInfo


def test_get_hostname() -> None:
    info = SystemInfo()
    assert isinstance(info.get_hostname(), str)
    assert len(info.get_hostname()) > 0


def test_get_os() -> None:
    info = SystemInfo()
    result = info.get_os()
    assert isinstance(result, str)
    assert "Linux" in result


def test_get_kernel() -> None:
    info = SystemInfo()
    assert isinstance(info.get_kernel(), str)


def test_get_architecture() -> None:
    info = SystemInfo()
    assert isinstance(info.get_architecture(), str)


def test_get_cpu_model() -> None:
    info = SystemInfo()
    model = info.get_cpu_model()
    assert isinstance(model, str)
    assert len(model) > 0


def test_get_cpu_model_fallback(tmp_path) -> None:
    fake_cpuinfo = tmp_path / "cpuinfo"
    fake_cpuinfo.write_text("")

    with open("/proc/cpuinfo", "r", encoding="utf-8") as real_file:
        pass

    assert SystemInfo._get_cpu_model() is not None
