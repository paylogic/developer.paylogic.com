:title: pytest-bdd: Behavioral Driven Development with the PyTest
:summary: Paylogic has quite long experience with the PyTest, mainly for the unit testing, but for the functional testing the RobotFramework was used which didn't have the same code reusability. This article is about how we switched to pytest-bdd our experience of unifying the functional and unit testing.
:category: Dev
:author: Oleg Pidsadnyi
:date: 2013-08-27 17:22
:slug: articles/pytest-bdd
:tags: python, pytest, bdd, gherkin, cucumber, testing

Paylogic has quite long experience with the py.test, mainly for the unit testing,
but for the functional testing the RobotFramework was used which didn't have the
same code re-usability.
This article is about how we switched to pytest-bdd our experience of unifying
the functional and unit testing.

.. contents::


BDD
###

Companies with long-term own projects like SaaS have to be up to date with the
market. Thats why there are usually several product managers responsible for the
different business interests.

These people of course have technical background, but often not in the company's primary technology.
The idea of BDD is to formalize the input of requirements and automate their testing.

Gherkin
=======

Gherkin serves both purposes of documenting requirements and testing them.
Pretty clear structure allows just-enough requirement specification and prevents
overlapping of requirements.

.. code-block:: gherkin


	Feature: Some terse yet descriptive text of what is desired
		In order to realize a named business value
		As an explicit system actor
		I want to gain some beneficial outcome which furthers the goal

		Scenario: Some determinable business situation
			Given some precondition
			And some other precondition

			When some action by the actor
			And some other action
			And yet another action

			Then some testable outcome is achieved
			And something else we can check happens too


What BDD is good for?
=====================

	- Specifications are written by non-technical people
	- Executed step-by-step
	- Testing without misinterpretation of the requirements

Our product management team picked up the Gherkin way of writing requirements relatively easily.
We also find it useful as the ultimately short summary of the documentation.

Whats wrong with BDD?
=========================

	- Too explicit/verbose while should be just-enough specification
	- Too many choices, too hard to stick to limitations
	- Keywords with flavors are not reusable

Without the recommendations or enforced guidelines it is very hard to follow the
just-enough specification in requirement declarations. Therefore, it is
important to use some kind of framework that would help to follow the BDD ideas.

Existing tools in Python
========================

Before adopting BDD we looked at the existing solutions.

Some of them were nice, but the way the test condition are being set up did not
satisfy us.The reason is that we always compared the setup of a test to our
experience with the unit testing where the problem of the test setup was already
solved.

RobotFramework
--------------

In the beginning we found the RobotFramework to be an easy tool to start writing
the functional tests. It has a freedom of scripting, a library with the bindings
to selenium webdriver and a possibility to write code in Python.

Later the lack of limitations became a reason the BDD was not used as intended.
Feature descriptions became programmatic with the variables in the text files.
The scenarios contained overlapping requirements. A pattern of scripting actions
appeared for complex scenarios which contained a chain of When-Then-When-Then
sections to observe the results.

Due to the complex system domain the Given sections contained a lot of detailed
and not reusable keywords. It happened because RobotFramework does not provide
means to setup a test and pass a shared stated across keywords.

We had to implement state sharing between keywords ourselves and learned from
it...

Splinter
--------

Unlike the RobotFramework most of the BDD tools map the python code to Gherkin
features. That keeps the feature files clean, browsable and readable. In addition it allows having
a nice overview of the functionality of the system.

Also they use Splinter - a pythonic webdriver that inherits some problems of the selenium, but
it is much more convenient to use (than for example robotframework-seleniumlibrary).

However the proper waiting for timeouts, until the element appears on the page or
until the end of the javascript activity still had to be implemented and monkeypatched.

Lettuce and Splinter
--------------------

Lettuce has its own runner which implements a context objects, which steps
use to communicate the state.

The context is implemented as global variables.

	"For the sake of turning easier and funnier to write tests, lettuce “violates” some principles of good design in python, such as avoiding implicity and using global stuff.
	The “world” concept of lettuce is mostly about “global stuff”."

	-- http://lettuce.it/reference/terrain.html#lettuce-world

Example:

.. code-block:: python


	@step('I have the number (\d+)')
	def have_the_number(step, number):
	    world.number = int(number)

Behave and Splinter
-------------------

The context object is explicitly passed to each step.

	"You’ll have noticed the “context” variable that’s passed around.
	It’s a clever place where you and behave can store information to share around.
	It runs at three levels, automatically managed by behave."

	-- http://pythonhosted.org/behave/tutorial.html#context

Example:

.. code-block:: python


	@given('I search for a valid account')
	def step_impl(context):
	   context.browser.get('http://localhost:8000/index')
	   form = get_element(context.browser, tag='form')
	   get_element(form, name="msisdn").send_keys('61415551234')
	   form.submit()


Freshen and Splinter
--------------------
Context is implemented as global variables.

	"Since the execution of each scenario is broken up between multiple step functions,
	it is often necessary to share information between steps. It is possible to do this
	using global variables in the step definition modules but, if you dislike that approach,
	Freshen provides three global storage areas which can be imported from the freshen module."

	-- https://github.com/rlisagor/freshen#context-storage

Example:

.. code-block:: python


	glc.stuff == gcc['stuff']  #  => True
	glc.doesnotexist           #  => None


Building context imperative style
=================================

A global context object solves the problem of sharing state, but it does not
provide any way for keywords to demand a certain situation. As the result, you
never know what is in your context and how did it get there. Side effects are
encapsulated inside methods and are not mentioned in the step name. It is hard
to break up the setup logic for the complicated data model hierarchy and reuse
it.

The following example illustrates the problem of missing a contract on how
context artifacts are stored:


Given I have 2 books
--------------------

.. code-block:: python


	context.books = [Book(), Book()]  # Store the whole list in the context?

Or

.. code-block:: python


	context.book1 = Book()  # Store it as individual members?

But I also need to create an author and pass it to the Book(author=Author(domain=Domain(...)))

What if the step I'm reusing already has context.author?

What other developers expect in when and then steps?


PyTest
######

PyTest is like no other test toolkit. It gives you true pythonic way of testing.
No special functions are needed for assertions, less imports needed, no classes are
necessary for the test cases.

But the main difference is in the dependency injection pattern that is used for
setting up the tests.

It allows concentrating on only what is necessary to implement the fixture (part of the setup)
or the test function. Everything that it depends on can be just specified in the
arguments of the function and PyTest will provide the values of all the dependencies.

This makes it a real declarative style where you don't have to worry about the order
of following or the side effects that were previously applied.

Fixtures
========

Fixtures implement a concept of expecting and returning values. They have a
scope where they are evaluated only once, by default they are created for every
test. If you want to use a fixture simply specify it's name in the arguments of
the test function or another fixture.

.. code-block:: python


	@pytest.fixture
	def author():
		"""Author object. Created only once and used by all the functions that require
		it in the same testing session.

		"""
		return Author()


	@pytest.fixture
	def book(author):
		"""Book. Depends on the author fixture."""
		return Book(author=author)

Complex setup
=============

All the dependencies will be resolved starting from the test function.
Test requires fixtures, fixtures depend on another fixtures etc...

The test function may expect a list of objects (Given I have 2 books),
but this list can be composed with the individual fixtures as well.
It is convenient if you want to assert a condition for the specific element
(Then the second book has to be interesting).

.. code-block:: python


	@pytest.fixture
	def two_books(first_book, second_book):
		return [first_book, second_book]


	@pytest.fixture
	def first_book(author, fiction):
		return Book(author=author, genre=fiction)


	@pytest.fixture
	def second_book(author, science):
		return Book(author=author, genre=science)

pytest-bdd
##########

What if we could combine the power of the pytest fixtures, our experience
and existing fixtures that we have for the unit tests with BDD?
Unfortunately there were no implementations of the Gherkin for the PyTest.

So for the requirements like:

.. code-block:: gherkin


	Scenario: Publishing the article
	    Given I'm an author user
	    And I have an article
	    When I go to the article page
	    And I press the publish button
	    Then I should not see the error message

The implementation of the Gherkin steps could be like:

.. code-block:: python
	
	# PyTest will execute this test_* function
	test_publishing_article = scenario('article.feature', 'Publishing the article')

	@given('I have an article')
	def article(author):
	    return create_test_article(author=author)


	@when('I go to the article page')
	def go_to_article(article, browser):
	    browser.visit(urljoin(browser.url, '/manage/articles/{0}/'.format(article.id)))


	@when('I press the publish button')
	def publish_article(browser):
	    browser.find_by_css('button[name=publish]').first.click()


	@then('I should not see the error message')
	def no_error_message(browser):
	    with pytest.raises(ElementDoesNotExist):
	        browser.find_by_css('.message.error').first


And so we made one...

The result is pretty elegant. Since the unit tests and BDD tests became the same
technology we could start unifying the test setup using the folder layout and
fixture inheritance via the conftest files and plugins.

This is another opportunity to unify the error reporting for the CI server since all
tests are using the same runner.

Splinter offers the option of the PhantomJS which is also speeding up a bit the execution.
The browser fixture scope allows reusing already open browser windows, but clearing the
cookies and opening the blank page between the test functions.

This optimizes the resource usage and test execution time. PyTest also has support for running
tests in the distributed environment which displays impressive scaling results.

With constantly growing number of tests it is very important to receive the early respone
from the CI server about the results of the testing and to keep control of the size of the
test codebase with the maximum reusability.


To be continued...
==================

Links
#####
 - pytest-bdd_ - BDD library for the py.test runner.
 - pytest-bdd-splinter_ - Splinter subplugin for the pytest-bdd.
 - pytest-bdd-example_ - Example project.

.. _pytest-bdd: https://github.com/olegpidsadnyi/pytest-bdd
.. _pytest-bdd-splinter: https://github.com/olegpidsadnyi/pytest-bdd-splinter
.. _pytest-bdd-example: https://github.com/olegpidsadnyi/pytest-bdd-example
