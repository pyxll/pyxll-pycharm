from os.path import expandvars
from itertools import chain
from glob import glob
from pathlib import Path
from functools import lru_cache
import contextlib
import logging
import sys

_log = logging.getLogger(__name__)


@contextlib.contextmanager
def _restore_sys_modules():
    # Take a copy of sys.modules and sys.path
    sys_modules = dict(sys.modules)
    sys_path = list(sys.path)

    yield

    # Restore sys.modules and sys.path
    sys.modules.clear()
    sys.modules.update(sys_modules)
    sys.path.clear()
    sys.path.extend(sys_path)


def _path_is_relative_to(a, b):
    # Path.is_relative_to is new in Python 3.9
    try:
        Path(a).relative_to(b)
        return Path(a).relative_to(b)
    except ValueError:
        return False


@lru_cache(maxsize=2)
def _import_pydevd(apply_fix=True):
    """Imports pydevd_pycharm and pydevd from the pydevd_pycharm package.
    Manipulates sys.modules and sys.path to try and import the right packages.
    This works around issues with debugpy also being installed.
    See https://youtrack.jetbrains.com/issue/PY-40661/pydevd-pycharm-conflicts-with-pydevd-package.
    """
    # If apply_fix is False then simply import and return the modules
    if not apply_fix:
        import pydevd_pycharm
        import pydevd

        pydevd_pycharm_dir = Path(pydevd_pycharm.__file__).parent
        pydevd_dir = Path(pydevd.__file__).parent
        if pydevd_pycharm_dir != pydevd_dir:
            _log.warning("Potential pydevd version conflict found. " +
                         f"Try uninstalling pydevd from '{pydevd_dir}' and reinstall pydevd_pycharm.")

        return pydevd_pycharm, pydevd

    try:
        # Try importing pydevd_pycharm from the default sys.path first
        import pydevd_pycharm
    except ImportError:
        # If that fails look for PyCharm and add it to sys.path
        _log.debug("pydevd_pycharm not found on sys.path. Looking for PyCharm install...")
        pydevd_eggs = list(reversed(sorted(chain.from_iterable(
            glob(expandvars(f"{env_var}\\JetBrains\\PyCharm*\\debug-eggs\\pydevd-pycharm.egg"), recursive=True)
            for env_var in ("${ProgramFiles}", "${ProgramFiles(x86)}")))))

        if pydevd_eggs:
            pydevd_egg = pydevd_eggs[0]
            _log.debug(f"Found pydevd-pycharm in PyCharm install: {pydevd_egg}")
            sys.path.insert(0, pydevd_egg)

    # Try to import pydevd_pycharm again (sys.path may have changed)
    import pydevd_pycharm

    # Next import pydev
    import pydevd

    # pydevd should be distributed as part of pydevd_pycharm
    pydevd_pycharm_dir = Path(pydevd_pycharm.__file__).parent
    pydevd_dir = Path(pydevd.__file__).parent
    if pydevd_pycharm_dir != pydevd_dir:
        _log.debug(f"Attempting to work around incompatible version of pydevd found: {pydevd.__file__}")

        # Remove all the existing pydevd modules from sys.modules
        pydev_modules = set()
        for name, module in sys.modules.items():
            if ((name.startswith("pydev") or name.startswith("_pydev"))
                    and (_path_is_relative_to(module.__file__, pydevd_dir) or
                         _path_is_relative_to(module.__file__, pydevd_pycharm_dir))):
                pydev_modules.add(name)

        for name in pydev_modules:
            del sys.modules[name]

        # Re-import pydevd_pycharm and pydevd with the PyCharm path appearing first on sys.path
        sys.path.insert(0, str(pydevd_pycharm_dir))
        import pydevd_pycharm
        import pydevd

        # Check what we've imported is now correct
        pydevd_pycharm_dir = Path(pydevd_pycharm.__file__).parent
        pydevd_dir = Path(pydevd.__file__).parent
        if pydevd_pycharm_dir != pydevd_dir:
            _log.warning("Potential pydevd version conflict found. " +
                         f"Try uninstalling pydevd from '{pydevd_dir}' and reinstall pydevd_pycharm.")

    return pydevd_pycharm, pydevd


@contextlib.contextmanager
def use_pycharm_pydevd(apply_fix=True):
    """Context manager that imports pydevd_pycharm and pydevd
    and ensures that sys.path includes the pycharm_pydevd path
    for any late imports.
    """
    if not apply_fix:
        yield _import_pydevd(apply_fix)
        return

    with _restore_sys_modules():
        pydevd_pycharm, pydevd = _import_pydevd(apply_fix)

        # Make sure that pydevd_pycharm.__file__ is first on the path
        if apply_fix:
            pycharm_dir = str(Path(pydevd_pycharm.__file__).parent)
            if sys.path[0] != pycharm_dir:
                sys.path.insert(0, sys.path.dirname(pydevd_pycharm.__file__))

        yield pydevd_pycharm, pydevd
