Classic Sven Co-op 3.0 LAN package for Linux Mint 22.x x86-64 through Wine.

- 12 slots by default, UDP 27016; isolated Wine prefix.
- AMXX admin menus, persistent profile-based co-op scoreboard ranking.
- Nominations, majority RTV, automatic votes on managed single maps.
- Sank Sounds chat WAVs and welcome sound.
- Local German/English settings panel, private credentials and backups.
- Full offline installer inputs with SHA-256 verification and original notices.

**Preview:** original engine startup, 16 loaded plugins, fresh assembly and
`sandstone -> osprey -> incoming -> sandstone` were verified on Windows.
The managed 30-minute limit and incoming's original 120-minute limit were verified.
Python/launcher checks and five focused package/security tests pass.

**Mint/Wine startup and real-player gameplay/ranking/audio tests remain open.**
Use matching classic Sven 3.0/WON clients. Current Steam Sven clients cannot join.
Stats are a Sven-specific replacement, not the Counter-Strike StatsMe binary.
No bots are enabled.

Download the full **Sven-Coop-3.0-Linux-Mint-0.1.0-preview.zip**, extract it on Mint,
install the README dependencies, then run `bash Setup-Linux.sh` and
`bash Start-Panel.sh`. Automatic GitHub source ZIPs lack binary components.

Credentials are generated locally and documented in the installed server's
`ADMIN.local.txt`. Do not publish your installed directory or backups.
