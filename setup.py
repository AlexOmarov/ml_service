"""A setuptools based setup module."""
from os import path
from setuptools import setup, find_packages
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ml_service',
    include_package_data=True,
    version='0.0.1',
    description='Microservice which is responsible for working with machine learning stuff.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AlexOmarov/ml_service',
    author='Alex Omarov',
    author_email='dungeonswdragons@gmail.com',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    keywords='Flask Flask-Assets Machine-learning Tensorflow',
    packages=find_packages(),
    install_requires=[
        'Flask~=1.1.2',
        'TensorFlow~=2.2.0rc4',
        'Matplotlib~=3.2.1',
        'Numpy~=1.18.3',
        'Waitress~=1.4.3'
    ],
    extras_require={
        'dev': [''],
        'test': [''],
        'env': ['']
    },
    entry_points={
        'console_scripts': [
            'install=wsgi:__main__',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/AlexOmarov/ml_service/issues',
        'Source': 'https://github.com/AlexOmarov/ml_service/',
    },
)
