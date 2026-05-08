import psutil

from bananalyzer.foreground import detect_foreground_activity


class _FakeWin32Gui:
    def __init__(self, hwnd: int = 1, title: str = "Title", class_name: str = "Class"):
        self._hwnd = hwnd
        self._title = title
        self._class_name = class_name

    def GetForegroundWindow(self):
        return self._hwnd

    def GetWindowText(self, hwnd):
        assert hwnd == self._hwnd
        return self._title

    def GetClassName(self, hwnd):
        assert hwnd == self._hwnd
        return self._class_name


class _FakeWin32Process:
    def __init__(self, pid: int = 1234):
        self._pid = pid

    def GetWindowThreadProcessId(self, hwnd):
        return (0, self._pid)


class _FakeProc:
    def __init__(self, name: str, exe: str):
        self._name = name
        self._exe = exe

    def name(self):
        return self._name

    def exe(self):
        return self._exe


def test_detect_foreground_activity_classifies_coding(mocker):
    fake_gui = _FakeWin32Gui(hwnd=42, title="Visual Studio Code", class_name="Chrome_WidgetWin_1")
    fake_process = _FakeWin32Process(pid=999)
    mocker.patch.object(psutil, "Process", return_value=_FakeProc("Code.exe", r"C:\VSCode\Code.exe"))

    candidate = detect_foreground_activity(
        platform="win32",
        win32gui_module=fake_gui,
        win32process_module=fake_process,
    )

    assert candidate.category == "coding"
    assert candidate.window.hwnd == 42
    assert candidate.window.pid == 999
    assert candidate.window.process_name == "Code.exe"
    assert candidate.window.process_exe == r"C:\VSCode\Code.exe"
    assert candidate.window.error is None


def test_detect_foreground_activity_classifies_unknown_for_unmapped_app(mocker):
    fake_gui = _FakeWin32Gui(hwnd=99, title="Some App", class_name="SomeClass")
    fake_process = _FakeWin32Process(pid=111)
    mocker.patch.object(psutil, "Process", return_value=_FakeProc("Unknown.exe", r"C:\Unknown.exe"))

    candidate = detect_foreground_activity(
        platform="win32",
        win32gui_module=fake_gui,
        win32process_module=fake_process,
    )

    assert candidate.category == "unknown"
    assert candidate.window.pid == 111
    assert candidate.window.error is None


def test_detect_foreground_activity_returns_unknown_when_no_hwnd():
    fake_gui = _FakeWin32Gui(hwnd=0)
    fake_process = _FakeWin32Process(pid=1)

    candidate = detect_foreground_activity(
        platform="win32",
        win32gui_module=fake_gui,
        win32process_module=fake_process,
    )

    assert candidate.category == "unknown"
    assert candidate.window.hwnd is None
    assert candidate.window.pid is None
    assert candidate.window.error is None
