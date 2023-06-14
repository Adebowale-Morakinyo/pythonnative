from setuptools import setup, find_packages

setup(
    name="pythonnative",
    version="0.0.1",
    author="Owen Carey",
    author_email="pythonnative@gmail.com",
    description="A cross-platform Python tool kit for Android and iOS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pythonnative.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "rubicon-objc>=0.4.6,<0.5.0",
        # Add more requirements here as necessary
    ],
)
