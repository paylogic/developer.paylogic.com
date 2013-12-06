Extended authors plugin
=======================

The extended authors plugin for Pelican provides a context generator so you can include a biography with an author.
It is compatible with the default author pages generator, so there is very little to modify.


How to install/use
------------------

* Create a 'authors' folder in your content folder or set `settings.AUTHOR_DIR`

* In your Pelican settings file:
    * `ARTICLE_EXCLUDES = ('pages', 'authors')`
    * `PAGE_EXCLUDES = ('authors',)`
    * `PLUGINS = ('plugins.pelican_extended_authors',)`

* For each author you want to have a biography, create a file in the authors folder. 
  The file need to have a slug property, corresponding with the author's slug.

* Include the data in your author.html and authors.html templates. 
  You can print the biography with: `{{ authors_info.get(author) }}`, 
  where `author` corresponds with an instantiated author object which should be provided by pelican.


Questions, comments, etcetera
-----------------------------

Please do not open an issue for plugin related actions in the issue tracker here. This is not the final place for this plugin to live, we are planning on releasing it seperately. If you do want to communicate with the developer of this plugin, send an email to maikel.wever@paylogic.eu.


Legal matter
------------

This plugin is licenced the same as the content of the Paylogic developer portal, under a `Creative Commons Attribution-ShareAlike 3.0
Unported License`_. The plugin was developed by Maikel Wever (maikel.wever@paylogic.eu).


.. External references:
.. _Creative Commons Attribution-ShareAlike 3.0 Unported License: http://creativecommons.org/licenses/by-sa/3.0/

