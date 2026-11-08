/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <amxmodx>
#include <amxmisc>
#include <nvault>
#define PROFILES 128
new gVault, gCount, gHash[PROFILES][34], gLabel[PROFILES][32],gFrozen;
new gProfile[33], gPoints[33], gDeaths[33], gSeconds[33], gLastScore[33];
public plugin_init() {
    register_plugin("Sven LAN Statistics", "0.1.0", "Sven LAN Package");
    register_cvar("sven_stats_version", "0.1.0", FCVAR_SERVER);
    register_clcmd("say", "chat"); register_clcmd("say_team", "chat");
    register_event("DeathMsg", "death", "a");
    register_event("ScoreInfo", "score_info", "a");
    register_event("30", "freeze", "a");
    gVault=nvault_open("sven_profiles");
    if(gVault==INVALID_HANDLE) set_fail_state("Cannot open ranking vault");
    new path[192], line[128], len, hash[34], label[32];
    get_configsdir(path,191); add(path,191,"/sven_profiles.ini");
    for(new n=0; gCount<PROFILES && read_file(path,n,line,127,len); n++) {
        if(!len || line[0]==';') continue;
        if(parse(line,hash,33,label,31)!=2 || strlen(hash)!=32) continue;
        new valid=1;
        for(new c=0;label[c];c++) if(!(label[c]>='a' && label[c]<='z') && !(label[c]>='A' && label[c]<='Z') && !(label[c]>='0' && label[c]<='9') && label[c]!='_' && label[c]!='-' && label[c]!='.') valid=0;
        if(!valid) continue;
        copy(gHash[gCount],33,hash); copy(gLabel[gCount],31,label); gCount++;
    }
    set_task(1.0,"sample",0,"",0,"b"); set_task(30.0,"save_all",0,"",0,"b");
}
public client_putinserver(id) {
    gProfile[id]=0; gPoints[id]=0; gDeaths[id]=0; gSeconds[id]=0;
    gLastScore[id]=get_user_frags(id);
    new token[40], hash[34]; get_user_info(id,"_scprofile",token,39);
    if(!token[0]) return;
    md5(token,hash);
    for(new p=0;p<gCount;p++) {
        if(!equal(hash,gHash[p])) continue;
        for(new other=1;other<=32;other++) if(other!=id && is_user_connected(other) && gProfile[other]==p+1) {
            client_print(id,print_chat,"[Stats] Profile already online; using guest session."); return;
        }
        gProfile[id]=p+1;
        new data[96], a[24], b[24], c[24];
        if(nvault_get(gVault,hash,data,95) && parse(data,a,23,b,23,c,23)==3) {
            gPoints[id]=str_to_num(a); gDeaths[id]=str_to_num(b); gSeconds[id]=str_to_num(c);
        }
        return;
    }
}
update_score(id) {
    if(gFrozen) return;
    new score=get_user_frags(id);
    gPoints[id]+=score-gLastScore[id]; gLastScore[id]=score;
}
public score_info() {new id=read_data(1);if(id>=1 && id<=32 && is_user_connected(id)) update_score(id);}
public sample() {
    if(gFrozen) return;
    for(new id=1;id<=32;id++) if(is_user_connected(id) && !is_user_bot(id)) {
        update_score(id); gSeconds[id]++;
    }
}
public freeze() {save_all();gFrozen=1;}
public death() {
    new id=read_data(2);
    if(id>=1 && id<=32 && is_user_connected(id)) gDeaths[id]++;
}
save(id) {
    if(!gProfile[id]) return;
    if(is_user_connected(id)) update_score(id);
    new data[96]; formatex(data,95,"%d %d %d",gPoints[id],gDeaths[id],gSeconds[id]);
    nvault_set(gVault,gHash[gProfile[id]-1],data);
}
public save_all() { for(new id=1;id<=32;id++) if(is_user_connected(id)) save(id); }
public client_disconnect(id) { save(id); gProfile[id]=0; }
public plugin_end() { save_all(); if(gVault!=INVALID_HANDLE) nvault_close(gVault); }
public chat(id) {
    new text[80]; read_args(text,79); remove_quotes(text);
    if(equal(text,"/statsme") || equal(text,"/rank")) {
        if(is_user_connected(id)) update_score(id);
        client_print(id,print_chat,"[Stats] %s | Co-op points: %d | Deaths: %d | Minutes: %d",gProfile[id]?gLabel[gProfile[id]-1]:"Guest (session only)",gPoints[id],gDeaths[id],gSeconds[id]/60);
        if(gProfile[id]) {
            save_all();new rank=1,data[96],a[24],b[24],c[24];
            for(new p=0;p<gCount;p++) {
                if(p==gProfile[id]-1) continue;
                if(nvault_get(gVault,gHash[p],data,95) && parse(data,a,23,b,23,c,23)==3 && (str_to_num(a)>gPoints[id] || (str_to_num(a)==gPoints[id] && str_to_num(b)<gDeaths[id]))) rank++;
            }
            client_print(id,print_chat,"[Stats] Rank: %d / %d profiles",rank,gCount);
        }
        if(!gProfile[id]) client_print(id,print_chat,"[Stats] Ask the operator for your private profile configuration.");
        return PLUGIN_HANDLED;
    }
    if(!equal(text,"/top15")) return PLUGIN_CONTINUE;
    save_all();
    new points[PROFILES], deaths[PROFILES], used[PROFILES], data[96], a[24], b[24], c[24];
    for(new p=0;p<gCount;p++) {
        points[p]=0;deaths[p]=0;
        if(nvault_get(gVault,gHash[p],data,95) && parse(data,a,23,b,23,c,23)==3) {
            points[p]=str_to_num(a); deaths[p]=str_to_num(b);
        }
    }
    new html[2048], pos; pos=formatex(html,2047,"<html><body><h3>Co-op Top 15</h3><pre>Profile / Points / Deaths^n");
    for(new rank=0;rank<15 && rank<gCount;rank++) {
        new best=-1;
        for(new p=0;p<gCount;p++) if(!used[p] && (best<0 || points[p]>points[best] || (points[p]==points[best] && deaths[p]<deaths[best]))) best=p;
        used[best]=1;
        pos+=formatex(html[pos],2047-pos,"%d. %s / %d / %d^n",rank+1,gLabel[best],points[best],deaths[best]);
    }
    add(html,2047,"</pre><p>Co-op points are scoreboard points, not monster kills.</p></body></html>");
    show_motd(id,html,"Co-op Top 15"); return PLUGIN_HANDLED;
}
