:title: How do we use pytest and pytest-bdd in Paylogic.
:date: 2014-04-23 11:00
:summary: Describing standards and best practices of using pytest and pytest-bdd in Paylogic
:category: Open source
:author: Andrey Makhnach
:slug: articles/how-do-we-use-pytest-and-pytest-bdd-in-paylogic
:tags: open source, python, pytest, pytest-bdd

************************************************
How do we use pytest and pytest-bdd in Paylogic.
************************************************


.. contents::

After some time of using pytest and pytest-bdd in Paylogic we created some standards in the structure of folders with
tests and fixtures, and the usage of pytest and pytest-bdd functionality.

Folder structure and fixture imports.
=====================================

All our tests are stored in the tests folder in the root of the project folder and our tests are separated by category,
such as unit, functional, blackbox, etc. The tests are stored in folders with names equal to their category. The
structure of the tests folder looks as follows:

::

    tests/

        fixtures/

        blackbox/

        functional/

        unit/

        conftest.py

In *tests/conftest.py* we register all global fixtures that represent objects, such as *event*, *order* and *merchant*.
Here we also register fixtures that represent attributes of objects like event_title, product_title, etc. The fixtures
which are related to pytest-bdd, for example *pytestbdd_window_size*, *pytestbdd_browser_load_timeout*, etc., are also
registered in *tests/conftest.py* because they are common fixtures for functional and backoffice tests.

I wrote "common fixtures" because *conftest.py* gives us possibility to separate fixtures, pytest and pytest's plugins
hooks and register them only for those tests which are related to them. I mean that we have fixtures/hooks which are
common for all tests and at the same time we have fixtures/hooks which are related only to functional/blackbox tests,
for example *pytestbdd_window_size*, this fixtures is used by pytestbdd and not used by our unit tests.

For registering fixtures we just import the fixtures from their packages. For example for registering the order fixture
and fixtures that represent attributes of order object such as *order_title*, *order_point_of_sale*, etc. we just do:

.. code-block:: python

    from tests.fixtures.order import (
        order,
        order_title,
        order_point_of_sale,
        ...
    )

A fixture that represents an object, e.g. an order, typically looks as follows:

.. code-block:: python

    @pytest.fixture
    def order(
        ...
        event,
        order_point_of_sale,
        order_products,
        ...
        expiry_time
    ):
        """Fixture which represents an order object."""
        return create_test_order(
            ...
            event=event,
            point_of_sale=order_point_of_sale,
            products=order_products,
            ...
            expiry_time=expiry_time
        )

As you can see that our order fixture is a regular pytest fixture, nothing special. It returns an instance of the Order
model which in turn is created by the *create_test_order* testhelper function.

We are using testhelper functions for creating fixtures and for populating the database with initial data after
re-creating it. We use testhelpers instead of loading json or yaml fixtures just because attributes of models changing
frequently and we decided that it will be better to just have a big file with a list of testhelpers that are called in
the right order for creating initial data.


Fixture parametrization.
========================

Overriding fixture parameters.
------------------------------

The order fixture inherits from lots of other fixtures because we want to have the possibility to override attributes
with which the order will be created. We override these using @pytest.mark.parametrize or with argumented steps in
pytest-bdd.

For example if we need to test an order with a different *expiry_time* we just do it like this:

.. code-block:: python

    import pytest

    @pytest.mark.parametrize(
        expiry_time,
        [
    datetime.date.now()+datetime.timedelta(days=2),
    datetime.date.now()-datetime.timedelta(days=2)
    ]
    )
    def test_complete_order(order):
        order.complete()
        assert order.state == OrderState.COMPLETED

Now, test_complete_order test will be executed twice and every time we will have an order with a different *expiry_time*.

We also use *pytest.fixture(params=[...])* to set parameters for fixtures:

.. code-block:: python

    import pytest

    @pytest.fixture(params=['127.0.0.1', '192.168.0.1'])
    def client_ip(request):
        return request.param

From the example you can see that as soon as we will run tests with the *client_ip* fixture then pytest will run this
test as many times as the number of parameters the *client_ip* fixture has defined (in this case of course two).

Now the question is of course, what is the difference between those two parametrization methods? The difference is that
*pytest.mark.parametrize* will influence only the test where it is defined, while *pytest.fixture(params=[..])*
influences every tests that uses this fixture. If you would for example define three parameters, then each test which
will use fixture which accepts params from params will be executed three times.

To see how frequently we use *pytest.mark.parametrize* instead of *pytest.fixture(params=[...])*, I can say that the
scope of using *pytest.mark.parametrize* is of course bigger than *pytest.fixture(params=[...])*. I think that it
depends only on our code base, test code base and types of our tests.

Fixtures for mocking.
---------------------

We even use fixtures for mocking. For example in the `settei <https://github.com/paylogic/settei>`_  project we needed
to mock a required method of the *pkg_resources.EntryPoint* class, so we wrote the following fixture:

.. code-block:: python

    # tests/test_get_entry_points.py
    ...
    @pytest.fixture
    def monkeypatch_entrypoint(monkeypatch, clean_config):
        """Mokeypatching EntryPoint."""
        monkeypatch.setattr(pkg_resources.EntryPoint, 'require', require)
        …

Each time when your tests depends on this fixture you will get the mocked require method of the
*pkg_resources.EntryPoint* class.

Functional testing.
===================

Parametrizing scenarios.
------------------------

We also use *pytest.mark.parametrize* for functional testing. For example if you need to test the functionality of
creating a product. The scenario of successfully creating a product can look like this:

::

    Scenario: Successfully creating a product
    Given I am a backoffice admin
    And I have an event

    When I go to the New product page
    And I fill in the name of the product
    And I fill in the quantity of the product equal to 5
    And I submit the form

    Then I should see a success message

As you can see, nothing special. But if you for example need to test that a form should show an error message if the
quantity of the product cannot equal 0, then you will create another scenario. It can look like this:

::

    Scenario: Unsuccessful creating of product
    Given I am a backoffice admin
    And I have an event

    When I go to the New product page
    And I fill in the name of the product
    And I fill in the quantity of the product equal to 0
    And I submit the form

    Then I should see an error message

As we can see there is double work and it is natural to wish avoid double work somehow. There is a solution. Let merge
those two scenarios in one.

::

    Scenario: Create product
    Given I am a backoffice admin
    And I have an event

    When I go to the New product page
    And I fill the name of product
    And I fill in the quantity of the product equal to <product_quantity>
    And I submit the form

    Then I should see a <message_status> message

Then in your tests file you will define the scenario like this:

.. code-block:: python

    import pytest
    from pytest_bdd import scenario

    @pytest.mark.parametrize(
        ['product_quantity', 'message_status'],
        [
            (5, 'success'),
            (0, 'error'),
        ]
    )
    @scenario('Create product')
    def test_create_product(product_quantity, message_status)
        """Create product."""

And now in your given, when and then steps you can ask for the *product_quantity* and *message_status* fixtures.

.. code-block:: python

    @when('I fill in the quantity of the product equal to <product_quantity>')
    def i_fill_the_quantity_of_product(product_quantity):
        …

    @then('I should see a <message_status> message')
    def assert_that_i_see_message(message_status):
        …

There is one more thing which we also use in testing, which is the step with arguments.

Steps with arguments.
---------------------

Consider that, for some reason, you have a similar step in several scenarios, for example *"Given I have an event with
2 products"* and *"Given I have an event with 5 products"*. In your test files you will then have two different steps
defined that are actually almost the same. There is a solution however which can help you use the same step for several
scenarios with different behaviour.

In your scenarios you write *"Given I have an event with 2 products"* and *"Given I have an event with 5 products"*, as
you did before, but now you need to create a steps package with a given.py file. In this file, add the following:

.. code-block:: python

    import re

    from pytest_bdd import given

    @given(re.compile('I have an event with (?P<product_quantity>\d+) products'))
    def i_have_an_event_with_products(product_quantity):
        """I have an event with products."""

Now, if your event fixture uses the *product_quantity* fixture, then for each scenario you will have the event with
different quantity of products, depending on what you write in your feature file.

Scenario outlines
-----------------

Scenarios also can be parametrized to cover few cases. In Gherkin the variable templates are written using corner
braces as <somevalue>.

::

    Scenario Outline: Outlined given, when, thens
    Given there are <start> cucumbers
    When I eat <eat> cucumbers
    Then I should have <left> cucumbers

    Examples:
    | start | eat | left |
    |  12   |  5  |  7   |


.. code-block:: python

    from pytest_bdd import given, when, then, scenario

    @scenario(
        'outline.feature',
        'Outlined given, when, thens',
        example_converters=dict(start=int, eat=float, left=str)
    )
    def test_outlined():
    pass


    @given('there are <start> cucumbers')
    def start_cucumbers(start):
        assert isinstance(start, int)
        return dict(start=start)


    @when('I eat <eat> cucumbers')
    def eat_cucumbers(start_cucumbers, eat):
        assert isinstance(eat, float)
        start_cucumbers['eat'] = eat


    @then('I should have <left> cucumbers')
    def should_have_left_cucumbers(start_cucumbers, start, eat, left):
        assert isinstance(left, str)
        assert start - eat == int(left)
        assert start_cucumbers['start'] == start
        assert start_cucumbers['eat'] == eat


Code also shows possibility to pass example converters which may be useful if you need parameter types different than
strings.

There are two types for outlines horizontal and vertical

::

    Scenario Outline: Outlined given, when, thens
    Given there are <start> cucumbers
    When I eat <eat> cucumbers
    Then I should have <left> cucumbers

    Examples: Vertical
    | start | 12 | 2 |
    | eat   | 5  | 1 |
    | left  | 7  | 1 |



Finally, you should not forget to register the given steps from *functional/steps/give.py* in the
*functional/conftest.py* in the functional folder.

.. code-block:: python

    # tests/functional/conftest.py
    from tests.functional.steps.given import *

Now your folder structure should look like this:

::

    tests/
        fixtures/

        blackbox/

        functional/
            steps
                __init__.py
                given.py
            conftest.py
        unit/
        conftest.py

All things registered in *tests/functional/conftest.py* will be accessible only in scope of the functional tests.

