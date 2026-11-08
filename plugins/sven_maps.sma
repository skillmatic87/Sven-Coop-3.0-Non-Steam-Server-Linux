/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <amxmodx>
#include <amxmisc>
#define MAPS 128
new gMaps[MAPS][32],gCount,gNominations[5][32],gNomCount,gVoted[33],gRtv[33],gVotes[5];
new gOptions[5][32],gOptionCount,gMenu,gActive,gImmediate,gAutomatic,gSingle,gNext[32];
public plugin_init() {
    register_plugin("Sven Campaign Votes","0.1.0","Sven LAN Package");
    register_cvar("sven_maps_version","0.1.0",FCVAR_SERVER);
    register_cvar("sc_map_minutes","30"); register_cvar("amx_nextmap","");
    register_clcmd("say","chat");
    new path[192],line[128],len;
    get_configsdir(path,191); add(path,191,"/sven_maps.ini");
    for(new n=0;gCount<MAPS && read_file(path,n,line,127,len);n++) {
        trim(line); if(!len || line[0]==';' || !is_map_valid(line)) continue;
        copy(gMaps[gCount++],31,line);
    }
    set_task(5.0,"configure"); set_task(10.0,"tick",0,"",0,"b");
}
public configure() {
    new map[32];get_mapname(map,31);
    gSingle=equal(map,"sandstone") || equal(map,"osprey") || equal(map,"rampage");
    if(gSingle) {set_cvar_num("mp_timelimit",get_cvar_num("sc_map_minutes"));set_cvar_num("mp_fraglimit",0);}
    else {
        // HLDS may execute server.cfg after Sven's map config. Restore the
        // original per-map limits rather than replacing them with our defaults.
        new path[96],line[128],len,key[40],value[32];formatex(path,95,"maps/%s.cfg",map);
        for(new n=0;read_file(path,n,line,127,len);n++) {
            if(parse(line,key,39,value,31)!=2) continue;
            if(equal(key,"mp_timelimit") || equal(key,"mp_fraglimit")) set_cvar_float(key,str_to_float(value));
        }
    }
    set_cvar_num("mp_voteallow",0);
}
public client_disconnect(id) {
    if(gActive && gVoted[id]>0 && gVotes[gVoted[id]-1]>0) gVotes[gVoted[id]-1]--;
    gRtv[id]=0; gVoted[id]=0;
}
public tick() {
    if(!gSingle) return;
    new left=get_timeleft();
    if(left>0 && left<=300 && !gAutomatic && !gActive) { gAutomatic=1;start_vote(0); }
    if(left>0 && left<=15 && gNext[0] && !task_exists(900)) set_task(1.0,"change",900);
}
public chat(id) {
    new text[80],cmd[24],map[32];read_args(text,79);remove_quotes(text);parse(text,cmd,23,map,31);
    if(equal(cmd,"/nextmap")) {
        client_print(id,print_chat,"[Maps] %s",gNext[0]?gNext:"Campaign continuation / native map cycle");return PLUGIN_HANDLED;
    }
    if(equal(cmd,"/nominate")) {
        if(!map[0]) {client_print(id,print_chat,"[Maps] Use /nominate mapname. Campaign starts only.");return PLUGIN_HANDLED;}
        new found;for(new n=0;n<gCount;n++) if(equal(map,gMaps[n])) found=1;
        if(!found || gActive || gNomCount>=5) {client_print(id,print_chat,"[Maps] Map unavailable or nominations full.");return PLUGIN_HANDLED;}
        for(new n=0;n<gNomCount;n++) if(equal(map,gNominations[n])) return PLUGIN_HANDLED;
        copy(gNominations[gNomCount++],31,map);client_print(0,print_chat,"[Maps] Nominated: %s",map);return PLUGIN_HANDLED;
    }
    if(!equal(cmd,"/rtv")) return PLUGIN_CONTINUE;
    if(get_gametime()<120.0 || gActive || gNext[0]) {client_print(id,print_chat,"[Maps] RTV unavailable (first 2 minutes, active vote or pending change).");return PLUGIN_HANDLED;}
    gRtv[id]=1; new players,votes;
    for(new n=1;n<=32;n++) if(is_user_connected(n) && !is_user_bot(n)) {players++;votes+=gRtv[n];}
    client_print(0,print_chat,"[Maps] RTV: %d/%d",votes,players/2+1);
    if(votes>players/2) start_vote(1);
    return PLUGIN_HANDLED;
}
start_vote(immediate) {
    gOptionCount=0;new current[32];get_mapname(current,31);
    for(new n=0;n<gNomCount;n++) if(!equal(current,gNominations[n])) copy(gOptions[gOptionCount++],31,gNominations[n]);
    for(new n=0;n<gCount && gOptionCount<5;n++) {
        if(equal(current,gMaps[n])) continue;
        new duplicate;for(new k=0;k<gOptionCount;k++) if(equal(gMaps[n],gOptions[k])) duplicate=1;
        if(!duplicate) copy(gOptions[gOptionCount++],31,gMaps[n]);
    }
    if(!gOptionCount) return;
    gActive=1;gImmediate=immediate;arrayset(gVotes,0,5);arrayset(gVoted,0,33);
    gMenu=menu_create("Next map / Naechste Karte","voted");
    for(new n=0;n<gOptionCount;n++) menu_additem(gMenu,gOptions[n]);
    for(new id=1;id<=32;id++) if(is_user_connected(id) && !is_user_bot(id)) menu_display(id,gMenu);
    set_task(20.0,"finish_vote");
}
public voted(id,menu,item) {
    if(menu!=gMenu || !gActive || item==MENU_EXIT || item<0 || item>=gOptionCount || gVoted[id]) return PLUGIN_HANDLED;
    gVoted[id]=item+1;gVotes[item]++;return PLUGIN_HANDLED;
}
public finish_vote() {
    new best,votes;for(new n=0;n<gOptionCount;n++) {votes+=gVotes[n];if(gVotes[n]>gVotes[best]) best=n;}
    gActive=0; menu_destroy(gMenu);
    if(!votes) {arrayset(gRtv,0,33);client_print(0,print_chat,"[Maps] No votes; keeping the native map cycle.");return;}
    copy(gNext,31,gOptions[best]);set_cvar_string("amx_nextmap",gNext);
    client_print(0,print_chat,"[Maps] Selected: %s",gNext);
    if(gImmediate) set_task(10.0,"change",900);
}
public change() {if(is_map_valid(gNext)) server_cmd("changelevel %s",gNext);}
