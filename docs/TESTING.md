# Tests and remaining acceptance

Observed on Windows, 2026-11-08:

- Original HLDS 4.1.1.0 starts Sven 3.0: protocol 46, build 2056, twelve slots.
- RCON confirms both sandstone and osprey after changing maps.
- Metamod-P loads AMXX 1.8.1.3746. Engine, nVault and FakeMeta report running.
- All sixteen configured AMXX plugins load, including our statistics/mapvotes
  and Sank Sounds 1.9.1. Loaded does not mean gameplay-verified.
- The Sven installer's root swds.dll prevents HLDS startup. Preserving the HLDS
  original fixes it; installation checks engine hashes after assembly.

Required on Mint/Wine before calling this a stable release:

1. Fresh setup: native extraction, Wine initialization, console startup, clean
   stop/restart. Check version/status/meta list/amxx modules/amxx plugins.
2. sandstone -> osprey -> sandstone; status must confirm each map, not just a
   fixed delay. Two actual classic clients must join, fight and respawn.
3. Admin menu with correct credentials and denied access without them. Map/sound
   downloads and chat sounds audible to both clients, including cooldown/quota.
4. Two distinct profiles; same names, renamed users, changed IP, reconnect and
   server restart must not merge identities. New profile B must remain zero after
   saved profile A has fifty points. A second concurrent user of one token gets
   guest statistics. Profile tokens never grant admin access.
5. Validate actual Sven DeathMsg victim semantics and positive/negative scoreboard
   deltas. Immediate disconnect, intermission and mapchange must retain final
   scores. Score is frozen at intermission. No monster-kill claim is made.
6. Nomination, majority RTV, no-vote result and reconnect during a vote. Natural
   afrikakorps/toonrun continuation must not be redirected. Check native limits on
   unmanaged maps including incoming and hostage.
7. Panel DE/EN, backups, invalid settings/maps rejected, duplicate starts refused,
   settings writes refused while another launcher owns the installation.
8. Twelve simultaneous clients or a documented equivalent load test. Twelve
   configured slots alone do not establish this capacity.

Ranking is checkpointed every thirty seconds and at orderly disconnect/shutdown.
A hard machine/process crash may lose the last unsaved interval.
