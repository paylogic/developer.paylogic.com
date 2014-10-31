:title: How we use pytest and pytest-bdd in Paylogic.
:date: 2014-10-31 11:00
:summary: Describing standards and best practices of using pytest and pytest-bdd in Paylogic
:category: Testing
:author: Andrey Makhnach
:slug: articles/how-we-use-pytest-and-pytest-bdd-in-paylogic
:tags: open source, python, pytest, pytest-bdd

********************************************
How we use pytest and pytest-bdd in Paylogic
********************************************


.. contents::

After some time of using `pytest <http://pytest.org>`_ and `pytest-bdd <https://github.com/olegpidsadnyi/pytest-bdd>`_
in Paylogic we developed some standards in the structure of folders with tests and fixtures, and the usage of pytest
and pytest-bdd functionality. This article describes those standards and our usage patterns.

Folder structure
================

All our tests are stored in the tests folder in the root of the project folder. Our tests are separated by category,
such as unit, functional, blackbox, etc. The tests are stored in the folders of their category. The
structure looks as follows:

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
registered in *tests/conftest.py* because they are common fixtures for both our functional as well as our blackbox tests.

I use the term "common fixtures" because *conftest.py* gives us the possibility to separate fixtures and pytest's plugins
hooks, and register them only for those tests that use them. In our case, we have fixtures/hooks which are
common for all tests and at the same time we have fixtures/hooks which are related only to functional/blackbox tests,
for example *pytestbdd_window_size*. You can imagine that this fixture is only used by pytest-bdd and not by our unit tests.

Fixture imports
===============
For registering fixtures we just import the fixtures from their packages. For example for registering the *order* fixture
and fixtures that represent attributes of *order* object such as *order_title*, *order_point_of_sale*, etc. we just do:

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

As you can see our order fixture is a regular pytest fixture, nothing special. It returns an instance of the Order
model which in turn is created by the *create_test_order* testhelper function.

We are using testhelper functions for creating fixtures and for populating the database with initial data after
re-creating it. We use testhelpers instead of loading JSON or YAML fixtures because attributes of models change
frequently and we decided that it would be better and more flexible to use just a list of testhelpers that are called in
the right order for creating initial data.


Fixture parametrization
=======================

Overriding fixture parameters
-----------------------------

The order fixture inherits from lots of other fixtures because we want to have the possibility to override attributes
with which the order will be created. We override these using @pytest.mark.parametrize or with argumented steps in
pytest-bdd.

For example if we need to test an order with a different *expiry_time* we do it like this:

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

From the example you can see that as soon as we run tests that use the *client_ip* fixture then pytest will run this
test as many times as the number of parameters the *client_ip* fixture has defined (in this case of course two).

Now the question is of course, what is the difference between those two parametrization methods? The difference is that
*pytest.mark.parametrize* will influence only the test on which it is explicitly defined, while *pytest.fixture(params=[..])*
influences every test that uses this fixture. If you would for example define three parameters for the above client_ip fixture,
then each test using this fixture will now be executed three times, once for every param. You are basically creating
three fixtures.

Regarding how frequently you would use *pytest.mark.parametrize* compared of *pytest.fixture(params=[...])*, it strongly
depends on your code base, test code base and type of test. I don't think I can say anything meaningful about that in a
general sense based on just our experiences.

Fixtures for mocking
--------------------

We also use fixtures for mocking. For example in the `settei <https://github.com/paylogic/settei>`_  project we needed
to mock a required method of the *pkg_resources.EntryPoint* class, so we wrote the following fixture:

.. code-block:: python

    # tests/test_get_entry_points.py
    ...
    @pytest.fixture
    def monkeypatch_entrypoint(monkeypatch, clean_config):
        """Monkeypatching EntryPoint."""
        monkeypatch.setattr(pkg_resources.EntryPoint, 'require', require)
        …

Each time when your tests depends on this fixture, the *require* method of the
*pkg_resources.EntryPoint* class would be mocked.

Functional testing
==================

Parametrizing scenarios
-----------------------

We also use *pytest.mark.parametrize* for functional testing with pytest-bdd. If you for example need to test the functionality of
creating a product, the scenario of successfully creating a product can look like this:

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

As we can see there is a lot of double work here, which is something we should try to avoid. Luckily, there is a solution. Let's merge
these two scenarios into one:

::

    Scenario: Create product
    Given I am a backoffice admin
    And I have an event

    When I go to the New product page
    And I fill the name of product
    And I fill in the quantity of the product equal to <product_quantity>
    And I submit the form

    Then I should see a <message_status> message

Then in your tests file you can define the scenario like this:

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

There is one more thing which we also use in testing, which is the step with arguments (or argumented steps).

Steps with arguments
--------------------

Consider that, for some reason, you have a similar step in several scenarios, for example *"Given I have an event with
2 products"* and *"Given I have an event with 5 products"*. In your test files you will then have two different steps
defined that are actually almost the same. There is a solution which can help you use the same step for several
scenarios with different behaviour.

In your scenarios you just write *"Given I have an event with 2 products"* and *"Given I have an event with 5 products"*, as
you did before, but in your given.py file you write the following:

.. code-block:: python

    import re

    from pytest_bdd import given

    @given(re.compile('I have an event with (?P<product_quantity>\d+) products'))
    def i_have_an_event_with_products(product_quantity):
        """I have an event with products."""

Now, if your event fixture uses the *product_quantity* fixture, then for each scenario you will get the event with a
different quantity of products, depending on what you write in your feature file.

Scenario outlines
-----------------

Scenarios can also be parametrized to cover multiple cases. In the `Gherkin language <http://docs.behat.org/en/v2.5/guides/1.gherkin.html>`_
the variable templates are written using corner braces, like so: <somevalue>. Scenario outlines are supported by pytest-bdd
exactly as described in the `behave docs <http://docs.behat.org/en/v2.5/guides/1.gherkin.html#scenario-outlines>`_.

A full example of a scenario outline can be found below.

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


This code also shows the possibility to use converters which may be useful if you need parameter
types different than strings.

There are two types of outlines, namely horizontal and vertical. These merely
state how you write the possible values of the attributes. We saw an example of
a horizontal outline above; the below is an example of a vertical outline. Note
that you have to explicitly state "Vertical" to indicate that you are using the
vertical outline type, otherwise pytest-bdd will default to horizontal.

::

    Scenario Outline: Outlined given, when, thens
    Given there are <start> cucumbers
    When I eat <eat> cucumbers
    Then I should have <left> cucumbers

    Examples: Vertical
    | start | 12 | 2 |
    | eat   | 5  | 1 |
    | left  | 7  | 1 |



Finally, you should not forget to register the given steps from *functional/steps/given.py* in
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

All things registered in *tests/functional/conftest.py* will now only be accessible in the scope of the functional tests.


Conclusion
==========

That is how our core of storing/creating our tests looks like. I hope that this article will
be useful for you. There are always ways to improve it and you are welcome in comments with your thoughts. We are
planning to improve a relation between code and tests, fixtures.

Thank you for reading.
