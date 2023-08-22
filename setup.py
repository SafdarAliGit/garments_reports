from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in garments_reports/__init__.py
from garments_reports import __version__ as version

setup(
	name="garments_reports",
	version=version,
	description="this is report application for garments",
	author="Tech Ventures",
	author_email="safar211@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
