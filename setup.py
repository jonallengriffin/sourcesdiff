# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup

PACKAGE_VERSION = '0.1'

# dependencies
deps = ['beautifulsoup4 >= 4.2.1']

setup(name='sourcesdiff',
      version=PACKAGE_VERSION,
      description="Library to compare two B2G sources.xml",
      long_description="",
      classifiers=[],
      keywords='mozilla',
      author='Mozilla Automation and Testing Team',
      author_email='tools@lists.mozilla.org',
      url='https://wiki.mozilla.org/Auto-tools/',
      license='MPL',
      packages=['sourcesdiff'],
      include_package_data=True,
      zip_safe=False,
      install_requires=deps,
      entry_points="""
      """,
      )
