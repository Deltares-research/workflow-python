.. _user_guide_index:

==========
User guide
==========

Workflowpy's main function is to ease the creation of workflows with the help of Python.
These workflow written in Python can than be translated to workflow engines like
SnakeMake_, which can then execute the workflow. This user guide provides a quick overview
of the terminology regarding workflows, the creation and execution of workflows,
the usage of methods in workflows, and the create of your own methods/ library of methods.

.. grid:: 4
    :gutter: 1

    .. grid-item-card::
        :text-align: center
        :link: user_guide_term
        :link-type: ref

        :octicon:`list-ordered;5em`
        +++
        Terminology

    .. grid-item-card::
        :text-align: center
        :link: user_guide_use_index
        :link-type: ref

        :octicon:`workflow;5em`
        +++
        How to use

    .. grid-item-card::
        :text-align: center
        :link: user_guide_create
        :link-type: ref

        :octicon:`code;5em`
        +++
        Create your own

    .. grid-item-card::
        :text-align: center
        :link: user_guide_examples
        :link-type: ref

        :octicon:`graph;5em`
        +++
        Examples

.. toctree::
   :maxdepth: 2
   :hidden:

   term.rst
   use/index.rst
   create.rst
   example.rst
