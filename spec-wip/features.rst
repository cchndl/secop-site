Features
========

Features allow the ECS to detect if a SECoP module support a certain functionality.
A feature typically needs some predefined accessibles and/or module properties to be present.
However, it is not only a list of mandatory or optional accessibles, but
indicates to the ECS that it may handle this functionality in a specific way.

.. _HasOffset:

``"HasOffset"``
    This feature is indicating that the value and target parameters are raw values, which
    need to be corrected by an offset. A module with the feature ``"HasOffset"`` must have
    a parameter ``offset``, which indicates to all clients that values are to be converted
    by the following formulas:

          ECS value = SECoP value + offset

          SECoP target = ECS target - offset

    mandatory parameter: offset
