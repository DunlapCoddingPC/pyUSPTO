Installation
============

pyUSPTO requires Python 3.11 or higher. Install the latest release from
`PyPI <https://pypi.org/project/pyUSPTO/>`_:

.. code-block:: bash

   pip install pyUSPTO

If you use `uv <https://docs.astral.sh/uv/>`_, add pyUSPTO to your project
with:

.. code-block:: bash

   uv add pyUSPTO

or install it into a virtual environment with ``uv pip install pyUSPTO``.

To use the library you will also need a USPTO Open Data Portal API key — see
:doc:`about` for how to get one.

Development Installation
------------------------

To work on pyUSPTO itself, clone the repository and install it in editable
mode with the development dependencies:

.. code-block:: bash

   git clone https://github.com/DunlapCoddingPC/pyUSPTO.git
   cd pyUSPTO
   pip install -e ".[dev]"

.. note::

   The development environment requires Python 3.12+, because the
   documentation tools in the ``dev`` extra (Sphinx 9.1) don't support
   Python 3.11. The package itself supports Python 3.11+.

See the :doc:`contributing guidelines <development>` for the full development
workflow, including running tests and linting.
