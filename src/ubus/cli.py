import logging
import os
from pprint import pprint as pp, pformat as pf

import click
from click_configfile import matches_section, Param, SectionSchema, ConfigFileReader
# from click_repl import repl

from ubus import Ubus

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)

pass_ubus = click.make_pass_decorator(Ubus)

class ConfigSectionSchema:
    @matches_section("ubus")
    class Ubus(SectionSchema):
        host = Param(type=str)
        username = Param(type=str)
        password = Param(type=str)


class ConfigFileProcessor(ConfigFileReader):
    config_files = ["python-ubus.ini"]
    config_searchpath = [os.path.expanduser("~/.config/"), "."]
    config_section_schemas = [ ConfigSectionSchema.Ubus ]

CONTEXT_SETTINGS = dict(default_map=ConfigFileProcessor.read_config(),
                        ignore_unknown_options=True)


#class UbusCli(click.MultiCommand):
#    def list_commands(self, ctx):
#        return list(ctx.obj)


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option('--host', default='localhost')
@click.option('--username', default='')
@click.option('--password', default='')
@click.option('--debug/--no-debug', default=False)
@click.argument('unproc', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(ctx, host, username, password, debug, unproc):
    assert isinstance(ctx, click.Context)

    if debug:
        _LOGGER.setLevel(logging.DEBUG)
    ubus = Ubus(host, username, password)
    ctx.obj = ubus
    if len(unproc) == 0:
        ctx.invoke(list)
        return

    if unproc[0] in ctx.command.commands.keys():
        ctx.invoke(ctx.command.commands[unproc[0]])
        return

    # TODO cleanup and allow repling of this
    # 1. list interface methods
    # pyubus dhcp
    if len(unproc) == 1:
        ns = unproc[0]
        click.echo("== %s ==" % ns)
        for m in ubus[ns]:
            click.echo(" * %s" % ubus[ns][m])
        return
    # 2. call method with or without parameters
    # pyubus dhcp ipv4leases
    # pyubus iwinfo assoclist device=wlan0
    elif len(unproc) >= 2:
        with ubus:
            ns, cmd, *params = unproc
            m = ubus[ns][cmd]
            params_dict = {}

            for param in params:
                k, v = param.split("=")
                params_dict[k] = v

            click.echo("Calling %s with %s" % (m, params_dict))
            res = m(**params_dict)
            click.echo("Result: %s" % pf(res))
            return


#@main.command()
#@pass_ubus
#def repl(ubus):
#    repl(click.get_current_context(), prompt_kwargs={})


@main.command()
@pass_ubus
def list(ubus):
    click.echo("Printing interfaces..")
    for iface in ubus:
        click.echo("> %s" % iface)
        for method in iface:
            click.echo("\t * %s" % method)
        click.echo()


@main.command()
@pass_ubus
def leases(ubus):
    with ubus:
        #print(ubus["dhcp"]["ipv4leases"]())
        def get_host_for_mac(leases, mac):
            simple_mac = assoc['mac'].replace(':', '').lower()
            if simple_mac in leases:
                return leases[simple_mac]
            return "<unknown>"

        mac_to_host = {}
        for dev in ubus["dhcp"]["ipv4leases"]().values():
            for iface, leases in dev.items():
                for vlist in leases.values():
                    for lease in vlist:
                        mac_to_host[lease['mac']] = lease['hostname']

        for device in ubus["iwinfo"]["devices"]():
            for assoc in ubus["iwinfo"]["assoclist"](device=device):
                print("%s (%s) - signal: %s, inactive: %s)" % (
                    get_host_for_mac(mac_to_host, assoc['mac']),
                    assoc['mac'],
                    assoc['signal'],
                    assoc['inactive']))

        #print(ubus["dhcp"]["ipv4leases"].has_access())
        #return

if __name__ == "__main__":
    main()
