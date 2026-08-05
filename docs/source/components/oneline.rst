.. _oneline:

One Line Comment Style
======================

Many users have raised concerns about the complexity of defining ``Sphinx-Needs`` need items with RST in source code.
Therefore, ``CodeLinks`` provides a customizable one-line comment style pattern to define ``need items``
to simplify the effort required to create a need in source code.

:ref:`Here <oneline_comment_style>` is the default one-line comment style.

**Additional examples and use cases:**

For more comprehensive examples and advanced configurations, see the `test cases <https://github.com/useblocks/sphinx-codelinks/tree/main/tests>`__.

Start and End sequences
-----------------------

To have a better understanding of the syntax of a one-line comment, we will break it down as follows:

**start_sequence** defines the characters where the one-line comment starts.
**end_sequence** defines the characters where the one-line comment ends.

The text between **start_sequence** and **end_sequence** contains the fields of a ``need item``.

field_split_char
----------------

Since there are always multiple fields for a need,

**field_split_char** defines the character to split the text into multiple ``pieces/fields``.

needs_fields
------------

Each field in a need may have different data types.
It could be a string if it is a field for ``id`` or ``title``. On the other hand,
it could be a list of strings as well, if the field requires a list of strings to represent ``links``.

This is where **needs_fields** comes in.

**needs_fields** contains the fields that are required for needs:

Each need field defines its:

- name
- data type (Optional)
- default value (Optional)

The examples in the following sections use :ref:`the default <oneline_comment_style>` to
explain the syntax of the one-line comment.

DataType
~~~~~~~~

By default, a field has the data type of ``str``.

For example, if the field definition is as follows:

.. code-block:: python

   {
       "name": "title
   }

It's equivalent to:

.. code-block:: python

   {
       "name": "title",
       "type": "str"
   }

If the field is expected to have a list of strings, it shall be defined as the following:

.. code-block:: python

   {
       "name": "links",
       "type": "list[str]"
   }

When the field has data type ``list[str]``:

- the strings must be given within ``[`` and ``]`` brackets
- ``,`` shall be used as the separator.

For example, with the following **needs_fields** configuration:

.. _`fields_config`:

.. tabs::

   .. code-tab:: python

      needs_fields = [
         {"name": "title"},
         {"name": "id"},
         {"name": "type", "default": "impl"},
         {"name": "links", "type": "list[str]", "default": []},
      ],

   .. code-tab:: toml

      needs_fields = [
         { name = "title" },
         { name = "id" },
         { name = "type", default = "impl" },
         { name = "links", type = "list[str]", default = [] },
      ]

the one-line comment shall be defined as follows:

.. tabs::

   .. code-tab:: c

      // @ title, id_123, implementation, [link1, link2]

   .. code-tab:: rst

       .. implementation:: title
           :id: id_123
           :links: link1, link2

Default value
~~~~~~~~~~~~~

The value mapped to the key ``default`` in a need field definition is the default value of a need field
when it is not given in the need definition.

For example, with the following needs_fields definition,

.. tabs::

   .. code-tab:: python

      needs_fields = [
         {
            "name": "title"
         },
         {
            "name": "type",
            "default": "implementation"
         },
      ]

   .. code-tab:: toml

      needs_fields = [
         { name = "title" },
         { name = "type", default = "implementation" }
      ]

the following need definition in source code is equivalent to RST shown below:

.. tabs::

   .. code-tab:: c

      // @ title here and default is used for type

   .. code-tab:: rst

      .. implementation:: title here and default is used for type

Positional Fields
~~~~~~~~~~~~~~~~~

All of the fields defined in ``needs_fields`` are positional fields.
This means the ``order of needs_fields`` determines ``the position of the field`` in the one-line comment.

For example, with the mentioned :ref:`needs_fields definition <fields_config>`

field ``title`` is the first element in the list, so the string of the title must be
the first field in the one-line comment.

.. tabs::

   .. code-tab:: c

      // @ this is title, this is id, this_type, [link1, link2]

   .. code-tab:: rst

      .. this_type:: this is title
         :id: this is id
         :links: link1, link2

.. note:: A field without a default value cannot follow a field that has a default value set.

Escaping Characters
~~~~~~~~~~~~~~~~~~~

If the value of the field contains characters that are ``field_split_char`` or angular brackets ``[`` and ``]``,

a leading character ``\`` must be used to escape them.

For example, with the mentioned :ref:`needs_fields definition <fields_config>`,
``,`` is escaped with ``\`` and is not considered as a separator.

.. tabs::

   .. code-tab:: c

      // @ title\, 3, IMPL_3 , impl, []

   .. code-tab:: rst

      .. impl:: title, 3
         :id: IMPL_3

The other example shows the angular brackets ``[`` and ``]`` and comma being escaped:

.. tabs::

   .. code-tab:: c

      // @ title 3, IMPL_3 , impl, [\[SPEC\,_1\]]

   .. code-tab:: rst

      .. impl:: title 3
         :id: IMPL_3
         :links: [SPEC,_1]

To have a backslash ``\`` as a literal in the value, use ``\\`` as shown in the following:

.. tabs::

   .. code-tab:: c

      // @ title\\ 3, IMPL_3 , impl, [\[SPEC\,_1\]]

   .. code-tab:: rst

      .. impl:: title\ 3
         :id: IMPL_3
         :links: [SPEC,_1]

.. caution:: Field values can never contain any newline characters ``\r`` or ``\n``.

Description
~~~~~~~~~~~

By default, only the text inside the one-line marker is used. Set
``description_position`` to ``above`` or ``below`` to additionally use the
surrounding comment text as the ``need item``'s description (body/content).

The description is the contiguous block of comment lines directly above or
below the marker line. Collection stops at the next marker line, a blank line,
or the boundary of the comment. Comment decoration (e.g. ``*``, ``//``, ``#``)
and surrounding whitespace are stripped from each line.

.. tabs::

   .. code-tab:: toml

      [codelinks.projects.my_project.analyse.oneline_comment_style]
      description_position = "below"

   .. code-tab:: c

      /*
       * @Function Bar, IMPL_4, impl, [SPEC_1]
       * This function does the thing.
       * It has a multi-line description.
       */

   .. code-tab:: rst

      .. impl:: Function Bar
         :id: IMPL_4
         :links: SPEC_1

         This function does the thing.
         It has a multi-line description.

With ``description_position = "above"`` the description block is taken from the
comment lines immediately preceding the marker line instead.

.. note:: Setting ``description_position = "none"`` (the default) disables
   description capture, preserving the original behavior.

Comment markup conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The markup language used inside source-code comments depends on the
programming language. Sphinx-Needs renders a need's title and body as
reStructuredText (RST), so content authored in another markup (e.g. Markdown)
would otherwise be interpreted as RST and render incorrectly.

For languages whose comments are conventionally written in Markdown, the
captured one-line marker content — both the **title** and the **description** —
is automatically converted from Markdown to RST. This is controlled by a
*static* language mapping in ``sphinx_codelinks.analyse.markup_format``
(``LANGUAGE_MARKUP_FORMATS``) and is **not** user-configurable. Languages not
listed there default to ``plain`` (no conversion), preserving the original
behavior.

Currently, ``rust`` and ``go`` are mapped to Markdown. For these languages a
description such as ``Calls `do_thing()` and returns **fast**.`` is converted to
the RST equivalent ``Calls ``do_thing()`` and returns **fast**.`` (the same
inline conversion applies to titles).

Markdown conversion requires the optional ``m2r2`` dependency. Install it with:

.. code-block:: bash

   pip install sphinx-codelinks[markdown]

If ``m2r2`` is not installed, the content is used verbatim and a warning is
emitted. The mechanism is extensible: additional markup formats can be added by
extending ``MarkupFormat`` and the converter registry in that module.
