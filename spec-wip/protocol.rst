Protocol
========

The basic element of the protocol are messages.


Message Syntax
--------------
The received byte stream which is exchanged via a connection is split into messages:

.. image:: images/messages.svg
   :alt: messages ::= (message CR? LF) +

A message is essentially one line of text, coded in ASCII (may be extended to UTF-8
later if needed). A message ends with a line feed character (ASCII 10), which may be preceded
by a carriage return character (ASCII 13), which must be ignored.

All messages share the same basic structure:

.. image:: images/message-structure.svg
   :alt: message_structure ::= action ( SPACE specifier ( SPACE data )? )?

i.e. message starts with an action keyword, followed optionally by one space and a specifier
(not containing spaces), followed optionally by one space and a JSON-value (see :RFC:`8259`) called data,
which absorbs the remaining characters up to the final LF.

.. note::
    numerical values and strings appear 'naturally' formatted in JSON-value, i.e. 5.0 or "a string".

The specifier consists of a module identifier, and for most actions, followed by a colon as separator
and an accessible identifier. In special cases (e.g. ``describe``, ``ping``), the specifier is just a token or may be empty:

.. image:: images/specifier.svg
   :alt: specifier ::= module | module ":" (parameter|command)

All identifiers (for properties, accessibles and modules) are composed by
ASCII letters, digits and underscore, where a digit may not
appear as the first character.

.. image:: images/name.svg
   :alt: name ::= [a-zA-Z_] [a-zA-Z0-9_]*

Identifiers starting with underscore ('custom-names') are
reserved for special purposes like internal use for debugging. The
identifier length is limited (<=63 characters).

.. note::
    Albeit names MUST be compared/stored case sensitive, names in each scope need to be unique when lowercased.
    The scopes are:

    - module names on a SEC Node (including the group entries of those modules)
    - accessible names of a module (including the group entries of those parameters) (each module has its own scope)
    - properties
    - names of elements in a :ref:`struct` (each struct has its own scope)
    - names of variants in an :ref:`enum` (each enum has its own scope)
    - names of qualifiers

SECoP defined names are usually lowercase, though that is not a restriction (esp. not for module names).

A SEC node might implement custom messages for debugging purposes, which are not
part of the standard. Custom messages start with an underscore or might just be
an empty line. The latter might be used as a request for a help text, when logged
in from a command line client like telnet or netcat. Messages not starting with
an underscore and not defined in the following list are reserved for future extensions.

When implementing SEC nodes or ECS-clients, a 'MUST-ignore' policy should be applied to unknown
or additional parts.
Unknown or malformed messages are to be replied with an appropriate ``ProtocolError`` by a SEC node.
An ECS-client must ignore the extra data in such messages. See also section :ref:`future-compatibility`.

Essentially the connections between an ECS and a SEC node can operate in one of two modes:

Synchronous mode:
   where a strict request/reply pattern is used

Async mode:
   where an update may arrive any time (between messages).

In both cases, a request from the ECS to the SEC node is to be followed by an reply from the SEC node to the ECS,
either indicating success of the request or flag an error.

.. note::
    an ECS may try to send a request before it received the reply to an earlier request.
    This has two implications: a SEC-node may serialize requests and fulfill them strictly in order.
    In that case the ECS should not overflow the input buffer of the SEC-node.
    The second implication is that an ECS which sends multiple requests, before the replies arrive,
    MUST be able to handle the replies arriving out-of-order. Unfortunately there is currently no indication
    if a SEC-node is operating strictly in order or if it can work on multiple requests simultaneously.

.. note::
    to improve compatibility, any ECS client SHOULD be aware of `update`_ messages at any time.

.. note::
    to clarify optionality of some messages, the following table is split into two:
    basic messages (which MUST be implemented like specified) and
    extended messages which SHOULD be implemented.

.. note::
    for clarification, the symbol "``␣``" is used here instead of a space character.
    <elem> refers to the element elem which is defined in another section.


.. table:: basic messages (implementation is mandatory, even if functionality seems not to be needed.)

    ======================= ============== ==================
     message intent          message kind   message elements
    ======================= ============== ==================
     `identification`_       request        ``*IDN?``
          \                  reply          ISSE\ **,SECoP,**\ *version,add.info*
     `description`_          request        ``describe``
          \                  reply          ``describing␣.␣``\ <:ref:`structure-report`>
     `activate updates`_     request        ``activate``
          \                  reply          ``active``
     `deactivate updates`_   request        ``deactivate``
          \                  reply          ``inactive``
     `heartbeat`_            request        ``ping␣<identifier>``
          \                  reply          ``pong␣<identifier>␣``\ <:ref:`data-report`>
     `change value`_         request        ``change␣<module>:<parameter>␣``\ <:ref:`value`>
          \                  reply          ``changed␣<module>:<parameter>␣``\ <:ref:`data-report`>
     `execute command`_      request        ``do␣<module>:<command>`` (**argumentless commands only**)
          \                  reply          ``done␣<module>:<command>␣``\ <:ref:`data-report`> (with null as value)
     `read request`_         request        ``read␣<module>:<parameter>``
        \                    reply          ``reply␣<module>:<parameter>␣``\ <:ref:`data-report`>
     value update_  event    event          ``update␣<module>:<parameter>␣``\ <:ref:`data-report`>
     `error reply`_          reply          ``error_<action>␣<specifier>␣``\ <:ref:`error-report`>
    ======================= ============== ==================

.. note::
    This means that ``change`` needs to be implemented, even if only readonly accessibles are present.
    In this case, a ``change`` message will naturally be replied with an ``error_change``
    message with an :ref:`error class <error-classes>` of "ReadOnly" and not with an "ProtocolError".

.. table:: extended messages (implementation is optional)

    ======================= ============== ==================
     message intent          message kind   message elements
    ======================= ============== ==================
     `logging`_              request        ``logging␣<module>␣``\ <loglevel>
         \                   reply          ``logging␣<module>␣``\ <loglevel>
         \                   event          ``log␣<module>:<loglevel>␣<message-string>``
     `activate updates`_     request        ``activate␣<module>``
       module-wise           reply          ``active␣<module>``
     `deactivate updates`_   request        ``deactivate␣<module>``
       module-wise           reply          ``inactive␣<module>``
     `heartbeat`_            request        ``ping``
      with empty identifier  reply          ``pong␣␣``\ <:ref:`data-report`>
     `execute command`_      request        ``do␣<module>:<command>␣``\ (\ :ref:`value` | ``null``)
          \                  reply          ``done␣<module>:<command>␣``\ <:ref:`data-report`>
    ======================= ============== ==================


Theory of operation:
    The first messages to be exchanged after the a connection between an ECS and a SEC node is established
    is to verify that indeed the SEC node is speaking a supported protocol by sending an identification_ request
    and checking the answer from the SEC node to comply.
    If this check fails, the connection is to be closed and an error reported.
    The second step is to query the structure of the SEC node by exchange of description_ messages.
    After this step, the ECS knows all it needs to know about this SEC node and can continue to either
    stick to a request/reply pattern or `activate updates`_.
    In any case, an ECS should correctly handle updates, even if it didn't activate them,
    as that may have been performed by another client on a shared connection.

Correct handling of side-effects:
  To avoid difficult to debug race conditions, the following sequence of events should be followed,
  whenever the ECS wants to initiate an action:

  1) ECS sends the initiating message request (either ``change`` target or ``do`` go) and awaits the response.

  2) SEC-node checks the request and if it can be performed. If not, SEC-node sends an error-reply (sequence done).
     If nothing is actually to be done, continue to point 4)

  3) If the action is fast finishing, it should be performed and the sequence should continue to point 4.
     Otherwise the SEC-node 'sets' the status-code to BUSY and instructs the hardware to execute
     the requested action.
     Also an ``update`` status event (with the new BUSY status-code) MUST be sent
     to **ALL** activated clients (if any).
     From now on all read requests will also reveal a BUSY status-code.
     If additional parameters are influenced, their updated values should be communicated as well.

  4) SEC-node sends the reply to the request of point 2) indicating the success of the request.

     .. note::
         This may also be an error. In that case point 3) was likely not fully performed.

     .. note::
        An error may be replied after the status was sent to BUSY:
        if triggering the intended action failed (Communication problems?).

  5) when the action is finally finished and the module no longer to be considered BUSY,
     an ``update`` status event MUST be sent, also subsequent status queries
     should reflect the now no longer BUSY state. Of course, all other parameters influenced by this should also
     communicate their new values.

.. note::
     An ECS establishing more than one connection to the same sec-node and
     which **may** process the ``update`` event message from point 3)
     after the reply of point 4) MUST query the status parameter synchronously
     to avoid the race-condition of missing the (possible) BUSY status-code.

.. note::
     temporal order should be kept wherever possible!



Message intents
---------------

Identification
~~~~~~~~~~~~~~

The syntax of the identification message differs a little bit from other
messages, as it should be compatible with IEEE 488.2. The identification
request "\ **\*IDN?**\ " is meant to be sent as the first message after
establishing a connection. The reply consists of 4 comma separated
fields, where the second and third field determine the used protocol.

In this and in the following examples, messages sent to the SEC-node are marked with "> ",
and messages sent to the ECS are marked with "< "

Example:

.. code::

  > *IDN?
  < ISSE,SECoP,V2019-09-16,v1.0

As the first part of the message has changed, a SECoP client SHOULD allow also the previous
form "ISSE&SINE2020" and an erroneously used form "SINE2020&ISSE", but can assume that
the second part "SECoP" is given as defined.
So far the SECoP version is given like "V2019-09-16", i.e. a capital "V" followed by a date in
``year-month-day`` format with 4 and 2 digits respectively.
The ``add.info`` field was used to differentiate between draft, release candidates (rc1, rc2,...) and final.
It is now used to indicate a release name.


Description
~~~~~~~~~~~

The next messages normally exchanged are the description request and
reply. The reply contains the :ref:`structure-report`, i.e. a structured JSON object describing the name of
modules exported and their parameters, together with the corresponding
properties.

Example:

.. code::

  > describe
  < describing . {"modules":{"t1":{"interface_classes":["TemperatureSensor","Readable"],"accessibles":{"value": ...

The dot (second item in the reply message) is a placeholder for extensibility reasons.
A client implementing the current specification MUST ignore it.

.. admonition:: Remark

    this reply might be a very long line, no raw line breaks are allowed in the
    JSON part! I.e. the JSON-part should be as compact as possible.

.. note::
    The use of a single dot for the specifier is a little contrary to the other messages addressing the
    SEC-node. It may be changed in a later revision. ECS-clients are advised to ignore the specifier part
    of the describing message. A SEC-node SHOULD use a dot for the specifier.

Activate Updates
~~~~~~~~~~~~~~~~

The parameterless "activate" request triggers the SEC node to send the
values of all its modules and parameters as update messages (initial updates). When this
is finished, the SEC node must send an "active" reply. (*global activation*)

.. note::
    the values transferred are not necessarily read fresh from the hardware, check the timestamps!

.. note::
    This initial update is to help the ECS establish a copy of the 'assumed-to-be-current' values.

.. note::
    An ECS MUST be able to handle the case of an extra update occurring during the initial phase, i.e.
    it must handle the case of receiving more than one update for any valid specifier.

A SEC node might accept a module name as second item of the
message (*module-wise activation*), activating only updates on the parameters of the selected module.
In this case, the "active" reply also contains the module name.

A SEC Node not implementing module-wise activation MUST NOT sent the module
name in its reply to an module-wise activation request,
and MUST activate all modules (*fallback mode*).

Update
~~~~~~

When activated, update messages are delivered without explicit request
from the client. The value is a :ref:`data-report`, i.e. a JSON array with the value as its first
element, and an JSON object containing the :ref:`qualifiers` as its second element.

If an error occurs while determining a parameter, an ``error_update`` message has to be sent,
which includes an <:ref:`error-report`> stating the problem.

Example:

.. code::

  > activate
  < update t1:value [295.13,{"t":150539648.188388,"e":0.01}]
  < update t1:status [[400,"heater broken or disconnected"],{"t":1505396348.288388}]
  < active
  < error_update t1:_heaterpower ["HardwareError","heater broken or disconnected",{"t":1505396349.20}]
  < update t1:value [295.14,{"t":1505396349.259845,"e":0.01}]
  < update t1:value [295.13,{"t":1505396350.324752,"e":0.01}]

The example shows an ``activate`` request triggering an initial update of two values:
t1:value and t1:status, followed by the ``active`` reply.
Also, an ``error_update`` for a parameter ``_heaterpower`` is shown.
After this two more updates on the ``t1:value`` show up after roughly 1s between each.

.. note::
    it is vital that all initial updates are sent, **before** the 'active' reply is sent!
    (an ECS may rely on having gotten all values)

.. note::
    to speed up the activation process, polling + caching of all parameters on the SEC-node is advised,
    i.e. the parameters should not just be read from hardware for activation, as this may take a long time.


Another Example with a broken Sensor:

.. code::

  > activate
  < error_update t1:value ["HardwareError","Sensor disconnected", {"t":1505396348.188388}]}]
  < update t1:status [[400,"Sensor broken or disconnected"],{"t":1505396348.288388}]
  < active

Here the current temperature can not be obtained. An ``error_update`` message is used
instead of ``update``.

Deactivate Updates
~~~~~~~~~~~~~~~~~~

A parameterless message. After the "inactive" reply no more updates are
delivered if not triggered by a read message.

Example:

.. code::

  > deactivate
  < update t1:value [295.13,{"t":1505396348.188388}]
  < inactive

.. admonition:: Remark

    the update message in the second line was sent before the deactivate message
    was treated. After the "inactive" message, the client can expect that no more untriggered
    update message are sent, though it MUST still be able to handle (or ignore) them, if they still
    occur.

The deactivate message might optionally accept a module name as second item
of the message for module-wise deactivation. If module-wise deactivation is not
supported, the SEC-node should ignore a deactivate message which contains a module name
and send an ``error_deactivate`` reply.
This requires the ECS being able to handle update events at any time!

.. admonition:: Remark

    it is not clear, if module-wise deactivation is really useful. A SEC Node
    supporting module-wise activation does not necessarily need to support module-wise
    deactivation.

Change Value
~~~~~~~~~~~~

The change value message contains the name of the module or parameter
and the value to be set. The value is JSON formatted.
As soon as the set-value is read back from the hardware, all clients,
having activated the parameter/module in question, get an "update" message.
After all side-effects are communicated, a "changed" reply is then send, containing a
:ref:`data-report` of the read-back value.

.. admonition:: Remarks

    * If the value is not stored in hardware, the "update" message can be sent immediately.
    * The read-back value should always reflect the value actually used.
    * an client having activated updates may get an ``update`` message before the ``changed`` message, both containing the same data report.


Example on a connection with activated updates. Qualifiers are replaced by {...} for brevity here.

.. code::

  > read mf:status
  < reply mf:status [[100,"OK"],{...}]
  > change mf:target 12
  < update mf:status [[300,"ramping field"],{...}]
  < update mf:target [12,{...}]
  < changed mf:target [12,{...}]
  < update mf:value [0.01293,{...}]

The status changes from "idle" (100) to "busy" (300).
The ECS will be informed with a further update message on mf:status,
when the module has finished ramping.
Until then, it will get regular updates on the current main value (see last update above).

.. note::
    it is vital that all 'side-effects' are realized (i.e. stored in internal variables) and be communicated, **before** the 'changed' reply is sent!


Read Request
~~~~~~~~~~~~

With the read request message the ECS may ask the SEC node about a reasonable recent value 'current' value.
In most cases this means, that the hardware is read to give a fresh value.
However, there are uses case where either an internal control loop is running anyway
in which case it is perfectly fine to returned the internally cached value.
In other cases (ls370+scanner) it may take a long time to actually obtain a fresh value,
in which case it is also fine to return the most recently obtained value.
In any way, the timestamp qualifier should indicate the time the value was **obtained**.

Example:

.. code::

  > read t1:value
  < reply t1:value [295.13,{"t":1505396348.188}]
  > read t1:status
  > reply t1:status [[100,"OK"],{"t":1505396348.548}]


Execute Command
~~~~~~~~~~~~~~~

Actions can be triggered with a command.
If an action needs significant time to complete (i.e. longer than a fraction of a second),
the information about the duration and success of such an action has to be
transferred via the ``status`` parameter.

If a command is specified with an argument, the actual argument is given in
the data part as a JSON-value. This may be also a JSON-object if the datatype of
the argument specifies that
(i.e. the type of the single argument can also be a :ref:`struct` or :ref:`tuple`, see :ref:`data-types`).
The types of arguments must conform to the declared datatypes from the datatype of the command argument.

A command may also have a return value, which may also be structured.
The "done" reply always contains a :ref:`data-report` with the return value.
If no value is returned, the data part is set to "null".
The "done" message should be returned quickly, the time scale should be in the
order of the time needed for communications. Still, all side-effects need to be realized
and communicated before sending the ``done`` message.


.. important:: If a command does not require an argument, an argument MAY still be transferred as JSON-null.
 A SEC node MUST also accept the message, if the data part is empty and perform the same action.
 More precisely, any SEC-node MUST treat the following two messages the same:

 - ``do <module>:<command>``
 - ``do <module>:<command> null``

 An ECS SHOULD only generate the shorter version.

Example:

.. code::

  > do t1:stop
  < done t1:stop [null,{"t":1505396348.876}]

  > do t1:stop null
  < done t1:stop [null,{"t":1505396349.743}]


.. _error-reply:

Error Reply
~~~~~~~~~~~

Contains an error class from the list below as its second item (the specifier).
The third item of the message is an :ref:`error-report`, containing the request message
(minus line endings) as a string in its first element, a (short) human readable text
as its second element. The third element is a JSON-Object, containing possibly
implementation specific information about the error (stack dump etc.).

Example:

.. code::

  > read tx:target
  < error_read tx:target ["NoSuchModule","tx is not configured on this SEC node", {}]
  > change ts:target 12
  < error_change ts:target ["NoSuchParameter","ts has no parameter target", {}]
  > change t:target -9
  < error_change t:target ["RangeError","requested value (-9) is outside limits (0..300)", {}]
  > meas:volt?
  < error_meas:volt?  ["ProtocolError","unknown action", {}]

.. _error-classes:

_`Error Classes`:
    Error classes are divided into two groups: persisting errors and retryable errors.
    Persisting errors will yield the exact same error message if the exact same
    request is sent at any later time without other interactions inbetween.
    A retryable error may give different results if the exact same message is sent at a later time, i.e.
    they depend on state information internal to either the SEC-node, the module or the connected hardware.

    .. list-table:: persisting errors
        :widths: 20 80

        * - ProtocolError
          - A malformed Request or on unspecified message was sent.
            This includes non-understood actions and malformed specifiers. Also if the message exceeds an implementation defined maximum size.
            *note: this may be retryable if induced by a noisy connection. Still that should be fixed first!*

        * - NoSuchModule
          - The action can not be performed as the specified module is non-existent.

        * - NoSuchParameter
          - The action can not be performed as the specified parameter is non-existent.

        * - NoSuchCommand
          - The specified command does not exist.

        * - ReadOnly
          - The requested write can not be performed on a readonly value.

        * - WrongType
          - The requested parameter change or Command can not be performed as the argument has the wrong type.
            (i.e. a string where a number is expected.)
            It may also be used if an incomplete struct is sent, but a complete struct is expected.

        * - RangeError
          - The requested parameter change or Command can not be performed as the argument value is not
            in the allowed range specified by the ``datainfo`` property.
            This also happens if an unspecified Enum variant is tried to be used, the size of a Blob or String
            does not match the limits given in the descriptive data, or if the number of elements in an :ref:`array`
            does not match the limits given in the descriptive data.

        * - BadJSON
          - The data part of the message can not be parsed, i.e. the JSON-data is no valid JSON.

        * - NotImplemented
          - A (not yet) implemented action or combination of action and specifier was requested.
            This should not be used in productive setups, but is very helpful during development.

        * - HardwareError
          - The connected hardware operates incorrect or may not operate at all due to errors inside or in connected components.

    .. list-table:: retryable errors
        :widths: 20 80

        * - CommandRunning
          - The command is already executing. request may be retried after the module is no longer BUSY.

        * - CommunicationFailed
          - Some communication (with hardware controlled by this SEC node) failed.

        * - TimeoutError
          - Some initiated action took longer than the maximum allowed time.

        * - IsBusy
          - The requested action can not be performed while the module is Busy or the command still running.

        * - IsError
          - The requested action can not be performed while the module is in error state.

        * - Disabled
          - The requested action can not be performed while the module is disabled.

        * - Impossible
          - The requested action can not be performed at the moment.

        * - ReadFailed
          - The requested parameter can not be read just now.

        * - OutOfRange
          - The value read from the hardware is out of sensor or calibration range

        * - InternalError
          - Something that should never happen just happened.

    .. admonition:: Remark

        This list may be extended, if needed. clients should treat unknown error classes as generic as possible.


.. Zwischenüberschrift: extended messages? optionale messages?

Logging
~~~~~~~

Logging is an optional message, i.e. a sec-node is not enforced to implement it.

``logging``
  followed by a specifier of <modulename> and a string in the JSON-part which is either "debug", "info", "error" or is the JSON-value false.
  This is supposed to set the 'logging level' of the given module (or the whole SEC-node if the specifier is empty) to the given level:

  This scheme may also be extended to configure logging only for selected parameters of selected modules.

  :"off":
    Remote logging is completely turned off.
  :"error":
    Only errors are logged remotely.
  :"info":
    Only 'info' and 'error' messages are logged remotely.
  :"debug":
    All log messages are logged remotely.

  A SEC-node should reply with an :ref:`error-report` (``ProtocolError``) if it doesn't implement this message.
  Otherwise it should mirror the request, which may be updated with the logging-level actually in use.
  i.e. if an SEC-node does not implement the "debug" level, but "error" and "info" and an ECS request "debug" logging, the
  reply should contain "info" (as this is 'closer' to the original request than "error") or ``false``).
  Similarly, if logging of a too specific item is requested, the SEC-node should activate the logging on the
  least specific item where logging is supported. e.g. if logging for <module>:<param> is requested, but the SEC-node
  only support logging of the module, this should be reflected in the reply and the logging of the module is to be influenced.

  .. note:: it is not foreseen to query the currently active logging level. It is supposed to default to ``"off"``.

``log``
  followed by a specifier of <modulename>:<loglevel> and the message to be logged as JSON-string in the datapart.
  This is an asynchronous event only to be sent by the SEC-node to the ECS which activated logging.


example::

  > logging  "error"           ; note: empty specifier -> select all modules
  < logging  "error"           ; SEC-node confirms
  < log mod1:debug "polling value"
  < log mod1:debug "sending request..."
  ...

another example::

  > logging mod1 "debug"       ; enable full logging of mod1
  < logging mod1 "error"       ; SEC-node can only log errors, logging of errors of mod1 is now active
  < log mod1:error "value par1 can not be determined, please refill read-out liquid"
  ...
  > logging mod1 false
  < logging mod1 false


.. _heartbeat:

Heartbeat
~~~~~~~~~

In order to detect that the other end of the communication is not dead,
a heartbeat may be sent. The second part of the message (the id) must
not contain a space and should be short and not be re-used.
It may be omitted. The reply will contain exactly the same id.

A SEC node replies with a ``pong`` message with a :ref:`data-report` of a null value.
The :ref:`qualifiers` part SHOULD only contain the timestamp (as member "t") if the
SEC node supports timestamping.
This can be used to synchronize the time between ECS and SEC node.

.. admonition:: Remark

    The qualifiers could also be an empty JSON-object, indicating lack of timestamping support.

For debugging purposes, when *id* in the ``ping`` request is omitted,
in the ``pong`` reply there are two spaces after ``pong``.
A client SHOULD always send an id. However, the client parser MUST treat two
consecutive spaces as two separators with an empty string in between.

Example:

.. code::

  > ping 123
  < pong 123 [null, {"t": 1505396348.543}]

:Related SECoP Issues: `SECoP Issue 3: Timestamp Format`_ and `SECoP Issue 7: Time Synchronization`_


Handling timeout Issues
~~~~~~~~~~~~~~~~~~~~~~~

If a timeout happens, it is not easy for the ECS to decide on the best strategy.
Also there are several types of timeout: idle-timeout, reply-timeout, etc...
Generally speaking: both ECS and SEC side needs to be aware that the other
side may close the connection at any time!
On reconnect, it is recommended, that the ECS does send a ``*IDN?`` and a ``describe`` message.
If the responses match the responses from the previous connection, the ECS should continue
without any internal reconfiguring, as if no interruption happened.
If the response of the description does not match, it is up to the ECS how to handle this.

Naturally, if the previous connection was activated, an ``activate``
message has to be sent before it can continue as before.

:Related SECoP Issues: `SECoP Issue 4: The Timeout SEC Node Property`_ and `SECoP Issue 6: Keep Alive`_


Multiple Connections
--------------------

A SEC node may restrict the number of simultaneous connections.
However, each SEC node should support as many connections as technically
feasible.



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
