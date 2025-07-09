"""
Setup for code-extractor JupyterLab extension
"""

from setuptools import setup, find_packages

setup(
    name="code-extractor",
    version="0.1.0",
    description="A JupyterLab extension to extract code blocks from notebooks to Python files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-username/code-extractor",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "jupyter_server>=1.6,<3",
        "jupyterlab>=4.0.0,<5"
    ],
    extras_require={
        "dev": [
            "jupyter-packaging",
            "jupyterlab>=4.0.0,<5",
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "jupyter_server.extension_points": [
            "code_extractor = code_extractor:_jupyter_server_extension_points"
        ]
    },
)
