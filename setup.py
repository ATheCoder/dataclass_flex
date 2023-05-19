from setuptools import setup, find_packages

setup(
    name='dataclass_flex',
    version='0.0.1',
    description='Flexible conversion between dataclasses',
    author='Arash Arbabi',
    author_email='arbabiarash0@gmail.com',
    packages=find_packages(),
    install_requires=[
        'networkx',
        'matplotlib'
    ],
)
