## About
mbu (modular backup utility) is a simple command-line tool for compressing and encrypting the contents of directories. It is primarily intended to be a flexible backend
for software that automatically and repetitively transfers files from a fixed, local position over a network. If paired with such software, this tool can be used to ensure security and integrity of the tranferred data. However, it can also be used in isolation to package files for manual transfer, or back them up to a connected storage medium.

## Operation details
mbu utilizes AES together with GCM for encryption and validation. In the interest of avoiding local key storage, it derives a temporary key from a password supplied by the user via PBKDF2HMAC. A hash of this password is stored under user_password in config.toml, which is used to confirm password validity before each usage. A persistent salt for PBKDF2HMAC is also stored after the initial password setup to ensure determinism. This should not be a grave issue for a single-user application, especially as an ephemeral key is needed. Still, bear in mind that mbu's key security could certainly be improved on.

There is currently no way to reset your password without replacing the value of user_password with an empty string (""), which should probably not be done if you have old archives that you still want to decrypt.

If packaging a directory manually (via -o/--package), the generated key should only exist in memory for a very brief period of time. Running mbu in watching mode (-w/--watch) will store the key in memory until the process is terminated. In any case, the security of whatever you encrypt is dependent on that of your machine; if someone other than you has simultaneous access to it, it would not be difficult at all to extract your key from memory.

### Basic usage
To compress and encrypt a directory named directory, and store the result in the packaging directory specified in config.toml:

[python3] mbu.py -o directory

To decrypt a previous backup of a directory, and decompress it into the restore directory specified in config.toml:

[python3] mbu.py -d directory

If you've already set up a password, you can skip the password prompt using -p or --password followed by your password:

[python3] mbu.py -p password [options]

You can tell mbu to continuously watch a directory for changes, and back it up automatically if changes are detected like so:

[python3] mbu.py -w directory

Note that currently, this just makes the program iteratively check the sizes and modification times of the target directory's contents against a previous record of them, calling Packer.make_package() if they differ. While it is a very simple algorithm that ought to work on or at least be adaptable to many operating systems, it is also fairly resource intensive. So unless you need to automate interfacing with a frontend, you might consider making manual backups with -o instead.

## Platforms and dependencies
mbu was designed to be platform-agnostic, and its only dependency save for the Python standard library is [cryptography 44.0.0](https://pypi.org/project/cryptography/). That being said, it has only been tested with Python 3.11.2 on Linux, so there may exist some undetected bugs on other platforms.

## State of the project
At present, this tool is functional but can be improved considerably. Though no promise of further development will be made, the following possible improvements are acknowledged:

*Better key security
*Built-in frontend options (the "pigeon")
*Confirm and/or ensure platform agnosticism
*Replace watching algorithm with something less resource-hungry
*Database stuff

That being said, the user is encouraged to report any bugs found.

