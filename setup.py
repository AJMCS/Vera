from setuptools import setup, find_packages

setup(
    name="search_agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.115.12",
        "uvicorn>=0.34.0",
        "python-dotenv>=1.0.1",
        "sentient-agent-framework>=0.3.0",
    ],
) 