"""
Click command handler functions
"""
# core library modules
from pathlib import Path

# third party packages
import click

# in-project modules
from phibes.cli.cli_config import CliConfig
from phibes.cli.cli_config import write_config_file
from phibes.cli.errors import PhibesCliError
from phibes.cli.errors import PhibesCliExistsError
from phibes.cli.errors import PhibesCliNotFoundError
from phibes.cli.lib import present_list_items2
from phibes.cli.lib import user_edit_local_item
from phibes.cli.options import crypt_choices
from phibes.lib.config import ConfigModel, load_config_file, StoreType
from phibes.lib.errors import PhibesExistsError
from phibes.lib.errors import PhibesNotFoundError
from phibes import text_views


def make_common_kwargs(**kwargs):
    """
    Returns a dict with entries common to all Phibes requests
    """
    try:
        ret_val = {'password': kwargs.get('password')}
    except KeyError:
        raise PhibesCliError('missing password')
    if 'path' in kwargs:
        store_path = kwargs.get('path')
    elif 'config' in kwargs:
        # this should be the cli_config file
        config_file = kwargs.get('config')
        load_config_file(config_file)
        store_path = ConfigModel().store_path
    else:
        raise PhibesCliError('path required, from param or config file')
    ret_val['locker'] = kwargs.get('locker', None)
    ret_val['store_type'] = StoreType.FileSystem
    ret_val['store_path'] = store_path  # this should get posted to Config.
    try:
        CliConfig().work_path = str(store_path.absolute())
    except TypeError as err:
        raise PhibesCliError(
            f"{err=}"
            f"{str(store_path.absolute())=}"
        )
    return ret_val


def create_locker(*args, **kwargs):
    """Create a Locker"""
    req_args = make_common_kwargs(**kwargs)
    try:
        path = req_args.get('store_path')
        crypt_int = kwargs.get('crypt_id')
    except KeyError as err:
        raise PhibesCliError(f'missing required param {err}')
    try:
        crypt_id = crypt_choices.choice_dict[crypt_int]
    except KeyError:
        raise PhibesCliError(f'invalid choice {crypt_int}')
    click.confirm(
        (
            f"Will attempt to create locker at\n"
            f"{path=}\n{crypt_id=}\n"
            f"Enter `y` to accept, `N` to abort"
        ), abort=True
    )
    try:
        resp = text_views.create_locker(crypt_id=crypt_id, **req_args)
    except PhibesExistsError as err:
        raise PhibesCliExistsError(f"Locker already exists\n{err}")
    # TODO: use Locker.status!
    click.echo(f"Locker created {resp}")


def get_locker(*args, **kwargs):
    """Get a Locker"""
    req_args = make_common_kwargs(**kwargs)
    try:
        inst = text_views.get_locker(**req_args)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)

    # click.echo(f"Locker stored as {inst['path']}")
    # click.echo(f"Created {inst['timestamp']}")
    # click.echo(f"Crypt ID {inst['crypt_impl']['crypt_id']}")
    # raise PhibesCliError(f"Locker {inst}")

    click.echo(f"Locker stored as {inst.path.name}")
    click.echo(f"Locker stored as {inst.path}")
    click.echo(f"Created {inst.timestamp}")
    click.echo(f"Crypt ID {inst.crypt_impl.crypt_id}")

    # Don't present server details
    # if inst.path.exists():
    #     click.echo(f"confirmed locker dir {inst.path} exists")
    # if inst.lock_file.exists():
    #     click.echo(f"confirmed lock file {inst.lock_file} exists")
    return inst


def delete_locker(*args, **kwargs):
    """Delete a Locker"""
    req_args = make_common_kwargs(**kwargs)
    try:
        inst = text_views.get_locker(**req_args)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    click.confirm(
        (
            f"Will attempt to delete locker with\n"
            f"{inst.path.resolve()}\n"
            f"Enter `y` to accept, `N` to abort"
        ), abort=True
    )
    try:
        resp = text_views.delete_locker(**req_args)
    except Exception as err:
        raise PhibesCliError(f"something went wrong {err=}")
    click.echo(resp)
    try:
        inst = text_views.get_locker(**req_args)
    except PhibesNotFoundError:
        inst = None
    if not inst:
        click.echo("confirmed locker removed")
    else:
        click.echo("locker not removed")


def create_item(*args, **kwargs):
    """Create an Item in a Locker"""
    req_args = make_common_kwargs(**kwargs)
    template = kwargs.get('template', None)
    if template == 'Empty':
        template = None
    try:
        item_name = kwargs.get('item')
    except KeyError as err:
        raise PhibesCliError(f'missing required param {err}')
    try:
        item_inst = text_views.get_item(item_name=item_name, **req_args)
        if item_inst:
            raise PhibesCliExistsError(
                f"{item_name} already exists in locker\n"
                f"please use the `edit` command to modify\n"
            )
    except PhibesNotFoundError:
        pass
    template_is_file = False
    if template:
        try:
            # try to get an item stored by the template name
            # TODO: Things like this will break when text_views
            #       are fixed to not return objects!
            found = text_views.get_item(item_name=template, **req_args)
            content = found.content
        except PhibesNotFoundError:
            try:
                # try to find a local file by that name
                content = Path(template).read_text()
                template_is_file = True
            except PhibesNotFoundError:
                raise PhibesCliNotFoundError(f"{template} not found")
            except FileNotFoundError:
                raise PhibesCliNotFoundError(f"{template} not found")
    else:
        content = ''
    if not template_is_file:
        content = user_edit_local_item(
            item_name=item_name, initial_content=content
        )
    return text_views.create_item(
        item_name=item_name, content=content, **req_args
    )


def edit_item(*args, **kwargs):
    """Edit the contents of an Item in a Locker"""
    req_args = make_common_kwargs(**kwargs)
    try:
        item_name = kwargs.get('item')
    except KeyError as err:
        raise PhibesCliError(f'missing required param {err}')
    try:
        item = text_views.get_item(item_name=item_name, **req_args)
        if not item:
            raise PhibesNotFoundError
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"{item_name} does not exist in locker\n"
        )
    content = user_edit_local_item(
        item_name=item_name, initial_content=item.content
    )
    return text_views.update_item(
        item_name=item_name, content=content, **req_args
    )


def get_item(*args, **kwargs):
    """Get and display an Item from a Locker"""
    req_args = make_common_kwargs(**kwargs)
    try:
        item_inst = text_views.get_item(
            item_name=kwargs['item'], **req_args
        )
    except KeyError as err:
        raise PhibesCliError(err)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    click.echo(f"{item_inst}")
    return item_inst


def get_items(*args, **kwargs):
    """Get and display all Items in a Locker"""
    req_args = make_common_kwargs(**kwargs)
    try:
        items = text_views.get_items(**req_args)
    except KeyError as err:
        raise PhibesCliError(err)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    report = present_list_items2(
        items=items, verbose=kwargs.pop('verbose', True)
    )
    click.echo(f"{report}")
    return items


def delete_item(*args, **kwargs):
    """Delete an Item from a Locker"""
    req_args = make_common_kwargs(**kwargs)
    try:
        resp = text_views.delete_item(
            item_name=kwargs['item'], **req_args
        )
    except KeyError as err:
        raise PhibesCliError(err)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    click.echo(f"{resp}")
    return resp


def edit_cli_config(create=True, **kwargs):
    """
    Provide values for a Phibes CLI config file
    """
    # There are options required for this command,
    # and there are options required to populate the config file
    # Maybe let the CliConfig class raise the errors for the latter
    # because e.g. if we are changing just our editor, we
    # shouldn't have to provide the store_path
    try:
        path = kwargs.get('path')
    except KeyError as err:
        raise PhibesCliError(f'missing required param {err}')
    try:
        new_config = CliConfig(**kwargs)
        new_config.validate()
        write_config_file(path, new_config, update=not create)
    except ValueError as err:
        raise PhibesCliError(err)
    except FileExistsError as err:
        raise PhibesCliExistsError(err)
    except FileNotFoundError as err:
        raise PhibesCliExistsError(err)
    return


def create_cli_config(**kwargs):
    """
    Provide values for a new Phibes CLI config file
    """
    edit_cli_config(create=True, **kwargs)


def update_cli_config(**kwargs):
    """
    Provide values to update an existing Phibes CLI config file
    """
    edit_cli_config(create=False, **kwargs)
