![Test](https://github.com/GlenRSmith/Phibes/workflows/Test/badge.svg)

Phibes is a utility to keep your secrets (passwords, restore codes, etc.) in an encrypted storage location on your filesystem.

As this is an early work-in-progress, I would discourage the use of it as an actual single-storage of passwords you can't afford to lose.

## Installation

`pip install phibes`

## Basic usage

The basic usage command is `phibes`. Available subcommands are: `init`, `status`, `delete`, `add`, `get`, `edit`, `list`, and `remove`.

They each prompt for the file system path to the locker, defaulting to the current working directory. (This can also be passed with `--path your/path`)

They each prompt for password, with a repeat for confirmation prompt when initializing the locker.

**It is crucial to never forget/lose your password, as it is irretrievable, and without it, nothing in your Locker will be accessible.**

1. In a command shell, change your working directory to an empty folder where you want your locker to exist.

1. Initialize the locker:

    `phibes init`

    You will be prompted for the `crypt_id`. This defaults to the current best available, which you should accept.

1. Add an item to the locker:

    `phibes add`

    You will be prompted for the item name, and an optional template name.

    The template name can be any named item already in your locker. If you provide a valid name, the contents of that item will be used for the initial contents of your new item. If you accept the default, "Empty", you will start with an empty document.

    You will _not_ be prompted for `editor`, but you can pass it with the command, e.g.:

    `phibes add --editor vim`
   
    You must otherwise have a valid editor set in one of the environment variables `PHIBES_EDITOR` or `EDITOR`.
   
    After you reply to all the prompts, your configured editor* will be launched, and when you save and exit, the contents of the temporary file will be encrypted and stored in a new item in your locker, and the temporary file deleted.

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

## Advanced usage

The advanced usage command is `phibesplus`. Available subcommands are: `create`, `info`, `delete`, `create-item`, `get-item`, `edit`, `list`, `delete-item`, `create-config`, and `update-config`.

Advanced usage differs from basic usage in several important ways:
 - Lockers have user-assigned names.
 - Operations depend on a stored configuration.
 - Multiple lockers can be stored in the same configured storage location.

1. Create a configuration

   `phibesplus create-config`

   You will be prompted for the location to save the new config file, and for relevant details to be stored in the config file.

   - location of configuration file [default is user home directory]
   - editor [default is from $EDITOR if it is set]
   - storage location [default is user home directory/.phibes]
   
   The file, `.phibes.cfg`, is a simple json file that you can also edit directly.
   
   Each time you issue a command, the app will search for a config file as follows:
   
   - path provided as part of the command (`--config`)
   - user home directory
   
1. Update a configuration

   `phibesplus update-config`

   Has the same prompts as `create-config`, but expects the config file to already exist.

1. Create a locker

   `phibesplus create`

   You will be prompted for a locker name and a password.
   **It is crucial to never forget/lose these, as they are irretrievable, and without them, nothing in your Locker will be accessible.**

1. Create an item in the locker

   `phibesplus create-item`

1. Edit an item in the locker

   `phibesplus edit`

1. Report an item in the locker

   `phibesplus get-item`

1. Report all items in the locker

   `phibesplus list`

1. Remove an item from the locker

   `phibesplus delete-item`

1. Report on the locker:

   `phibesplus info`

1. Delete the locker:

   `phibesplus delete`


### Editor

In the command-line client, addition/update of Items to a Locker is done by executing the `add/edit` commands, which will attempt to launch a configured editor, and store the encrypted contents of the file when you save and exit. (Some editors, like Atom, are problematic because they don't block python when they are invoked. We recommend configuring vim, emacs, or nano.)

There is no attempt made to confirm that what you've configured is valid prior to this execution.

### Storage Path

This will be where the data you add is stored.
When you issue a command, the app will use the storage from your configuration file.

When you use the CLI to create a config file, the default storage path is in the directory `.phibes` in the user's home directory.
