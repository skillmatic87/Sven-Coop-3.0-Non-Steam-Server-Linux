# Components and notices

The release manifest records exact component hashes. Hashes identify inspected
files; independent publisher checksums are not claimed unless separately stated.

- HLDS 4.1.1.0, original installer retained unchanged:
  https://archive.org/download/goldsrc_hlds_won_windows/hlds-win/hlserver4110.exe
  SHA-256: `178fdf8a3d43ab91063ccb83be05be0457c98db348fc28eba6b9c9ea4e5dc849`.
  Original agreement is in `components/HLDS-LICENSE.txt` and shown at setup.
- Sven Co-op 3.0 original installer:
  https://valvearchive.com/Community/Mods/Sven%20Co-op/Builds/svencoop30.exe
  SHA-256: `410d56668a63e57a03a58a6668c9466dacf99eeeabfe2f76955c1e2c9c0c7f1c`.
  The operator installed it into an isolated folder with WON selected. Game
  resources are archived unchanged; only the machine-specific uninstall log is
  omitted. Original license.txt and notices are included. Root engine replacements
  supplied by this installer are excluded.
- Metamod-P 1.21p109 Windows, release and corresponding source:
  https://github.com/Bots-United/metamod-p/releases/tag/v1.21p109
- AMX Mod X 1.8.1 Windows base:
  https://sourceforge.net/projects/amxmodx/files/AMX%20Mod%20X%20Base/1.8.1/
  Source: https://github.com/alliedmodders/amxmodx/tree/amxmodx-1.8.1
- Sank Sounds 1.9.1, compiled with AMXX 1.8.1; source included beside binary:
  https://github.com/ZTHawk/HL1_SankSounds/tree/ed02c30bed512994b98e208c644c1e366b5209e3
- Classic WAV pack:
  https://sourceforge.net/projects/statsme/files/StatsMe%20Add-Ons/Soundpack%201.0/
  Additional WAVs come from the operator's existing CS LAN pack; third-party audio
  is not covered by our software license. Available original notices are retained.
- WiseUnpacker 3.0.0, native self-contained Linux x64 extraction tool:
  https://github.com/mnadareski/WiseUnpacker/releases/tag/3.0.0

Our plugins are GPL-2.0-or-later; other original components keep their own
licenses. Corresponding upstream sources are linked above and retained in the
release's third-party source bundle where available.

Sven's native Linux server was introduced in 4.7:
https://wiki.svencoop.com/Change_log/4.7 . This package runs the original Windows
3.0 GameDLL under Wine.
