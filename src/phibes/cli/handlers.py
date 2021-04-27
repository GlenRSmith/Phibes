"""
Click command handler functions
"""
# core library modules
from pathlib import Path

# third party packages
import click

# in-project modules
from phibes.cli.cli_config import CliConfig, write_config_file
from phibes.cli.errors import PhibesCliError, PhibesCliExistsError
from phibes.cli.errors import PhibesCliNotFoundError
from phibes.cli.lib import present_item, present_list_items
from phibes.cli.lib import user_edit_local_item
from phibes.cli.options import crypt_choices
from phibes.lib.config import ConfigModel, load_config_file
from phibes.lib.errors import PhibesExistsError, PhibesNotFoundError
from phibes.storage.types import StoreType
from phibes.lib import views


def set_store_config(**kwargs):
    """
    Sets up configuration of storage
    """
    if 'path' in kwargs:
        # inclusion of a `path` arg means FileSystem storage
        config = ConfigModel()
        config.store = {
            'store_type': StoreType.FileSystem.name,
            'store_path': kwargs['path']
        }
        config.apply()
        store_info = config.store
    elif 'config' in kwargs:
        # this should be the cli_config file
        config_file = kwargs.get('config')
        load_config_file(config_file)
        config = ConfigModel()
        store_info = config.store
    else:
        raise PhibesCliError('path required, from param or config file')
    return store_info


def create_locker(password: str, crypt_id: int, locker: str = None, **kwargs):
    """Create a Locker"""
    store_info = set_store_config(**kwargs)
    try:
        crypt_id = crypt_choices.choice_dict[crypt_id]
    except KeyError:
        raise PhibesCliError(f'invalid choice {crypt_id}')
    click.confirm(
        (
            f"Will attempt to create locker at\n"
            f"{store_info=}\n{crypt_id=}\n"
            f"Enter `y` to accept, `N` to abort"
        ), abort=True
    )
    try:
        resp = views.create_locker(
            password=password, locker_name=locker, crypt_id=crypt_id, **kwargs
        )
    except PhibesExistsError as err:
        raise PhibesCliExistsError(f"Locker already exists\n{err}")
    # TODO: use Locker.status!
    click.echo(f"Locker created {resp}")
    click.echo(f"{store_info}")
    click.echo(f"Was created {resp['timestamp']}")
    click.echo(f"Crypt ID {resp['crypt_id']}")


def get_locker(password: str, locker: str = None, **kwargs):
    """Get a Locker"""
    store_info = set_store_config(**kwargs)
    try:
        inst = views.get_locker(
            password=password, locker_name=locker, **kwargs
        )
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    if hasattr(inst, 'path'):
        click.echo(f"Locker stored as {inst.path}")
        if hasattr(inst.path, 'name'):
            click.echo(f"Locker stored as {inst.path.name}")
    click.echo(f"{store_info}")
    click.echo(f"Was created {inst['timestamp']}")
    click.echo(f"Crypt ID {inst['crypt_id']}")
    return inst


def delete_locker(password: str, locker: str = None, **kwargs):
    """Delete a Locker"""
    store_info = set_store_config(**kwargs)
    try:
        inst = views.get_locker(
            password=password, locker_name=locker, **kwargs
        )
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    click.confirm(
        (
            f"Will attempt to delete locker \n"
            f"{store_info=}\n"
            f"{inst=}\n"
            f"Enter `y` to accept, `N` to abort"
        ), abort=True
    )
    try:
        resp = views.delete_locker(
            password=password, locker_name=locker, **kwargs
        )
    except Exception as err:
        raise PhibesCliError(f"something went wrong {err=}")
    click.echo(resp)
    try:
        inst = views.get_locker(
            password=password, locker_name=locker, **kwargs
        )
    except PhibesNotFoundError:
        inst = None
    if not inst:
        click.echo("confirmed locker removed")
    else:
        click.echo("locker not removed")


def create_item(
        password: str,
        item: str,
        template: str = None,
        locker: str = None,
        **kwargs
):
    """Create an Item in a Locker"""
    # if any env_var options are in there, calling the config
    # constructor should set the relevant environment variable
    CliConfig(**kwargs)
    store_info = set_store_config(**kwargs)
    if template == 'Empty':
        template = None
    try:
        item_inst = views.get_item(
            password=password,
            locker_name=locker,
            item_name=item,
            **kwargs
        )
        if item_inst:
            raise PhibesCliExistsError(
                f"{item} already exists in locker {store_info}\n"
                f"please use the `edit` command to modify\n"
            )
    except PhibesNotFoundError:
        pass
    template_is_file = False
    if template:
        try:
            found = views.get_item(
                password=password,
                locker_name=locker,
                item_name=template,
                **kwargs
            )
            content = found['body']
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
        content = user_edit_local_item(item_name=item, initial_content=content)
    return views.create_item(
        password=password,
        locker_name=locker,
        item_name=item,
        content=content,
        **kwargs
    )


def edit_item(password: str, item: str, locker: str = None, **kwargs):
    """Edit the contents of an Item in a Locker"""
    # if any env_var options are in there, calling the config
    # constructor should set the relevant environment variable
    CliConfig(**kwargs)
    set_store_config(**kwargs)
    try:
        item_inst = views.get_item(
            password=password, locker_name=locker, item_name=item, **kwargs
        )
        if not item_inst:
            raise PhibesNotFoundError
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"{item} does not exist in locker\n"
        )
    content = user_edit_local_item(
        item_name=item, initial_content=item_inst['body']
    )
    return views.update_item(
        password=password,
        locker_name=locker,
        item_name=item,
        content=content,
        **kwargs
    )


def get_item(password: str, item: str, locker: str = None, **kwargs):
    """Get and display an Item from a Locker"""
    store_info = set_store_config(**kwargs)
    try:
        item_inst = views.get_item(
            password=password, locker_name=locker, item_name=item, **kwargs
        )
    except KeyError as err:
        raise PhibesCliError(err)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    ret_val = present_item(item_inst)
    click.echo(f"{store_info}")
    click.echo(f"{ret_val}")
    return item_inst


def get_items(password: str, locker: str = None, **kwargs):
    """Get and display all Items in a Locker"""
    set_store_config(**kwargs)
    try:
        items = views.get_items(
            password=password,
            locker_name=locker,
            **kwargs
        )
    except KeyError as err:
        raise PhibesCliError(err)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    report = present_list_items(
        items=items, verbose=kwargs.pop('verbose', True)
    )
    click.echo(f"{report}")
    return items


def delete_item(password: str, item: str, locker: str = None, **kwargs):
    """Delete an Item from a Locker"""
    set_store_config(**kwargs)
    try:
        resp = views.delete_item(
            password=password, locker_name=locker, item_name=item, **kwargs
        )
    except KeyError as err:
        raise PhibesCliError(err)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(err)
    click.echo(f"Item was probably removed: {resp}")
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
