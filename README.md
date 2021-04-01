![Test](https://github.com/GlenRSmith/Phibes/workflows/Test/badge.svg)

Phibes is a utility to keep your secrets (passwords, restore codes, etc.) in an encrypted storage location on your filesystem.

As this is an early work-in-progress, I would discourage the use of it as an actual single-storage of passwords you can't afford to lose.

## Installation

At this time, the app isn't available through PyPi, so you'll have to install from github.

Clone the repository and install it in a virtual environment (python 3.8 or later) using pip.

## Basic usage

By default, these commands all prompt the user for all available options.

They each prompt for the file system path to the locker, defaulting to the current working directory.

They each prompt for password, with a repeat for confirmation prompt when initializing the locker.

Available subcommands are: `init`, `status`, `delete`, `add`, `get`, `edit`, `list`, and `remove`.

1. In a command shell, change your working directory to an empty folder where you want your locker to exist.

1. Initialize the locker:

    `phibes init`

    You will be prompted for the `crypt_id`. This defaults to the current best available, which you should accept.

1. Add an item to the locker:

    `phibes add`

    This step requires that you have a valid editor set in one of the environment variables `PHIBES_EDITOR` or `EDITOR`.
    
    You will be prompted for the item name, and an optional template name.

    The template name can be any named item already in your locker. If you provide a valid name, the contents of that item will be used for the initial contents of your new item. If you accept the default, "Empty", you will start with an empty document.

    You will _not_ be prompted for `editor`, but you can pass it with the command, e.g.:

    `phibes add --editor vim`
   
    You must otherwise have a valid editor set in one of the environment variables `PHIBES_EDITOR` or `EDITOR`.
   
    After you reply to all the prompts, your configured editor will be launched, and when you save and exit, the contents of the temporary file will be encrypted and stored in a new item in your locker, and the temporary file deleted.

1. Edit an item in the locker:

   `phibes edit`

    You will be prompted for an item name. If the item exists in the locker, your editor will be launched with the current content of the item. When you save and exit, the contents of the temporary file will be encrypted and the item in your locker updated, and the temporary file deleted.

1. Report an item in the locker:

   `phibes get`

    You will be prompted for an item name. If the item exists in the locker, the contents will be decrypted and reported to the console.

1. Report all items in the locker:

   `phibes list`

    You will be prompted for `Verbose`. If you select `verbose`, the full details (including decrypted content) of all items in the locker will be reported. Otherwise, only the names of all items in the locker will be reported.
   
1. Remove an item from the locker:

   `phibes remove`

    You will be prompted for an item name. If the item exists in the locker, it will be removed.

1. Report on the locker:

   `phibes status`

    The storage location, creation time, and crypt ID will be reported to the console.

1. Delete the locker:

   `phibes delete`

    The locker will be deleted.

## Setup/Config

With your virtual environment activated and phibes installed, you can run the `config` command, and be prompted for some requisite details, with some defaults provided.

- location of configuration file [default is user home directory]
- editor [default is from $EDITOR if it is set]
- storage location [default is current working directory]

The file, `.phibes.cfg`, is a simple json file that you can also edit directly.

Each time you issue a command, the app will search for a config file as follows:

- path provided as part of the command (`--config`)
- user home directory

### Editor

In the command-line client, addition/update of Items to a Locker is done by executing the `edit` command, which will launch an editor and store the encrypted contents of the file when you save and exit. (Some editors, like Atom, are problematic because they don't block python when they are invoked. I recommend configuring vim, emacs, or nano.)

When you issue the edit command, phibes will attempt to launch the editor you have specified in your config.
There is no attempt made to validate that what you've configured is valid prior to this execution.

### Storage Path

This will be where the data you add is stored.
When you issue a command, the app will use the storage from your configuration file.

When you use the CLI to create a config file, the default storage path is in the directory `.phibes` in the user's home directory.

## Usage

The command-line interface follows the approach `phibes.py <command>` followed by prompts for options. You may also provide these options as part of the command line.

- Create a Locker for all of your Secrets

```
> ./phibes_cli.py  create-locker
```

You will then be prompted for a locker name and a password.
**It is crucial to never forget/lose these, as they are irretrievable, and without them, nothing in your Locker will be accessible.**

For each of the operations below, you will be prompted for the name and password of the Locker.

- Add a Secret to your Locker

```
./phibes_cli.py create-item
```
Your configured editor will be launched with a temporary file.
Put your secret information in this file, save, and exit, and the contents will be encrypted and saved as a Secret in your Locker.
(The temporary file is immediately deleted.)

- Confirm that your Secret is in your Locker
```
./phibes_cli.py list
```
You will be presented a list of the names of all Items in the Locker.

- See the unencrypted contents of your Secret
```
./phibes_cli.py get-item --item <your item name>
```
You will be shown your unencrypted Secret. (You can also pass the `verbose` parameter to the `list` command.)
