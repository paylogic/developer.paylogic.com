:title: Traduki
:date: 2014-06-17 10:00
:summary: Internationalisation helper classes for SQLAlchemy-based projects
:category: Open Source
:author: Spyros Ioakeimidis
:slug: articles/traduki
:tags: internationalisation, sqlalchemy, python

.. contents::

Introduction
============

The :code:`traduki` package provides internationalisation helper classes for
SQLAlchemy-based projects.

Motivation
==========

Our former approach was to store the translations in tables. Then join
the tables in order to obtain the translations. This allowed us to search on
the internationalized fields, but it required us to make a lot of joins, even
in cases where searching was not required. When we would not eagerly join, and
we would access an internationalized property, we would cause two queries per
property.

One of the queries is to table with the translations, and another is a to a table with only the ids.

The translations table has one translation per row, which makes it inefficient and difficult to get all the translations for all the properties in one row:

Inefficient because for n properties and m languages, you need nm joins.
Difficult because it's cumbersome to write these queries (it's already cumbersome in raw sql, more so in SQLAlchemy). So, we don't do it, and so we do more one-row queries.

performance issues

we want to be able to search on the internationalized fields fast

we want language chains, which means that if your language is Dutch but the
item has only an English field, we will display it in English.

Design
======

Usage
=====

:code:`traduki` is very simple to use.

.. code-block:: python

    import traduki

    from sqlalchemy import create_engine, Column, Integer
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker


    engine = create_engine('sqlite://')

    Base = declarative_base()


    def get_current_language():
        """Current language callback for our project."""
        return 'en'


    def get_language_chain():
        """Language chain (fallback rule) callback for our project."""
        return {'*': 'en'}

    i18n_attributes = traduki.initialize(
        Base, ['en', 'nl'], get_current_language, get_language_chain)


    class MyModel(Base):

        __tablename__ = "mymodel"

        id = Column(Integer, primary_key=True)
        title_id = i18n_attributes.i18n_column(nullable=False, unique=False)
        title = i18n_attributes.i18n_relation(title_id)
        """Title."""

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    sess = Session()

    model = MyModel()
    model.title = {'en': 'English title', 'nl': 'Dutch title'}
    sess.add(model)
    sess.commit()

    sess.refresh(model)
    model = sess.query(MyModel).first()

    assert model.title.get_dict() == {'en': 'English title', 'nl': 'Dutch title'}


Conclusion
==========

one constraint is the sqlalchemy requirement
