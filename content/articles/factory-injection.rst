:title: Factory injection, combining pytest with factory_boy
:date: 2016-04-01 11:02
:summary: Combining best practices of dependency injection and the factory pattern with pytest and factory_boy.
:category: Open source
:author: Oleg Pidsadnyi
:slug: articles/factory-injection-combining-pytest-factory_boy
:tags: open source, python, pytest, pytest-bdd, factory_boy, pytest-factoryboy

****************************************************
Factory injection, combining pytest with factory_boy
****************************************************

.. contents::

The most annoying in writing tests is the setup. All this boilerplate requires so much effort and
thinking. You would prefer to focus on taking an action and asserting the result knowing some precondition, than
diving again and again into researching how to make it happen. It would be nice to have some idea,
some pattern that helps you to get started.

Normally testing tools don't provide any pattern to help you creating the test data.
Developers are just writing chunks of code and create entities imperatively. Then they are trying to
reuse this code, share it between different functions. But as a matter of fact these fixtures
are not refactored too often as too many tests are using them. So the code gets duplicated with lots of flavors.

And in case of BDD it quickly ends up with scripting the creation of an entire hierarchy:

.. code-block:: gherkin

	Scenario: Dark Helmet vs Lone Star v1

		Given I am your father's brother's nephew's cousin's former roommate

		When So what does that make us?

		Then Absolutely nothing

This fixture is a very complicated flavor. Flavors have a huge downside of encapsulating the creation code,
that makes it impossible to reuse and to parametrize, so let's split it:

.. code-block:: gherkin

	Scenario: Dark Helmet vs Lone Star v2
		Given there's a room
		And there's you
		And you have a father
		And your father has a brother
		And your father's brother has a nephew
		And your father's brother's nephew has a cousin
		And there's I am
		And your father's brother's nephew's cousin's lived in the room
		And I lived in the room

		When So what does that make us?

		Then Absolutely nothing

And this is getting even worse, but it is realistic! Imagine how terrible it is to reuse this setup for similar tests.
But there's a solution to that - Gherkin Background section:


.. code-block:: gherkin

	Feature: Spaceballs

		Background:
			Given there's a room
			And there's you
			And you have a father
			And your father has a brother
			And your father's brother has a nephew
			And your father's brother's nephew has a cousin
			And there's I am

		Scenario: Dark Helmet vs Lone Star v3
			Given your father's brother's nephew's cousin's lived in the room
			And I lived in the room

			When So what does that make us?
		
			Then Absolutely nothing

How is it now different from the v1? A lot more paper work and the flavor is still there.
Anyway you have to address that particular person by some symbolic name, especially because these steps
are executed separately and the context is shared between them.

Popular BDD tools are providing this feature, but every step has to come up with certain variable name,
put it in the context, make sure to check if it was already created.
It also implies that the given steps have to be in the certain order which is again too programmatic.


On the other hand most of the systems have statically defined hierarchy. In case you need an object all
non-nullable parents in the hierarchy have to be created, otherwise this object cannot exist. All the preconditions
that make your system valid are not really worth mentioning. This is so called just-enough-specification principle
of Gherkin where you specify only the facts that you need to observe later assuming everything else simply works.

Certain flavors usually also have statically defined roles in the systems with much shorter names.
To achieve that there should be some kind of pattern to make sure all object's dependencies are created without
mentioning them explicitly.

At Paylogic we gained quite some experience by using pytest for more than 7 years, you can read some
`previous articles <http://developer.paylogic.com/articles/how-we-use-pytest-and-pytest-bdd-in-paylogic.html>`_.


Dependency injection
--------------------

The main difference between pytest and the most of the other testing tools is dependency injection.

.. code-block:: python

	@pytest.fixture
	def you(your_father):
		"""You can't be created without your father."""
		...

Basically the entire hierarchy is configured statically in the code as dependencies. It is easy to follow the flow
by looking at definitions. Each fixture cares only about creating itself and ordering all necessary information as
dependencies.

In pytest-BDD we implemented dependency injection support for the steps, so that pytest fixtures are shared among them
instead of the context object that you have to feed in imperative way.

Compared to the other testing tools pytest code has more declarative way rather than imperative and dependencies
allow just-enough-specification.


Ideal test
----------

What would be the ideal test?
I would say the one where I mention only those attributes that make the test case, these values are defined
as close as possible to the test code where I can compare them with the assertion section.

pytest has elegant way to parametrize tests:

.. code-block:: python

	@pytest.mark.parametrize("book__price", [Amount("EUR", "15.20")])
	@pytest.mark.parametrize(
		("author__fee_percent", "expected_author_fee"),
		(
			(27, Amount("EUR", "4.104")),
			(12.5, Amount("EUR", "1.9")),
		),
	)
	def test_unicode(book, expected_author_fee):
		"""Test author fee calculation."""
		assert book.author_fee == expected_author_fee

The only downside of using pytest fixtures is finding their implementation since you don't have to import them.
Fixtures can be inherited and overridden so you are not always sure in what context you are. It would be
nice to have more compact representation of their definitions or to avoid their manual definition completely.

Factory pattern
---------------

There's a great project for Python called factory_boy. It allows creating objects starting on any level of the
model hierarchy also creating all necessary dependencies. Factory pattern solves the problem of the encapsulation
so that any value can passed to any level.

It is declarative, compact and easy to maintain. Factories are look-alike models and provide great overview on
what values attributes will get.

There are post-generation declarations and actions that help you solving problems related to circular dependencies
and to apply some side effects after the object is created.


.. code-block:: python

	import factory
	import faker

	fake = faker.Factory()


	class AuthorFactory(factory.Factory):

		class Meta:
			model = Author

		name = factory.LazyAttribute(lambda f: fake.name())



	class BookFactory(factory.Factory):

		class Meta:
			model = Book

		# Parent object is created at first
		author = factory.SubFactory(AuthorFactory)

		title = factory.LazyAttribute(lambda f: fake.sentence())


	# Create a book with default values.
	book = BookFactory()

	# Create a book with specific title value.
	book_with_title = BookFactory(title='pytest in a nutshell')

	# Create a book parametrized with specific author name.
	book_with_author_name = BookFactory(author__name='John Smith')

	# Creates books with titles "Book 1", "Book 2", "Book 3", etc.
	tons_of_books = BookFactory.create_batch(
		size=100000,
		title=factory.Sequence(lambda n: "Book {0}".format(n)),
	)



The double underscore syntax allows you to address the attribute, the attribute of the attribute etc.
This is nice technique that helps creating complex and large datasets for various needs.

These datasets can be totally parallel hierarchies or a common parent can be passed to bind them,
or even the certain rules how to obtain the parent can be configured on the attribute declaration.

We use it to populate our sandbox environment database with the demo data that 3rd parties can use.

Normally for the well isolated test you don't need the entire hierarchy. It takes too much time and resource
to create everything. It should be like a lightning that is reaching the target following the shortest path,
create only what's necessary to make it work.

Also the tests that are separated in steps want to use only relevant nodes of the hierarchy, not navigating
through entire hierarchy to reach the certain instance or attribute. And this is where pytest good at,
also solving a problem of binding objects to the common parent which is an instance of the fixture in the session.


Factory vs dependency injection
-------------------------------

So just to recap, Factory is good at compact declarative style with the good overview of what would be the values,
flexibility in parametrization on any level of hierarchy.

pytest is good at delivering fully configured fixtures at any point of the test setup, parametrization of the
test case.

What if there could be a way to combine those two to take advantage of:

* Minimum objects creation in the hierarchy path.
* Easily accessed instances of the hierarchy path by conventional names.
* Strong convention of naming attributes for the parametrization.
* Compact declarative notation for the models and attributes.

It is possible to parametrize anything using pytest as long as it is a fixture. It means that we need
fixtures not only for the principal entities, but also for all their attributes.
Since fixture names are unique within the scope of a test session and represent the same instance, the double
underscore convention of a factory_boy can be also applied.


pytest-factoryboy
=================

So I made a library where I'm trying to combine best practices of the dependency injection and the factory pattern.
The main idea is that the logic of creating the attribute is incorporated in the factory attribute declarations
and dependencies are represented by sub-factory attributes.

Basically there's no need in manual implementation of the fixtures since factories can be introspected and fixtures
can be automatically generated. Only registration is needed where you can optionally choose a name of the fixture.


Factory Fixture
~~~~~~~~~~~~~~~

Factory fixtures allow using factories without importing them. Name convention is lowercase-underscore
class name.

.. code-block:: python

    import factory
    from pytest_factoryboy import register

    class AuthorFactory(factory.Factory):

        class Meta:
            model = Author


    register(AuthorFactory)


    def test_factory_fixture(author_factory):
        author = author_factory(name="Charles Dickens")
        assert author.name == "Charles Dickens"

Basically you don't have to be bothered importing the factory at all. The only thing you should keep in mind
is the naming convention to guess the name and just request it in your fixture or your test function.


Model Fixture
~~~~~~~~~~~~~

Model fixture implements an instance of a model created by the factory. Name convention is lowercase-underscore
class name.


.. code-block:: python

    import factory
    from pytest_factoryboy import register

    @register
    class AuthorFactory(Factory):

        class Meta:
            model = Author

        name = "Charles Dickens"


    def test_model_fixture(author):
        assert author.name == "Charles Dickens"


Model fixtures can be registered with specific names. For example if you address instances of some collection
by the name like "first", "second" or of another parent as "other":


.. code-block:: python

    register(BookFactory)  # book
    register(BookFactory, "second_book")  # second_book

    register(AuthorFactory) # author
    register(AuthorFactory, "second_author") # second_author

    register(BookFactory, "other_book")  # other_book, book of another author

    @pytest.fixture
    def other_book__author(second_author):
        """Make the relation of the second_book to another (second) author."""
        return second_author



Attributes are Fixtures
~~~~~~~~~~~~~~~~~~~~~~~

There are fixtures created for factory attributes. Attribute names are prefixed with the model fixture name and
double underscore (similar to factory boy convention).


.. code-block:: python

    @pytest.mark.parametrized("author__name", ["Bill Gates"])
    def test_model_fixture(author):
        assert author.name == "Bill Gates"

SubFactory
~~~~~~~~~~

Sub-factory attribute points to the model fixture of the sub-factory.
Attributes of sub-factories are injected as dependencies to the model fixture and can be overridden_ in
the parametrization.

Related Factory
~~~~~~~~~~~~~~~

Related factory attribute points to the model fixture of the related factory.
Attributes of related factories are injected as dependencies to the model fixture and can be overridden_ in
the parametrization.


post-generation
~~~~~~~~~~~~~~~

Post-generation attribute fixture implements only the extracted value for the post generation function.


Integration
~~~~~~~~~~~

An example of factory_boy_ and pytest_ integration.

factories/__init__.py:

.. code-block:: python

    import factory
    from faker import Factory as FakerFactory

    faker = FakerFactory.create()


    class AuthorFactory(factory.django.DjangoModelFactory):

        """Author factory."""

        name = factory.LazyAttribute(lambda x: faker.name())

        class Meta:
            model = 'app.Author'


    class BookFactory(factory.django.DjangoModelFactory):

        """Book factory."""

        title = factory.LazyAttribute(lambda x: faker.sentence(nb_words=4))

        class Meta:
            model = 'app.Book'

        author = factory.SubFactory(AuthorFactory)

tests/conftest.py:

.. code-block:: python

    from pytest_factoryboy import register

    from factories import AuthorFactory, BookFactory

    register(AuthorFactory)
    register(BookFactory)

tests/test_models.py:

.. code-block:: python

    from app.models import Book
    from factories import BookFactory

    def test_book_factory(book_factory):
        """Factories become fixtures automatically."""
        assert isinstance(book_factory, BookFactory)

    def test_book(book):
        """Instances become fixtures automatically."""
        assert isinstance(book, Book)

    @pytest.mark.parametrize("book__title", ["pytest for Dummies"])
    @pytest.mark.parametrize("author__name", ["Bill Gates"])
    def test_parametrized(book):
        """You can set any factory attribute as a fixture using naming convention."""
        assert book.name == "pytest for Dummies"
        assert book.author.name == "Bill Gates"


Fixture partial specialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a possibility to pass keyword parameters in order to override factory attribute values during fixture
registration. This comes in handy when your test case is requesting a lot of fixture flavors. Too much for the
regular pytest parametrization.
In this case you can register fixture flavors in the local test module and specify value deviations inside ``register``
function call.


.. code-block:: python

    register(AuthorFactory, "male_author", gender="M", name="John Doe")
    register(AuthorFactory, "female_author", gender="F")


    @pytest.fixture
    def female_author__name():
        """Override female author name as a separate fixture."""
        return "Jane Doe"


    @pytest.mark.parametrize("male_author__age", [42])  # Override even more
    def test_partial(male_author, female_author):
        """Test fixture partial specialization."""
        assert male_author.gender == "M"
        assert male_author.name == "John Doe"
        assert male_author.age == 42

        assert female_author.gender == "F"
        assert female_author.name == "Jane Doe"


Fixture attributes
~~~~~~~~~~~~~~~~~~

Sometimes it is necessary to pass an instance of another fixture as an attribute value to the factory.
It is possible to override the generated attribute fixture where desired values can be requested as
fixture dependencies. There is also a lazy wrapper for the fixture that can be used in the parametrization
without defining fixtures in a module.


LazyFixture constructor accepts either existing fixture name or callable with dependencies:

.. code-block:: python

    import pytest
    from pytest_factoryboy import register, LazyFixture


    @pytest.mark.parametrize("book__author", [LazyFixture("another_author")])
    def test_lazy_fixture_name(book, another_author):
        """Test that book author is replaced with another author by fixture name."""
        assert book.author == another_author


    @pytest.mark.parametrize("book__author", [LazyFixture(lambda another_author: another_author)])
    def test_lazy_fixture_callable(book, another_author):
        """Test that book author is replaced with another author by callable."""
        assert book.author == another_author


    # Can also be used in the partial specialization during the registration.
    register(AuthorFactory, "another_book", author=LazyFixture("another_author"))


Post-generation dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike factory_boy which binds related objects using internal container for the lazy evaluations,
pytest-factoryboy relies on the pytest request.

Circular dependencies between objects can be resolved using post-generation hooks/related factories in combination with
passing the SelfAttribute, but in case of pytest request fixture functions have to return values in order to be cached
in the request and to become available to other fixtures.

Thats why evaluation of the post-generation declaration in pytest-factoryboy is deferred until calling
the test function.
This solves circular dependency resolution for situations like:

::

    o->[ A ]-->[ B ]<--[ C ]-o
    |                        |
    o----(C depends on A)----o


On the other hand deferring post-generation declarations evaluation makes their result unavailable during the generation
of objects that are not in the circular dependency, but they rely on the post-generation action.
It is possible to declare such dependencies to be evaluated earlier, right before generating the requested object.

.. code-block:: python

    from pytest_factoryboy import register


    class Foo(object):

        def __init__(self, value):
            self.value = value


    class Bar(object):

        def __init__(self, foo):
            self.foo = foo


    @register
    class FooFactory(factory.Factory):

        """Foo factory."""

        class Meta:
            model = Foo

        value = 0

        @factory.post_generation
        def set1(foo, create, value, **kwargs):
            foo.value = 1


    class BarFactory(factory.Factory):

        """Bar factory."""

        foo = factory.SubFactory(FooFactory)

        @classmethod
        def _create(cls, model_class, foo):
            assert foo.value == 1  # Assert that set1 is evaluated before object generation
            return super(BarFactory, cls)._create(model_class, foo=foo)

        class Meta:
            model = Bar


    register(
        BarFactory,
        'bar',
        _postgen_dependencies=["foo__set1"],
    )
    """Forces 'set1' to be evaluated first."""


    def test_depends_on_set1(bar):
        """Test that post-generation hooks are done and the value is 2."""
        assert depends_on_1.foo.value == 1


All post-generation/RelatedFactory attributes specified in the `_postgen_dependencies` list during factory registration
are evaluated before the object generation.


In case you are using ORM the SQLAlchemy is especially good with post-generation actions. It is as lazy as possible
and doesn't require to bind objects by using constructors or primary keys to be generated.
SQLAlchemy is your friend here.


Hooks
~~~~~

pytest-factoryboy exposes several `pytest hooks <http://pytest.org/latest/plugins.html#well-specified-hooks>`_
which might be helpful controlling database transaction, for reporting etc:

* pytest_factoryboy_done(request) - Called after all factory based fixtures and their post-generation actions were evaluated.


Conclusion
==========

As pytest helps you write better programs, pytest-factoryboy helps you write better tests.
Conventions and limitations allow you to focus on the test rather on test exercise and assertions than implementation
of the complicated setup.

It is easy to parametrize particular low-level attributes of your models, but it is also easy to identify
higher level flags to apply all the side effects for the certain work-flows of your system.

In both cases it is not needed to navigate through files and folders how pytest inherits fixtures to find certain
implementation. It is enough to take a look at the factory classes to get the idea what to expect, but in the most
of the cases it is easy to guess by combining the model name and the attribute name that you know by heart.

It is also a great help in behavioral tests to introduce homogenic given steps and avoid fixture flavors.
Since you are not implementing that much of fixtures manually flavors just don't exist.
Given steps are simply specifying attribute values for the models depending on them or applying some mutations
after the instance is created. And again you are operating only the attributes declared on the factory level
that define your data or dispatch the work-flow of your system.


Future
======

Is there more room to automate? Yes.

Python is amazing dynamic language with a lot of introspection possibilities. Most of the good libraries provide
tools for introspection.

In case of SQLAlchemy and if you are decorating your types with meaningful types, for example by using Email,
Password, Address types from the SQLAlchemy-Utils, you could generate base classes for your factories
and let faker provide with realistic human-readable values.

There's a project that I want to continue on called Alchemyboy that allows generation of the base classes for
factories based on SQLAlchemy models.



Links
=====

* `How we use pytest and pytest-bdd in Paylogic. <http://developer.paylogic.com/articles/how-we-use-pytest-and-pytest-bdd-in-paylogic.html>`_ 
* `pytest - helps you write better programs. <http://pytest.org/latest/>`_
* `pytest-bdd <http://pytest-bdd.readthedocs.org/en/latest/>`_
* `factory_boy <https://factoryboy.readthedocs.org>`_
* `pytest-factoryboy - factory_boy integration with the pytest. <http://pytest-factoryboy.readthedocs.org>`_


.. _overridden: http://pytest.org/latest/fixture.html#override-a-fixture-with-direct-test-parametrization
.. _pytest: http://pytest.org
