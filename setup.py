import os
from glob import glob

from setuptools import setup

package_name = "emlid_interface"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "launch"),
            glob(os.path.join("launch", "*launch.[pxy][yma]*")),
        ),
        (os.path.join("share", package_name, "param"), glob("param/*.yaml")),
    ],
    install_requires=["setuptools", "nmea-parser==0.5.0"],
    zip_safe=True,
    maintainer="patrick",
    maintainer_email="patrick.amy@ufl.edu",
    description="TODO: Package description",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "emlid_interface_node = emlid_interface.emlid_interface_node:main"
        ],
    },
)
