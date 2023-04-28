:html_theme.sidebar_secondary.remove:

=================
Welcome to SECoP!
=================

.. toctree::
    :maxdepth: 1
    :hidden:

    intro/index
    spec1-0/index

.. toctree::
    :maxdepth: 1
    :hidden:

    implementations/index

.. toctree::
    :maxdepth: 1
    :hidden:

    contact
    ISSE <https://sampleenvironment.org/>
    impressum

.. grid::

   .. grid-item::
      :columns: 4

      .. code-block::
         :class: intro-code-block

         > describe
         < describing secop {"..."}

   .. grid-item::

      The SECoP (Sample Environment Communication Protocol) is an Inclusive, Simple
      and Self Explaining (ISSE) communication protocol.
      It is, coincidentally, developed by `ISSE
      <https://sampleenvironment.org/>`_.


.. grid::

   .. grid-item::

   .. grid-item::

      .. button-ref:: intro/index
         :color: warning
         :shadow:

         See examples

   .. grid-item::

      .. button-ref:: spec1-0/index
         :color: info
         :shadow:

         Read the spec

   .. grid-item::

      .. button-ref:: implementations/index
         :color: danger
         :shadow:

         Download code

   .. grid-item::

.. grid::
   :gutter: 5

   .. grid-item::

      **Inclusive** means that facilities can use this protocol and don’t have to change
      their work flow (rewrite drivers completely or organize and handle hardware in a
      specific way to fulfill SECoP requirements).

   .. grid-item::
      :columns: 4

      .. image:: _static/landing_1_cdbs_1.jpg
         :target: https://ess.eu/
         :width: 50 %
         :align: right

.. grid::
   :gutter: 5

   .. grid-item::
      :columns: 4

      .. image:: _static/technology-connections-ss-1920-800x459.gif
         :target: https://fz-juelich.de/
         :width: 90 %

   .. grid-item::

      **Simple** means it should be easy to integrate and to use.

.. grid::
   :gutter: 5

   .. grid-item::

      **Self Explaining** means that with SECoP, not only the pure data is transported. It
      also transports meta data, which allows environment control software to
      configure by itself.

   .. grid-item::

      .. image:: _static/heldele_automation_gmh-startseite-slider-bosch_rexroth_partner-1920x1080__002_.webp
         :target: https://mlz-garching.de/
         :width: 65 %
         :align: right


.. grid::
   :gutter: 5

   .. grid-item::

      .. image:: _static/mag-v-15t-rgb.jpg
         :target: https://psi.ch/
         :width: 70 %

   .. grid-item::

      The benefit of SECoP will be to circulate expensive devices between different
      facilities with minimised effort for configuration and integration. This should
      result in an increased utilisation of expensive equipment.

The :doc:`Introduction <intro/index>` section has examples of the protocol, as
well as example code to get started with writing drivers using one of our
implementations.

See the :doc:`Specification <spec1-0/index>` section for the full specification.

In :doc:`Implementations <implementations/index>` you can see the known implementations, which
cover a wide range of use cases and technologies.
