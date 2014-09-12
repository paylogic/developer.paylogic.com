:title: Traduki
:date: 2014-08-27 10:00
:summary: Internationalization made easy with the help of SQLAlchemy.
:category: Open Source
:author: Spyros Ioakeimidis
:slug: articles/traduki
:tags: internationalization, sqlalchemy, python, database, i18n
:email: spyrosikmd@gmail.com

.. contents:: Table of Contents
   :depth: 2

Introduction
============

``traduki`` is an `open source <https://github.com/paylogic/traduki>`_
package, which consists of internationalization helper classes targeted for
SQLAlchemy-based python projects. The advantage of using ``traduki`` is that
it removes the burden of defining translation tables, and provides
a consistent, intuitive and easy way to introduce internationalization into
your application. Minimalistic design allowed us to use only
`SQLAlchemy <http://www.sqlalchemy.org/>`_ as a python dependency.

Why we were in a need of something different
============================================

As Paylogic operates in several countries, internationalization is a strong
requirement. However, we used to do internationalization differently from how
we do it these days. Our former approach was to join translation tables in order
to obtain the translations. This allowed us to search on the internationalized
fields, but it required a lot of joins, even in cases where searching was not a requirement.
We could either `eager load <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#eager-loading>`_,
load relationships at the same time the parent is loaded, or
`lazy load <http://docs.sqlalchemy.org/en/rel_0_9/glossary.html#term-lazy-loading>`_,
load relationships the first time they are accessed. When we lazy load,
and access an internationalized property, we cause two queries per property.

One of these queries is to the translations table, and the other one
to a table with only the ids. The translations table had one translation per
row, which made it inefficient and difficult to get all the translations for
all the properties in one row. For example,

====  ===============  ========= ================
 Translation
-------------------------------------------------
 id    language_code    text_id   localized_text
====  ===============  ========= ================
1     en               10        English title 1
2     nl               10        Dutch title 1
3     en               11        English subtitle
4     nl               11        Dutch subtitle
5     en               12        English title 2
6     nl               12        Dutch title 2
====  ===============  ========= ================

where the :code:`text_id` references the :code:`title_id` and
:code:`subtitle_id` fields from a hypothetical :code:`Event` table.

====  ==========  =============
 Event
-------------------------------
 id    title_id    subtitle_id
====  ==========  =============
1     10          11
2     12          13
====  ==========  =============

This approach was inefficient because for ``n`` properties and ``m``
languages, we would need to do ``n*m`` joins. The difficult part comes from
the fact that it was cumbersome to write those queries. In the case of
the previous example,

.. code-block:: python

    a_alias = aliased(Translation)

    q = session.query(Event).\
        join(Translation).\
        filter(Translation.text_id==Event.title_id).\
        filter(a_alias.text_id==Event.subtitle_id).\
        filter(Event.id.in_(event_ids)).\
        all()

The end-result was that we did not do this, and we were doing more one-row queries.
We should mention that normally we don't need objects to have dynamic list
of available languages. Maybe it is a strict requirement in other use cases,
but in our use case it is enough to just use a static set of available languages,
which change infrequently.

Another issue with this approach was that the number of results returned from
queries was not deterministic, and required left joins which is even worse
performance-wise. Most of the time you want to eager load relationships.
However, in this case you can never apply a limit or offset because you cannot
trust the number of rows returned.

The aforementioned approach had performance issues. We wanted to be able to
search on the internationalized fields and search fast, which was not possible.
Another requirement was that we wanted language chains. What this means is that
if your language is Dutch, but only the English version of the text is
available, we should display by default the English version of it.

Advantages of the new design
============================

In the end, taking into consideration our motivation and requirements, we came up
with our solution on how to solve the problem of i18n. The following
example illustrates our current approach using ``traduki``. Let's assume that we
have a table :code:`Event`, and we want the ``title`` and ``subtitle`` to be
translated into English and Dutch. The :code:`Event` table contains the ids of
the fields that we wish to have available in those two languages. Let's also
assume that for the event with :code:`id = 8`, the Dutch translation is not
available.

====  ==========  =============
 Event
-------------------------------
 id    title_id    subtitle_id
====  ==========  =============
5     10          11
...   ...         ...
8     25          26
====  ==========  =============

The :code:`Translation` table would then contain a reference to those fields
that we wish to have translated. The :code:`id = 10` for the ``title`` and
:code:`id = 11` for the ``subtitle`` of the first event, and :code:`id = 25`
and :code:`id = 26` for the ``title`` and ``subtitle`` for the second event
respectively. It also contains the translated texts in English and Dutch
(only for the first event). With this approach, we can easily get the
translated texts by joining the :code:`Event` and :code:`Translation` tables.

====  ===================  ===================
 Translation
----------------------------------------------
 id    en                    nl
====  ===================  ===================
10     English title 1      Dutch title 1
11     English subtitle 1   Dutch subtitle 1
...    ...                  ...
25     English title 2
26     English subtitle 2
====  ===================  ===================

The advantage of this approach is that with a simple join between these tables
on the id of the text (for example the ``title_id``), we get one row with all
the translations.

.. code:: python

    q = session.query(Translation).join(Event, Event.title_id==Translation.id)

As can be seen from the query, for ``n`` properties and ``m`` languages,
the number of joins is reduced from ``n*m`` to ``n``, making them also more
intuitive since all translated items are foreign keys to the :code:`Translation`
table, joining once per foreign key. Additionally, ``traduki`` returns a user-friendly
format of this result as a dictionary of language codes and translations. For example:

.. code-block:: python

    {'en': 'English title 1', 'nl': 'Dutch title 1'}

In case of the second event, where the Dutch translation is not available,
``traduki`` falls back to the language that we have defined, in this
case English. So it will return:

.. code-block:: python

    {'en': 'English title 2', 'nl': 'English title 2'}

This approach has one drawback. When a new language is introduced then we need
to alter the translations table to include it. This operation can be expensive.
This was by design so we were aware of our use case. We found out that
the gains in performance are higher, because we search and sort much more often
than we add new languages. However, the most important things for us is not
adding new languages but having a static set of available languages.

How it works
============

``traduki`` is very simple to use. The following example is a concise and
stand-alone application that illustrates the use of ``traduki``. It is
split in parts, to better explain how each part works.

Example
-------

The first part is straightforward. We do standard sqlalchemy imports,
create the engine (in this case the database will be in memory), and define the
declarative base for our models.

.. code-block:: python

    import traduki

    from sqlalchemy import create_engine, Column, Integer
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite://')

    Base = declarative_base()

The next part is where ``traduki`` is used. We define two callbacks, one
for getting the current language and one for getting the language chain. Here
we just return hard coded data for simplicity. We could read this data from a
current ``request`` object, for example using `Flask <http://flask.pocoo.org/>`_
request, something like :code:`flask.request.locale` to get the current language.
We use these callbacks when we deal with the initialization of the :code:`i18n_attributes`.
``traduki`` at the moment of initialization declares the model for the translations
dynamically and sets up all the appropriate relationships.

.. code-block:: python

    def get_current_language():
        """Current language callback for our project."""
        return 'en'


    def get_language_chain():
        """Language chain (fall-back rule) callback for our project."""
        return {'*': 'en'}

    i18n_attributes = traduki.initialize(
        Base, ['en', 'nl'], get_current_language, get_language_chain)

The language list that we pass to :code:`traduki.initialize` function is used
to declare language columns in translations model. So if we use :code:`['en', 'nl']`
the resulting translations model would be something similar to the following declaration.

.. code-block:: python

    class Translation(Base):

        __tablename__ = 'traduki_translation'

        id = Column(Integer, primary_key=True)

        en = Column(UnicodeText, nullable=True, index=True)
        nl = Column(UnicodeText, nullable=True, index=True)

Back to our example, we define our model and use the column and relation provided by
``traduki``. The rest is just to have a complete and running example.

.. code-block:: python

    class Model(Base):

        __tablename__ = 'model'

        id = Column(Integer, primary_key=True)

        title_id = i18n_attributes.i18n_column(nullable=False, unique=False)
        title = i18n_attributes.i18n_relation(title_id)
        """Title."""

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    model = Model()
    model.title = {'en': 'English title', 'nl': 'Dutch title'}
    session.add(model)
    session.commit()

    session.refresh(model)

    assert model.title.get_dict() == {'en': 'English title', 'nl': 'Dutch title'}
    assert model.title.en == 'English title'

To run this example, copy and paste these parts in an ``example.py`` file, and
use the following commands to install the required packages and run the
example:

.. code-block:: bash

    virtualenv env

    source env/bin/activate

    pip install sqlalchemy traduki

    python example.py

Querying
--------

Querying translations can also be done using usual SQLAlchemy techniques.
From the previous example, lets assume that we want to get all :code:`Model`
instances that have English translation for their :code:`title`.

.. code-block:: python

    english_title_objects = (
        session.query(Model)
        .join(
            i18n_attributes.Translation,
            Model.title_id == i18n_attributes.Translation.id)
        .filter(i18n_attributes.Translation.en.isnot(None))
        .all()
    )

:code:`i18n_attributes.Translation` is the translations model declared during initialization
of ``traduki``. It provides helper methods to get the text of a specified language
and get the available languages as a dictionary. It also contains language fields as attributes,
which is nice as it enables directly attribute access to get a language for a specific field
:code:`model.title.en`.

Similar projects
================

We conducted research on how to make an efficient design. We tried lots of
ways to minimize the timing of the queries for large datasets. Also we've looked
around for existing solutions, such as `SQLAlchemy-i18n <https://github.com/kvesteri/sqlalchemy-i18n>`_.

The approach of this project is to create a separate translations table and each row in the table
is a translation in a specific language for a specific field. This is similar to our
previous approach and has the same limitations in performance. You need to explicitly
query for languages and fields and do lots of joins. In our case, you load all the languages
and translations for a field. This might sound like a lot of overhead at first, but in modern
applications you usually have 10-12 languages and you want them to be available all at once in
the client.

Conclusion
==========

Before ``traduki``, there was little done in i18n in open source.  We are waiting for your feedback
and recommendations. Check `traduki <https://github.com/paylogic/traduki>`_ in our github profile.
