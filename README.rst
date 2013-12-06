Paylogic developer portal
=========================

This repository contains the sources for the Paylogic developer portal hosted
at developer.paylogic.com_. We use the static site generator Pelican_ to
generate the web pages from content written in the reStructuredText_ format.

The git repository is hosted on our GitHub_ account and we use `GitHub Pages`_
with a custom DNS name for hosting.

Running it locally
------------------

To run the developer portal locally (e.g. to easily preview changes) the
following steps should help you get started::

  # Clone the git repository.
  git clone git@github.com:paylogic/dev-portal.git

  # Create, activate and initialize the virtual environment.
  virtualenv ~/.virtualenvs/dev-portal
  source ~/.virtualenvs/dev-portal/bin/activate
  pip install -r dev-portal/requirements.txt

  # Run Pelican and view the result in a web browser.
  cd dev-portal
  make devserver
  gnome-open http://127.0.0.1:8000

Publishing changes
------------------

If you 1) followed the steps above, 2) have push access to ``paylogic/dev-portal``
and 3) have activated the virtual environment, then all you need to publish the
latest changes to the live website is to run the command ``make github``. This
will publish your changes using `GitHub Pages`_.

License
-------

This work is licensed under the `Creative Commons Attribution-ShareAlike 3.0
Unported License`_.

.. External references:
.. _Creative Commons Attribution-ShareAlike 3.0 Unported License: http://creativecommons.org/licenses/by-sa/3.0/
.. _developer.paylogic.com: http://developer.paylogic.com/
.. _GitHub Pages: http://pages.github.com/
.. _GitHub: https://github.com/paylogic
.. _Pelican: http://docs.getpelican.com/en/3.2/getting_started.html
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
