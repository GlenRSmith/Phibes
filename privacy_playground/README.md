Python Privacy Playground is a utility to keep your secrets (passwords, restore codes, etc.) in an encrypted storage location on your filesystem.

As this is an early work-in-progress, I would discourage the use of it as an actual single-storage of passwords you can't afford to lose.

####Usage

The command-line interface follows the approach `./ppp.py <item> <action>` followed by prompts for necessary information.

- Create a Locker for all of your Secrets

```
> ./ppp.py locker create
```

You will then be prompted for a locker name and a password.
It is important to never forget/lose the password, as it is absolutely irretrievable, and without it, nothing in your Locker will be accessible.

For each of the operations below, you will be prompted for the name and password of the Locker.

- Add a Secret to your Locker

```
./ppp.py secret edit
```
Your configured editor will be launched with a temporary file.
Put your secret information in this file, save, and exit, and the contents will be encrypted and saved as a Secret in your Locker.
(The temporary file is immediately deleted.)

- Confirm that your Secret is in your Locker
```
./ppp.py secret list-all
```
You will be presented a list of the names of all Secrets in the Locker.

- See the unencrypted contents of your Secret
```
./ppp.py secret inspect
```
You will be shown your unencrypted Secret.

