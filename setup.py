from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

def version():
    with open("iutest/_version.py") as f:
        f.readlines()[-1].split()[-1].strip("\"'")

setup(
    name="iutest",
    version=version(),
    description="A Python unittest ui tool that aims to support many unittest frameworks.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mgland/iutest",
    author="Miguel Gao",
    author_email="opensourcemg@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[
        "iutest",
        "iutest.core",
        "iutest.core.testrunners",
        "iutest.dcc",
        "iutest.plugins",
        "iutest.plugins.nose2plugins",
        "iutest.tests",
        "iutest.tests.empty",
        "iutest.tests.iutests",
        "iutest.ui",
    ],
    include_package_data=True,
    install_requires=["reimport", "nose2", "pytest", "pyside2"],
    entry_points={
        "console_scripts": [
            "iutest=iutest.cli:main",
        ]
    },
)