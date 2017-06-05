Python interface for Ubus
=========================

This package provides a pythonic interface for accessing
`ubus <https://wiki.openwrt.org/doc/techref/ubus>` over its
separately packaged JSON-RPC interface.

Library use
===========

Ubus class is the entrypoint to access all functionalities of this
package, which provides an access to the available interfaces:

::

    ubus = Ubus('router.local')
    for iface in ubus.interfaces:
        print(iface)

Besides iterator interface the interfaces can be accessed with a
dict-style accessors, which also return ``UbusNamespace`` objects for
accessing the underlying methods.

::

    dhcp = ubus['dhcp']
    for method in dhcp:
         print(method)

``UbusMethod`` class implement ``__call__`` to allow easy execution of
methods:

::

    v4leases = dhcp['ipv4leases']()

Where required, the parameters are passed as dictionaries:

::

    ubus['session']['login'](username='user', password='1234')

Context manager support
-----------------------

Ubus constructor accepts username and password as parameters, which in
turn allows using the class as a context-manager to simplify session
handling:

::

    with Ubus('router.local', 'user', '1234') as ubus:
        wlan0_devices = ubus['iwinfo']['assoclist'](device='wlan0')

Command-line utility
====================

There is also a simple command-line interface (similar to ubus
command-line tool) called pyubus, which enables running arbitrary
commands from the console. When no parameters are given it will output
the list of available namespaces (calls implicitly list command, more
information in --help). All unknown commands are interpreted as
namespaces names, so listing all available methods in namespace 'dhcp'
can be done by simply calling:

::

    $ pyubus dhcp

Methods can be directly executed by passing their name, and potential
parameters in ``key=value`` format to the utility:

::

    $ pyubus iwinfo assoclist device=wlan0

Configuration can be either passed as options or through creating an
ini-style configuration file in ~/.config/python-ubus.ini:

::

    [ubus]
    host = router.local
    username = user
    password = 1234
