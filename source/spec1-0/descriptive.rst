.. _descriptive-data:

Descriptive Data
================


Format of Descriptive Data
--------------------------

The format of the descriptive data is JSON, as all other data in SECoP.

:note:
    all names on each hierarchy level needs to unique (i.e. not repeated) when lowercased.

SEC Node Description
--------------------

.. image:: images/sec-node-description.svg
   :alt: SEC_node_description ::= '{' ( property ',' )* '"modules":' modules ( ',' property )* '}'

.. compound::

    property:

    .. image:: images/property.svg


Mandatory SEC Node Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``"modules"``
    contains a JSON-object with names of modules as key and JSON-objects as
    values, see `Module Description`_.

    :Remark:

        Be aware that some JSON libraries may not be able to keep the order of the
        items in a JSON objects. This is not required by the JSON standard, and not needed
        for the functionality of SECoP. However, it might be an advantage
        to use a JSON library which keeps the order of JSON object items.

``"equipment_id"``
     worldwide unique id of an equipment as string. Should contain the name of the
     owner institute or provider company as prefix in order to guarantee worldwide uniqueness.

     example: ``"MLZ_ccr12"`` or ``"HZB-vm4"``

``"description"``
     text describing the node, in general.
     The formatting should follow the 'git' standard, i.e. a short headline (max 72 chars),
     followed by ``\n\n`` and then a more detailed description, using ``\n`` for linebreaks.

Optional SEC Node Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``"firmware"``
     short string naming the version of the SEC node software.

     example: ``"frappy-0.6.0"``

``"implementor"``
     Is an optional string.
     The implementor of a SEC-node, defining the meaning of custom modules, status values, custom
     properties and custom accessibles. The implementor **must** be globally unique, for example
     'sinq.psi.ch'. This may be achieved by including a domain name, but it does not need
     to be a registered name, and other means of assuring a global unique name are also possible.

``"timeout"``
     value in seconds, a SEC node should be able to respond within
     a time well below this value. (i.e. this is a reply-timeout.)
     Default: 10 sec, *see* `SECoP Issue 4: The Timeout SEC Node Property`_


Module Description
------------------

.. image:: images/module-description.svg
   :alt: module_description ::= '{' ( property ',' )* '"accessibles":' accessibles ( ',' property )* '}'


Mandatory Module Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``"accessibles"``
    a JSON-object containing the accessibles and their properties, see `Accessible Description`_.

    :Remark:

        Be aware that some JSON libraries may not be able to keep the order of the
        items in a JSON objects. This is not required by the JSON standard, and not needed
        the functionality of SECoP. However it might be an advantage
        to use a JSON library which keeps the order of JSON object items.

``"description"``
    text describing the module, formatted like the node-property description

``"interface_classes"``
    list of matching classes for the module, for example ``["Magnet", "Drivable"]``


Optional Module Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~

``"visibility"``
     string indicating a hint for UIs for which user roles the module should be display or hidden.
     MUST be one of "expert", "advanced" or "user" (default).

     :Note:
         this does not imply that the access is controlled. It is just a
         hint to the UI for the amount of exposed modules. A visibility of "advanced" means
         that the UI should hide the module for users, but show it for experts and
         advanced users.

``"group"``
     identifier, may contain ":" which may be interpreted as path separator between path components.
     The ECS may group the modules according to this property.
     The lowercase version of a path component must not match the lowercase version of any module name on
     the same SEC node.

     :related issue: `SECoP Issue 8: Groups and Hierarchy`_

``"meaning"``
    tuple, with the following two elements:

    1.  a string from an extensible list of predefined meanings:

        * ``"temperature"``   (the sample temperature)
        * ``"temperature_regulation"`` (to be specified only if different from 'temperature')
        * ``"magneticfield"``
        * ``"electricfield"``
        * ``"pressure"``
        * ``"rotation_z"`` (counter clockwise when looked at 'from sky to earth')
        * ``"humidity"``
        * ``"viscosity"``
        * ``"flowrate"``
        * ``"concentration"``

        This list may be extended later.

        ``_regulation`` may be postfixed, if the quantity generating module is different from the
        (closer to the sample) relevant measuring device. A regulation device MUST have an
        `interface classes`_ of at least ``Writable``.

        :related issue: `SECoP Issue 26: More Module Meanings`_

    2.  a value describing the importance, with the following values:

        - 10 means the instrument/beamline (Example: room temperature sensor always present)
        - 20 means the surrounding sample environment (Example: VTI temperature)
        - 30 means an insert (Example: sample stick of dilution insert)
        - 40 means an addon added to an insert (Example: a device mounted inside a dilution insert)

        Intermediate values might be used. The range for each category starts at the indicated value minus 5
        and ends below the indicated value plus 5.

        :related issue: `SECoP Issue 9: Module Meaning`_

.. _implementor:

``"implementor"``
     Is an optional string.
     The implementor of a module, defining the meaning of custom status values, custom
     properties and custom accessibles. The implementor must be globally unique, for example
     'sinq.psi.ch'. This may be achieved by including a domain name, but it does not need
     to be a registered name, and other means of assuring a global unique name are also possible.


Accessible Description
----------------------

.. image:: images/accessible-description.svg
   :alt: accessible_description ::= '{' property+ '}'


Mandatory Accessible Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``"description"``
    string describing the accessible, formatted as for module-description
    or node-description

Mandatory Parameter Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``"readonly"``
    mandatory boolean value.
    Indicates whether this parameter may be changed by an ECS, or not.

``"datainfo"``
    mandatory datatype of the accessible, see :ref:`data-types`.
    This is always a JSON-Object with a single entry mapping the name of the datatype as key to
    a JSON-object containing the datatypes properties.

    :Note:
        commands and parameters can be distinguished by the datatype.

Optional Accessible Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``"group"``: XXX
    identifier, may contain ":" which may be interpreted as path separator between path components.
    The ECS may group the modules according to this property.
    The lowercase version of a path component must not match the lowercase version of any module name or accessible on
    the same SEC node.

    :related issue: `SECoP Issue 8: Groups and Hierarchy`_

    :Remark:

        the accessible-property ``group`` is used for grouping of accessibles within a module,
        the module-property ``group`` is used for grouping of modules within a node.

``"visibility"``
    a string indication a hint for a GUI about
    the visibility of the accessible. values and meaning as for module-visibility above.

    :Remark:

        Setting an accessibles visibility equal or higher than its modules
        visibility has the same effect as omitting the visibility.
        For example a client respecting visibility in 'user' mode, will not show modules
        with 'advanced' visibility, and therefore also not their accessibles.



Optional Parameter Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``"constant"``
    Optional, contains the constant value of a constant parameter.
    If given, the parameter is constant and has the given value.
    Such a parameter can neither be read nor written, and it will **not** be transferred
    after the activate command.

    The value given here must conform to the Datatype of the accessible.


Custom Properties
-----------------
Custom properties may further augment accessibles, modules or the SEC-node description.

As for all custom extensions, the names must be prefixed with an underscore. The meaning
of custom properties is dependent on the implementor, given by the `implementor`_
module property. An ECS not knowing the meaning of a custom property MUST ignore it.
The datatype of a custom property is not pre-defined,
an ECS should be prepared to handle anything here.

:note:
    An ECS which is not programmed to be aware about a specific custom property
    must ignore it.

.. _`Interface Classes and Features`: Interface%20Classes%20and%20Features.rst
.. DO NOT TOUCH --- following links are automatically updated by issue/makeissuelist.py
.. _`SECoP Issue 3: Timestamp Format`: issues/003%20Timestamp%20Format.rst
.. _`SECoP Issue 4: The Timeout SEC Node Property`: issues/004%20The%20Timeout%20SEC%20Node%20Property.rst
.. _`SECoP Issue 6: Keep Alive`: issues/006%20Keep%20Alive.rst
.. _`SECoP Issue 7: Time Synchronization`: issues/007%20Time%20Synchronization.rst
.. _`SECoP Issue 8: Groups and Hierarchy`: issues/008%20Groups%20and%20Hierarchy.rst
.. _`SECoP Issue 9: Module Meaning`: issues/009%20Module%20Meaning.rst
.. _`SECoP Issue 26: More Module Meanings`: issues/026%20More%20Module%20Meanings.rst
.. _`SECoP Issue 35: Partial structs`: issues/035%20Partial%20Structs.rst
.. _`SECoP Issue 36: Dynamic units`: issues/036%20Dynamic%20units.rst
.. _`SECoP Issue 37: Clarification of status`: issues/037%20Clarification%20of%20status.rst
.. _`SECoP Issue 38: Extension mechanisms`: issues/038%20Extension%20mechanisms.rst
.. _`SECoP Issue 42: Requirements of datatypes`: issues/042%20Requirements%20of%20datatypes.rst
.. _`SECoP Issue 43: Parameters and units`: issues/043%20Parameters%20and%20units.rst
.. _`SECoP Issue 44: Scaled integers`: issues/044%20Scaled%20integers.rst
.. _`SECoP Issue 49: Precision of Floating Point Values`: issues/049%20Precision%20of%20Floating%20Point%20Values.rst
.. _`SECoP Issue 59: set_mode and mode instead of some commands`: issues/059%20set_mode%20and%20mode%20instead%20of%20some%20commands.rst
.. DO NOT TOUCH --- above links are automatically updated by issue/makeissuelist.py

.. _interface classes: :ref:`interface classes`
