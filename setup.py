from setuptools import setup, find_packages

setup(
    name="monadical_event_finder",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "joblib",
        "pandas",
        "pydantic",
        "scikit-learn",
        "sentence_transformers",
        "websockets"
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "event_finder=event_finder.start:main",
        ],
    },
)
