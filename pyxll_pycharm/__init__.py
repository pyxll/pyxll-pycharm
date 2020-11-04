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
import pydevd_pycharm
import pkg_resources
import pydevd
import ctypes
import logging
import sys

_log = logging.getLogger(__name__)

_MB_YESNO = 0x04
_MB_OK = 0x0
_IDYES = 0x6


def connect_to_pycharm(*args):
    """Connect to the remote PyCharm debugger."""
    # Get the settings from the config
    port = 5000
    suspend = False

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

        # Try to stop the current debugger (this sets pydevd.connected to False)
        _log.info("Stopping the PyCharm debugger connection...")
        pydevd.stoptrace()

        # Undo the stdout/stderr redirection (not strictly necessary!)
        if hasattr(sys, "_pydevd_out_buffer_") and hasattr(sys, "stdout_original"):
            sys.stdout = sys.stdout_original
            del sys._pydevd_out_buffer_

        if hasattr(sys, "_pydevd_err_buffer_") and hasattr(sys, "stderr_original"):
            sys.stderr = sys.stderr_original
            del sys._pydevd_err_buffer_

    # Connect to the remote debugger
    pydevd_pycharm.settrace("localhost",
                            port=port,
                            suspend=suspend,
                            stdoutToServer=True,
                            stderrToServer=True)

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
    ribbon = pkg_resources.resource_string(__name__, "resources/ribbon.xml")
    return [
        (None, ribbon)
    ]
