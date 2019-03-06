import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='arsenal-america-pub-scraper',
    version='0.0.1',
    author='Matthew Armand',
    author_email='marmand68@gmail.com',
    description='Automated extraction of official Arsenal pubs in America',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/matthewarmand/arsenal-america-pub-scraper',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
