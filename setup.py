from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vcf2pd4qc',
    version='0.0.1-dev',
    author="ACEnglish",
    author_email="acenglish@gmail.com",
    url="https://github.com/acengish/vcf2pd4qc",
    packages=['vpq', 'vpq/stats', 'vpq/examples'],
    license='MIT',
    scripts=["bin/vpq"],
    description="Library that assists the analysis of VCF files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        "joblib==0.14.1",
        "pysam==0.15.4",
        "seaborn==0.9.1",
        "pandas==0.24.2",
        "numpy==1.18.1",
    ],
)
