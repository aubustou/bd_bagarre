from setuptools import setup

setup(
    name="bd_bagarre",
    version="0.1",
    packages=["bd_bagarre", "bd_bagarre.model"],
    url="",
    license="MIT",
    author="Aubustou",
    author_email="",
    description="",
    install_requires=[
        "sqlalchemy",
        "apischema",
        "lxml",
        "xmltodict",
        "feedgenerator",
        "fastapi[all]",
        "pymongo",
        "python-magic",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pdbpp",
        ],
    },
    entry_points={
        "console_scripts": [
            "bd-bagarre=bd_bagarre.mongodb_server:main",
        ],
    },
)
