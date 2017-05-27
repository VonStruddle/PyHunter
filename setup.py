from setuptools import setup


setup(
    name='pyhunter',
    packages=['pyhunter'],
    version='0.2',
    description='An (unofficial) Python wrapper for the Hunter.io API',
    author='Quentin Durantay',
    author_email='quentin.durantay@gmail.com',
    url='https://github.com/VonStruddle/PyHunter',
    download_url='https://github.com/VonStruddle/PyHunter/archive/0.1.tar.gz',
    install_requires=['requests'],
    keywords=['hunter', 'hunter.io', 'lead generation', 'lead enrichment'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
    ],
)
