:title: Pre-fill Registration Data
:date: 2013-12-02 10:56
:summary: How to integrate with the pre-fill registration feature.
:category: Integration
:author: Spyros Ioakeimidis
:slug: articles/prefill-registration
:tags: integration

*In some cases it is required that the registration form in the front office is pre-filled
with the personal data of a consumer, assuming that a consumer has provided the personal data beforehand on a
pre-registration step. The following sections describe the steps that third parties have to implement
in order to provide the possibility of pre-filling the registration form in the front office.*

JSON data format
------------------------

The first step is to construct the data. The data should be structured using JSON. The JSON data should adhere to the
following format:

.. code-block:: javascript

    {
      "first_name": "Test Client First Name",
      "last_name": "Test Client Last Name",
      "email": "test@testmail.com",
      "gender": "1",
      "birth_date": "1978-10-07",
      "phone_number": "0123456789",
      "address": "Address 1A",
      "postal_code": "9999AB",
      "city": "Groningen",
      "country": "NL"
    }

The :code:`gender` attribute should contain a code according to `ISO 5218 <http://en.wikipedia.org/wiki/ISO/IEC_5218>`_,
which specifies the following codes:

- 0 = not known
- 1 = male
- 2 = female
- 9 = not applicable

The format of the :code:`birth_date` attribute should be :code:`YYYY-MM-DD`. This
format is according to `ISO 8601 <http://en.wikipedia.org/wiki/ISO_8601>`_.
Finally, the :code:`country` code attribute should contain a value according to
`ISO 3166 <http://www.iso.org/iso/country_codes/iso_3166_code_lists/country_names_and_code_elements.htm>`_.
For example, for The Netherlands the country code :code:`NL` should be used.

Compression and Encoding
------------------------

The second step is to compress and encode the data. Compression helps to reduce the length of the data, as the URL can contain
up to a maximum number of characters. It is not only that the JSON data itself
might be long. Encoding also increases the length of the data by approximately
33%. Encoding is used to protect the privacy of the data.

The way encoding and
compression can be implemented depends on which programming language is used. A simple implementation is illustrated both for
Python and PHP. If a different programming language is used, then please contact
the support team of Paylogic (URL here). The data should first be compressed and then encoded.

Python
~~~~~~~

.. code:: python

    import json
    import zlib

    from base64 import urlsafe_b64encode

    # construct the json data
    json_data = {"first_name": "Test Client First Name", ... }

    # create a string of the json data
    json_data_string = json.dumps(json_data)

    # compress the data
    compressed_data = zlib.compress(json_data_string)

    # encode the data using base64 and urlsafe
    encoded = urlsafe_b64encode(compressed_data)

The compression is performed using the :code:`zlib` standard python module. The
default level of compression has the value of 6.

PHP
~~~~~~~

.. code:: php

    <?php
    $json_data_string = '{"first_name": "Test Client First Name", ... }';

    $compressed_data = gzcompress($json_data, 6);

    $encoded_data = base64_encode($compressed);

    $encoded_data = str_replace(array('+','/'), array('-','_'), $encoded_data);
    ?>

Transferring the data
------------------------

The third step is to append the encoded and compressed data to the landing page URL.
The landing page URL is the URL that is usually included within the confirmation emails.
The encoded and compressed data should be appended to the landing page URL **after** the fragment identifier (**#**).

The implementation of this is left to the third parties. The only constraint is that
the appended data should have a specific form. We assume that the landing page URL contains some query parameters (substituted with '...' in the following example for clarity) and :code:`FGRAhdfhasAHDFA=` is
the encoded and compressed data. Then, a landing page URL with the appended data would have the following form:

.. code::

    http://tickets.company.com/?...#pld=FGRAhdfhasAHDFA=

It is important to use :code:`pld` as a parameter, as this is also used
in Paylogic side. The above method will work if Paylogic handles the creation of the landing page.

Third party handles landing page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case third party handles the creation of the landing page, then one more step needs to be performed.
The code of javascript below should be appended at the end of the landing page HTML document.
This ensures that the data are read from the landing page URL and that they are appended in the queue URL, which
resides as an iframe inside the landing page HTML document.

.. code:: javascript

    <script type="text/javascript">
    var getHashParam = function() {
      window.location.hash.replace(/([^#&]+)/g, function(match) {
        // This is to ensure that if the variable contains '=' then they remain in the value.
        // for example: pld=FHadfsdhFJASDF3423==
        // In this case:
        //   key: pld
        //   value: FHadfsdhFJASDF3423==
        var param = match.split(/=(.+)?/);
        if (param[0] === "pld") {
            queue = document.getElementById('paylogic-frontoffice');
            queue.src = queue.src + '#pld=' + param[1];
        }
      });
    };
    getHashParam();
    </script>
