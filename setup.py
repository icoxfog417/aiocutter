from distutils.core import setup

setup(
    name='aiocutter',
    packages=['aiocutter'],
    install_requires=[
        'aiohttp',
        'beautifulsoup4'
    ],
    version='0.0.3',
    description='scraping tool for asyncio',
    author='icoxfog417',
    author_email='icoxfog417@yahoo.co.jp',
    url='https://github.com/icoxfog417/aiocutter',
    download_url='https://github.com/icoxfog417/aiocutter/tarball/master',
    keywords=['asyncio', 'scraping'],
    classifiers=[],
)
