const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const source=fs.readFileSync('preserved/candidate/youtube.response.js','utf8');
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
assert.equal(sha(source),'f98483d5f5017514f82502253c0db5ce2d4ffb7839887aa2cadc22666f5a7f12');
const original=fs.readFileSync('preserved/original.sgmodule','utf8');
const candidate=fs.readFileSync('preserved/candidate/YouTube-Original-Reviewed.sgmodule','utf8');
assert.equal(candidate,original.replace('https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js','https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/scripts/youtube.original.response.js'));
const stats={cases:0,network:0,unexpectedStorage:0};
function context(body,path='player',args={},agent='com.google.ios.youtube'){
 const done=[],writes=[],reads=[];
 const headers=new Proxy({'User-Agent':agent},{get(t,k){if(k==='Cookie'||k==='Authorization')throw Error('sensitive header access');return t[k]}});
 const c={Uint8Array,ArrayBuffer,TextEncoder,TextDecoder,console:{log(){}},$argument:JSON.stringify(args),$request:{url:'https://youtubei.googleapis.com/youtubei/v1/'+path,headers},$response:{body},$persistentStore:{read(k){reads.push(k);if(!['YouTubeAdvertiseInfo','YouTubeConfig'].includes(k)){stats.unexpectedStorage++;throw Error(k)}return null},write(v,k){writes.push([k,v]);return true}},$notification:{post(){}},$done(v){done.push(v)},$httpClient:new Proxy({},{get(){stats.network++;throw Error('unexpected network')}})};
 vm.createContext(c);return{c,done,writes,reads};
}
const marker='try{Ki()}catch(l){console.log(String(l)),F.exit()}';
assert.ok(source.includes(marker));
const h=context(new Uint8Array());
vm.runInContext(source.replace(marker,'globalThis.types={player:oe,watch:ei,reel:zr,guide:Zr,setting:Qr};'),h.c,{timeout:1000});
const types=h.c.types;
function run(bytes,path,args,agent){const x=context(bytes,path,args,agent);vm.runInContext(source,x.c,{timeout:1000});assert.equal(x.done.length,1);stats.cases++;return x;}
const player=types.player.create({adPlacements:[{}],adSlots:[{}],playabilityStatus:{}});
const input=types.player.toBinary(player);
for(const agent of ['com.google.ios.youtube','com.google.ios.youtubemusic']){
 const x=run(input,'player',{},agent),p=types.player.fromBinary(x.done[0].body);
 assert.equal(p.adPlacements.length,0);assert.equal(p.adSlots.length,0);
 assert.equal(p.playabilityStatus.pictureInPictureRender.pictureInPictureAbility.active,true);
 assert.equal(p.playabilityStatus.backgroundPlayerRender.backgroundAbility.active,true);
 assert.equal(x.writes.length,0);
}
const w=run(types.watch.toBinary(types.watch.create({contents:[{player}]})),'get_watch');
assert.equal(types.watch.fromBinary(w.done[0].body).contents[0].player.adSlots.length,0);
const reel=types.reel.create({entries:[{command:{reelWatchEndpoint:{adClientParams:{isAd:true}}}},{command:{reelWatchEndpoint:{adClientParams:{isAd:false}}}}]});
const r=run(types.reel.toBinary(reel),'reel/reel_watch_sequence');assert.equal(types.reel.fromBinary(r.done[0].body).entries.length,1);
for(const path of ['browse','next','search','guide']){const x=run(new Uint8Array(),path);assert.equal(x.writes.length,0);}
const settings=run(types.setting.toBinary(types.setting.create()),'account/get_setting');
assert.ok(types.setting.fromBinary(settings.done[0].body).settingItems.some(x=>x.backgroundPlayBackSettingRenderer));
for(const b of [[255],[10,255],[0],[58,128]]){const x=run(new Uint8Array(b),'player');assert.equal(Object.keys(x.done[0]).length,0);}
// User's module excludes config/log_event; query strings must not reach these handlers.
for(const q of ['config','log_event']){const x=run(input,'player?'+q+'=1');assert.equal(x.writes.length,0);assert.equal(types.player.fromBinary(x.done[0].body).adSlots.length,0);}
assert.equal(stats.network,0);assert.equal(stats.unexpectedStorage,0);
fs.writeFileSync('preserved/test-results.json',JSON.stringify({...stats,sourceSha256:sha(source),moduleOnlyChange:'script-path URL',scope:'Synthetic protobuf fixtures; not an iOS or live account test'},null,2)+'\n');
console.log(stats);
