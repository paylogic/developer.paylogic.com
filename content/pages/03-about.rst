:title: About

This website is built using Pelican_, a static site generator written in
Python. The input files are reStructuredText_ files stored in a git repository.
Right now the generated files are uploaded to an Amazon S3 bucket but we're
planning to use `GitHub Pages`_ to publish this website. This will make it
easy for the engineering and operational IT teams of Paylogic to manage the
content of this website.

Getting started
~~~~~~~~~~~~~~~

Here's how you get a copy of the git repository, create a virtual environment,
install the dependencies and generate an up to date copy of the static pages:

.. code-block:: sh

  git clone ssh://code.paylogic.eu//var/git/users/peter/devportal
  cd devportal
  mkvirtualenv devportal
  pip install -r requirements.txt
  pelican .

After this is done you'll find a static copy of the website in ``output/``.

Why Pelican?
~~~~~~~~~~~~

Because Pelican_ is nice! We found it through a comment on a Hacker News
post: https://news.ycombinator.com/item?id=4858738.

Why GitHub Pages?
~~~~~~~~~~~~~~~~~

Because `GitHub Pages`_ are dead simple to use, everyone who needs write access
already has it (by joining the Paylogic organization on GitHub) and we can set
up a custom DNS name instead of sticking to the ugly defaults.

.. External references:
.. _GitHub Pages: http://pages.github.com/
.. _Pelican: http://docs.getpelican.com/en/3.2/getting_started.html
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
