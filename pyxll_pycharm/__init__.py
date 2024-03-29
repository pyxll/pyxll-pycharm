"""
PyXLL-PyCharm

PyCharm debugging support for PyXLL.

Requires:
    - PyXLL >= 5.0.0
    - PyCharm Professional

To install this package use::

    pip install pyxll_pycharm

To configure add the following to your pyxll.cfg file::

    [PYCHARM]
    port = 5000
    suspend = 0
"""
from pyxll import get_config
import pkg_resources
import ctypes
import logging
import sys

_log = logging.getLogger(__name__)

_MB_YESNO = 0x04
_MB_OK = 0x0
_IDYES = 0x6


def connect_to_pycharm(*args):
    """Connect to the remote PyCharm debugger."""
    # Defer importing pydevd until it's actually needed as it will conflict with using
    # other debuggers such as VS Code.
    import pydevd_pycharm
    import pydevd

    # Get the settings from the config
    port = 5000
    suspend = False
    stdout_to_server = True
    stderr_to_server = True

    cfg = get_config()
    if cfg.has_option("PYCHARM", "port"):
        try:
            port = int(cfg.get("PYCHARM", "port"))
        except (ValueError, TypeError):
            _log.error("Unexpected value for PYCHARM.port.")

    if cfg.has_option("PYCHARM", "suspend"):
        try:
            suspend = bool(int(cfg.get("PYCHARM", "suspend")))
        except (ValueError, TypeError):
            _log.error("Unexpected value for PYCHARM.suspend.")

    if cfg.has_option("PYCHARM", "stdout_to_server"):
        try:
            stdout_to_server = bool(int(cfg.get("PYCHARM", "stdout_to_server")))
        except (ValueError, TypeError):
            _log.error("Unexpected value for PYCHARM.stdout_to_server.")

    if cfg.has_option("PYCHARM", "stderr_to_server"):
        try:
            stderr_to_server = bool(int(cfg.get("PYCHARM", "stderr_to_server")))
        except (ValueError, TypeError):
            _log.error("Unexpected value for PYCHARM.stderr_to_server.")

    # If the debugger is not already running ask the user if they have started the debug server
    if not pydevd.connected:
        result = ctypes.windll.user32.MessageBoxA(
            0,
            b"Have you started the PyCharm remote debugger on port %d?" % port,
            b"PyCharm Remote Debug",
            _MB_YESNO)

        if result != _IDYES:
            ctypes.windll.user32.MessageBoxA(
                0,
                b"Please start the PyCharm remote debugger on port %d first." % port,
                b"PyCharm Remote Debug",
                _MB_OK)
            return
    else:
        # The debugger is already running so check if the user has restarted the debug server
        result = ctypes.windll.user32.MessageBoxA(
            0,
            b"The PyCharm debugger was already connected.\n" +
            b"Have you re-started the PyCharm remote debugger on port %d?" % port,
            b"PyCharm Remote Debug",
            _MB_YESNO)

        if result != _IDYES:
            ctypes.windll.user32.MessageBoxA(
                0,
                b"Please re-start the PyCharm remote debugger on port %d first." % port,
                b"PyCharm Remote Debug",
                _MB_OK)
            return

        # Call stoptrace (this sets pydevd.connected to False)
        _log.debug("Disconnecting from the PyCharm debugger...")
        pydevd.stoptrace()

        # Undo the stdout/stderr redirection (not strictly necessary!)
        if hasattr(sys, "_pydevd_out_buffer_") and hasattr(sys, "stdout_original"):
            sys.stdout = sys.stdout_original
            del sys._pydevd_out_buffer_

        if hasattr(sys, "_pydevd_err_buffer_") and hasattr(sys, "stderr_original"):
            sys.stderr = sys.stderr_original
            del sys._pydevd_err_buffer_

        # End the debugging session and kill all the pydevd threads
        pydb = pydevd.get_global_debugger()
        pydb.finish_debugging_session()
        pydevd.kill_all_pydev_threads()

        # Wait for all the pydevd threads to end
        _log.debug("Waiting for the pydevd threads to finish.")
        threads = list(pydevd.PyDBDaemonThread.created_pydb_daemon_threads.keys())
        for thread in threads:
            thread.join(timeout=1.0)
            if thread.is_alive():
                raise RuntimeError("Timed out waiting for pydevd thread to terminate.")

    # Connect to the remote debugger
    _log.debug("Connecting to the PyCharm debugger...")
    pydevd_pycharm.settrace("localhost",
                            port=port,
                            suspend=suspend,
                            stdoutToServer=stdout_to_server,
                            stderrToServer=stderr_to_server)

    # Reset excepthook to the default to avoid a PyCharm bug
    sys.excepthook = sys.__excepthook__

    ctypes.windll.user32.MessageBoxA(
        0,
        b"You are now connected to the PyCharm debugger.",
        b"PyCharm Remote Debug",
        _MB_OK)


def modules():
    """Entry point for getting the pyxll modules.
    Returns a list of module names."""
    return [
        __name__
    ]


def ribbon():
    """Entry point for getting the pyxll ribbon file.
    Returns a list of (filename, data) tuples.
    """
    cfg = get_config()

    disable_ribbon = False
    if cfg.has_option("PYCHARM", "disable_ribbon"):
        try:
            disable_ribbon = bool(int(cfg.get("PYCHARM", "disable_ribbon")))
        except (ValueError, TypeError):
            _log.error("Unexpected value for PYCHARM.disable_ribbon.")

    if disable_ribbon:
        return []

    ribbon = pkg_resources.resource_string(__name__, "resources/ribbon.xml")
    return [
        (None, ribbon)
    ]
