from setuptools import setup

setup(name='pingwithbowie',
      version='1.0',
      description='Sing With Bowie Python Backend',
      author='Evgeni Dmitriev',
      author_email='evgeni@odditystudio.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=[
          'redis',
          'twython',
          'flask',
          'requests>=2.9.1',
          'ndg-httpsclient>=0.4.0',
      ],
      )
