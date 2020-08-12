Phibes is a utility to keep your secrets (passwords, restore codes, etc.) in an encrypted storage location on your filesystem.

As this is an early work-in-progress, I would discourage the use of it as an actual single-storage of passwords you can't afford to lose.

####Installation

At this time, the app isn't available through PyPi, so you'll have to install from github.

Clone the repository and install it in a virtual environment (python 3.8).

####Setup/Config

With your virtual environment activated and phibes installed, you can run the `config` command, and be prompted for some requisite details, with some defaults provided.

- location of configuration file [default is user home directory]
- editor [default is from $EDITOR if it is set]
- storage location [default is current working directory]

The file, `.phibes-conf.json`, is a simple json file that you can also edit directly.

Each time you issue a command, the app will search for a config file as follows:

- path provided as part of the command
- environment variable "PHIBES_CONFIG"
- current working directory
- user home directory

######Editor

In the command-line client, addition/update of Items to a Locker is done by executing the `edit` command, which will launch an editor and store the encrypted contents of the file when you save and exit. (Some editors, like Atom, are problematic because they don't block python when they are invoked. I recommend configuring vim, emacs, or nano.)

When you issue the edit command, the editor to use will be the first of:
- `editor` specified as part of the command
- `editor` specified in discovered config file (see above)
- environment variable `PHIBES_EDIT`

######Storage Path

This will be where the data you add is stored.
When you issue a command, the app will determine the storage path as follows:
- `storage_path` specified as part of the command
- `storage_path` specified in discovered config file (see above)
- environment variable `PHIBES_STORE`

####Usage

The command-line interface follows the approach `./ppp.py <item> <action>` followed by prompts for necessary information.

- Create a Locker for all of your Secrets

```
> ./phibes_cli.py locker create
```

You will then be prompted for a locker name and a password.
It is important to never forget/lose these, as they are irretrievable, and without them, nothing in your Locker will be accessible.

For each of the operations below, you will be prompted for the name and password of the Locker.

- Add a Secret to your Locker

```
./phibes_cli.py edit --item-type secret
```
Your configured editor will be launched with a temporary file.
Put your secret information in this file, save, and exit, and the contents will be encrypted and saved as a Secret in your Locker.
(The temporary file is immediately deleted.)

- Confirm that your Secret is in your Locker
```
./phibes_cli.py secret list-all
```
You will be presented a list of the names of all Secrets in the Locker.

- See the unencrypted contents of your Secret
```
./phibes_cli.py secret inspect
```
You will be shown your unencrypted Secret.


