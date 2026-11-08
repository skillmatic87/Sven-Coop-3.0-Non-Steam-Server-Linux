# Sven Co-op 3.0 Non-Steam Server — Linux Mint

Classic **12-slot LAN server** using original Windows WON HLDS under an isolated
Wine prefix on Linux Mint 22.x x86-64. Includes admin menus, persistent co-op
ranking, nominations/mapvotes, chat sounds and a local English/German panel.

**Preview 0.1.0:** Windows engine/plugin startup and map changes are verified.
Mint/Wine and actual client gameplay need the checks in [TESTING.md](docs/TESTING.md).
Players need matching **Sven Co-op 3.0 / Half-Life WON clients**. Current Steam
Sven clients cannot join this classic server.

## Install on Mint

Download the **full installer ZIP from Releases**, then extract it into a writable
folder. GitHub's automatic Source code ZIP has no component archives.
Allow 3 GiB free space. Install system dependencies once:

```bash
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install python3 wine wine32:i386 wine64 libicu74 ca-certificates
```

Then, as your normal user:

```bash
bash Setup-Linux.sh
bash Start-Server.sh
```

Setup verifies SHA-256 hashes and extracts the bundled original HLDS installer
with the bundled native Linux WiseUnpacker. Read and accept its original license.
No component downloads are needed. Installation creates `SvenServer-Linux`;
existing directories are never overwritten. Failed setups retain an `.incomplete`
marker and cannot start; inspect the error and use a new destination on retry.

Defaults: LAN, 12 slots, UDP **27016**, `sandstone`, normal difficulty.
CS 1.5 can continue on UDP 27015. No firewall or service changes are made.
Allow UDP 27016 if Mint's firewall blocks LAN access. Connect using
`connect MINT-LAN-IP:27016`. Set `bind` to the Mint LAN address during setup if
automatic interface selection is unsuitable; `0.0.0.0` means all interfaces.

## Panel and administrator access

```bash
bash Start-Panel.sh
```

The local panel opens at 127.0.0.1:8766 with a private session link. Start/stop,
server settings, map rotation, welcome text and player profiles are available in
German/English. Stop before saving; private configuration backups are created.
Closing the panel stops the server it started. Parallel launchers cannot own the
same server. Logs are written to `SvenServer-Linux/console.log` and game logs.

Generated credentials are in `SvenServer-Linux/ADMIN.local.txt`: use the selected
admin player name and its `setinfo _pw` instruction, then `amxmodmenu`. RCON has a
separate password. Never publish the installed server directory or its backups.

## Player features

- `/statsme`, `/rank`, `/top15`: co-op scoreboard points, deaths and playtime.
  This is the **Sven-specific StatsMe replacement**, not a CS StatsMe binary.
  Scoreboard points are not claimed to be monster kills or weapon accuracy.
- Persistent profiles use private `setinfo _scprofile` tokens. The first profile
  is documented in `ADMIN.local.txt`; create others in the panel. Save the line
  in each player's client `autoexec.cfg`. Names/IPs may change without merging
  players. Guests receive session statistics. Tokens are for a trusted LAN,
  not encrypted authentication. Admin rights are separate from ranking profiles.
- `/nominate mapname`, `/rtv`, `/nextmap`: nominate, request a vote or see the next
  map. RTV requires a majority and is available after two minutes. Voting lasts
  twenty seconds; RTV changes maps ten seconds after the result. Disconnecting
  removes that player's current ballot.
- Automatic votes apply to `sandstone`, `osprey`, `rampage`, five minutes before
  their configured limit (default thirty minutes). Other maps retain their native
  rules/transitions. The initial nomination list contains selected campaign starts
  and single maps. Preserve this when editing; a stage-two map is not a campaign
  start. Native Sven voting is disabled to avoid conflicting votes.
- Sank Sounds: chat WAVs, welcome sound, ten-second cooldown and twenty sounds
  per player/map. `/sounds` lists triggers.
- No bots are enabled; Counter-Strike YaPB is not a Sven co-op bot.

The original HLDS engine DLLs are preserved. The Sven installer's root `swds.dll`
is deliberately excluded because it prevents this HLDS build from starting.
Original WON resource-selection copies are applied during setup.

See [components and notices](docs/THIRD-PARTY.md) and [building](docs/BUILD.md).
Our Python/shell/HTML is MIT licensed; our AMXX plugins are GPL-2.0-or-later.
Third-party components and audio retain their own ownership and licenses.
