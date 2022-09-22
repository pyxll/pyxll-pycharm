# PyXLL-PyCharm

PyCharm debugging support for PyXLL.

Requires:

- PyXLL >= 5.0.0
- PyCharm Professional

To install this package use:

    pip install pyxll-pycharm

Once installed a "PyCharm Debug" button will be added to the PyXLL ribbon tab in Excel, so
long as you have PyXLL 5 or above already installed.

To debug your Python code running in Excel with PyXLL

1. Create a new Run Configuration in PyCharm using the "Python Debug Server" template. 
2. Install the "pydev-pycharm" package using the exact version specified in your new Run Configuration.
3. Change the port in your Run Configuration to 5000.
4. Run the new Run Configuration using the green "Debug" button in PyCharm.
5. Connect Excel to PyCharm using the "PyCharm Debug" button in Excel.

To configure add the following to your pyxll.cfg file (default values shown):

    [PYCHARM]
    port = 5000
    suspend = 0
    stdout_to_server = 1
    stderr_to_server = 1
    disable_ribbon = 0

For more information about installing and using PyXLL see https://www.pyxll.com.

Copyright (c) PyXLL Ltd
