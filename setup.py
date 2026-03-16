from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyhunter',
    packages=['pyhunter'],
    version='2.0',
    description='An (unofficial) Python wrapper for the Hunter.io API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Quentin Durantay',
    author_email='quentin.durantay@gmail.com',
    url='https://github.com/VonStruddle/PyHunter',
    download_url='https://github.com/VonStruddle/PyHunter/archive/121.tar.gz',
    license='MIT',
    install_requires=['requests>=2.20.0'],
    keywords=['hunter', 'hunter.io', 'lead generation', 'lead enrichment'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Utilities'
    ],
)
