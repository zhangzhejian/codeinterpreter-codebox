import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="",
    version="0.0.1",
    author="Zhejian Zhang",
    author_email="527284545@qq.com",
    install_requires=requirements,
    description="Backend for Code Interpreter for Feishu",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
