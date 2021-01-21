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
from setuptools import setup, find_packages
from os import path


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="pyxll_pycharm",
    description="Adds PyCharm debugging support to PyXLL.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version="0.1.3",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "pyxll_pycharm": [
            "pyxll_pycharm/resources/ribbon.xml",
            "pyxll_pycharm/resources/debug.png",
        ]
    },
    project_urls={
        "Source": "https://github.com/pyxll/pyxll-pycharm",
        "Tracker": "https://github.com/pyxll/pyxll-pycharm/issues",
    },
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows"
    ],
    entry_points={
        "pyxll": [
            "modules = pyxll_pycharm:modules",
            "ribbon = pyxll_pycharm:ribbon"
        ]
    },
    install_requires=[
        "pyxll >= 5.0.0",
        "pydevd-pycharm"
    ]
)
