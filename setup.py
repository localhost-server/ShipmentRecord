from setuptools import setup, find_packages

setup(
    name="pdf-shipping-extractor",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.24.0",
        "pandas>=1.5.0",
        "openpyxl>=3.0.10",
        "pdfplumber>=0.9.0",
        "anthropic>=0.7.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "flake8>=4.0.0",
        ],
    },
    python_requires=">=3.8",
    author="PDF Shipping Data Extractor",
    description="A Streamlit application that extracts shipping information from PDF courier airway bills using Anthropic AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
