from setuptools import setup


def readme():
    src = "./iutest/icons/iutest.svg"
    dst = "http://mgland.com/shared/iutest.svg"
    with open("README.md") as f:
        longDesc = f.read()
    return longDesc.replace(src, dst)


def version():
    with open("iutest/_version.py") as f:
        return f.readlines()[-1].split()[-1].strip("\"'")


setup(
    name="iutest",
    version=version(),
    description="An interactive python test runner supports various test frameworks.",
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
        "Framework :: Pytest",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Unit",
        "Intended Audience :: Developers",
    ],
    packages=[
        "iutest",
        "iutest.core",
        "iutest.core.runners",
        "iutest.dcc",
        "iutest.plugins",
        "iutest.plugins.nose2plugins",
        "iutest.tests",
        "iutest.tests.empty",
        "iutest.tests.iutests",
        "iutest.ui",
    ],
    include_package_data=True,
    install_requires=["reimport"],
    entry_points={"console_scripts": ["iutest=iutest.cli:main"]},
)
