# Building the preview

Build with Python 3.11+ on Windows and the AMXX 1.8.1 compiler. The development
helper currently uses the parent CS workspace's research cache; the delivered
Mint package is independent of that workspace.

Required research inputs: original HLDS installer and its WiseUnpacker extraction,
AMXX base extraction, Metamod-P Windows archive, pinned Sank Sounds source and
soundpack archive under the parent's `downloads/research`. The parent project's
components manifest records their original source hashes.

Install the checksum-identified Sven 3.0 installer into a separate folder, select
WON, and retain its original files/notices. Obtain the official WiseUnpacker
3.0.0 net10.0_linux-x64_release.zip as `runtime/sven-wise-linux.zip` in the parent
workspace. Do not overwrite an existing game/server installation.

```text
python scripts/build.py --sven PATH-TO-ISOLATED-SVEN-INSTALL
python scripts/check.py
python scripts/package.py
```

The generated release ZIP includes all installer inputs and their manifest.
Publish only the allowlisted source files, installer ZIP and SHA-256 file.
Never publish installed credentials, operator profiles, backups or test logs.
GitHub's automatic source ZIP lacks binary components and cannot run setup alone.
