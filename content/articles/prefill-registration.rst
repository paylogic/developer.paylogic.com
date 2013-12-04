:title: Prefill Registration Data
:date: 2013-12-02 10:56
:summary: How to integrate with the prefill registration feature.
:category: Integration
:author: Spyros Ioakeimidis
:slug: articles/prefill-registration
:tags: integration

*Paylogic offers a feature to allow the prefilling of the personal data of a
consumer during the sales process via a personalized URL. This can be used
whenever a merchant already has the data of the consumers and wants to offer
these consumers a more personalized and smooth ticketing process, or when a
pre-registration step is used. The following sections describe the steps that
third parties have to implement in order to provide the possibility of
prefilling the registration form in the front office.*

JSON data format
------------------------

The first step is to construct the data. The data should be structured using
JSON. The JSON data should adhere to the following format:

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

The :code:`gender` attribute should contain a code according to `ISO 5218
<http://en.wikipedia.org/wiki/ISO/IEC_5218>`_, which specifies the following
codes:

- 0 = not known
- 1 = male
- 2 = female
- 9 = not applicable

The format of the :code:`birth_date` attribute should be :code:`YYYY-MM-DD`.
This format is according to `ISO 8601 <http://en.wikipedia.org/wiki/ISO_8601>`_.
Finally, the :code:`country` code attribute should contain a value according to
`ISO 3166 <http://www.iso.org/iso/country_codes/iso_3166_code_lists/country_names_and_code_elements.htm>`_.
For example, for The Netherlands the country code :code:`NL` should be used. It
should be mentioned that no certain format is required for :code:`postal_code`,
as long as its length is less than or equal to 12.

Compression and Encoding
------------------------

The second step is to compress and encode the data. Compression helps to reduce
the length of the data, as the URL should contain up to a maximum number of
characters. It is not only that the JSON data itself might be long. Encoding
also increases the length of the data by approximately 33%.

The pseudo code below illustrates the process of encoding and compression. It
also includes the creation of the JSON data. The data should first be compressed
and then encoded.

.. code::

    create the JSON data

    create a string out of the JSON data

    compress the data using gzip compatible compression

    encode the data using base64 and make them url safe

The way encoding and compression can be implemented depends on which programming
language is used. A simple implementation is illustrated both for Python and
PHP. If there are any questions regarding the implementation, then please contact
the Paylogic support team.

Python
~~~~~~~

The compression is done using the `zlib <http://www.zlib.net/>`_
standard python module. The data is encoded to utf-8 prior to compression. Data
encoding is performed using base64 as specified in `RFC 3548 <http://tools.ietf.org/html/rfc3548.html>`_

.. code:: python

    import json
    import zlib

    from base64 import urlsafe_b64encode

    # construct the json data
    json_data = {"first_name": "Test Client First Name", ... }

    # create a string of the json data
    json_data_string = json.dumps(json_data)

    # encode the data to utf8 and compress it
    compressed_data = zlib.compress(json_data_string.encode('utf8'))

    # encode the data using base64 and urlsafe
    encoded = urlsafe_b64encode(compressed_data)

PHP
~~~~~~~

The compression is done using the `gzcompress <http://php.net/manual/en/function.gzcompress.php>`_
method, which uses the `zlib <http://www.zlib.net/>`_ data format. The data is
encoded to utf-8 prior to compression. Data encoding is performed using base64
as specified in `RFC 3548 <http://tools.ietf.org/html/rfc3548.html>`_

.. code:: php

    <?php
    # create a string of the json data
    $json_data_string = '{"first_name": "Test Client First Name", ... }';

    # encode data to utf8 and compress it
    $compressed_data = gzcompress(utf8_encode($json_data_string));

    # encode the data using base64
    $encoded_data = base64_encode($compressed_data);

    # make data urlsafe
    $encoded_data = str_replace(array('+','/'), array('-','_'), $encoded_data);
    ?>

Transferring the data
------------------------

The third step is to append the encoded and compressed data to the landing page
URL. The landing page URL is the URL that is usually included within the
invitation emails. The encoded and compressed data should be appended to the
landing page URL **after** the fragment identifier (**#**). The advantage of
this approach is that data after the fragment identifier is not sent over the
network and is only used client-side.

The implementation of this is left to the third parties. The only constraint is
that the appended data should have a specific form. We assume that the landing
page URL contains some query parameters (substituted with '...' in the
following example for clarity) and :code:`FGRAhdfhasAHDFA` is the encoded and
compressed data. Then, a landing page URL with the appended data would have the
following form:

.. code::

    http://tickets.company.com/?...#pld=FGRAhdfhasAHDFA

It is important to use :code:`pld` as a parameter, as this is also used on the
side of Paylogic, when retrieving the data from the URL. The above method will
work if Paylogic handles the creation of the landing page.

Third party handles landing page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case a third party handles the creation of the landing page, then one more
step needs to be performed. The Javascript code below should be appended at the
end of the landing page HTML document. This ensures that the data is read from
the landing page URL and that it is appended in the queue URL, which resides as
an iframe inside the landing page HTML document.

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
            queue.src = queue.src + '#' + param[0] + '=' + param[1];
        }
      });
    };
    getHashParam();
    </script>
