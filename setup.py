# setup.py
from setuptools import find_packages, setup

setup(
    name="audioNER",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "audioNER-cli = audioNER.app_client:main",
        ],
    },
    install_requires=[
        # Add dependencies here
    ],
)
