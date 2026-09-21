const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync('scripts/youtube.response.js','utf8');
const stats={cases:0,network:0,keyAccess:0};
function context(body,url='https://youtubei.googleapis.com/youtubei/v1/player'){
 const writes=[],done=[];
 const c={Uint8Array,ArrayBuffer,TextEncoder,TextDecoder,console:{log(){}},$request:{url,headers:{}},$response:{body},$persistentStore:{read(k){if(k!=='YouTubeReviewedAdvertiseInfo'){stats.keyAccess++;throw Error('unexpected read '+k)}return null},write(v,k){assert.equal(k,'YouTubeReviewedAdvertiseInfo');writes.push([k,v]);return true}},$notification:{post(){}},$done(v){done.push(v)},$httpClient:new Proxy({}, {get(){return ()=>{stats.network++;throw Error('network prohibited')}}})};
 vm.createContext(c);return {c,writes,done};
}
let h=context(new Uint8Array());
const marker='try{Ki()}catch(l){F.exit()}';assert.ok(source.includes(marker));
vm.runInContext(source.replace(marker,'globalThis.testTypes={player:oe,watch:ei,reel:zr,next:re,search:Yr,browse:qr};'),h.c,{timeout:1000});
const types=h.c.testTypes;
function run(bytes,path){const x=context(bytes,'https://youtubei.googleapis.com/youtubei/v1/'+path);vm.runInContext(source,x.c,{timeout:1000});assert.equal(x.done.length,1);stats.cases++;return x;}
const player=types.player.create({adPlacements:[{}],adSlots:[{}],playabilityStatus:{}});
const input=types.player.toBinary(player);assert.ok(input.length>0);
const p=run(input,'player');const output=types.player.fromBinary(p.done[0].body);assert.equal(output.adPlacements.length,0);assert.equal(output.adSlots.length,0);assert.equal(output.playabilityStatus.pictureInPictureRender,undefined);assert.equal(output.playabilityStatus.backgroundPlayerRender,undefined);assert.equal(p.writes.length,0);
const watch=types.watch.create({contents:[{player}]});const w=run(types.watch.toBinary(watch),'get_watch');assert.equal(types.watch.fromBinary(w.done[0].body).contents[0].player.adSlots.length,0);
const reel=types.reel.create({entries:[{command:{reelWatchEndpoint:{adClientParams:{isAd:true}}}},{command:{reelWatchEndpoint:{adClientParams:{isAd:false}}}}]});const r=run(types.reel.toBinary(reel),'reel/reel_watch_sequence');assert.equal(types.reel.fromBinary(r.done[0].body).entries.length,1);
for(const path of ['browse','next','search'])run(new Uint8Array(),path);
for(const path of ['config','log_event','guide','account/get_setting']){const x=run(new Uint8Array([10,255]),path);assert.equal(Object.keys(x.done[0]).length,0);assert.equal(x.writes.length,0);}
// Malformed/truncated wire input must preserve the original response.
for(const b of [[255],[10,255],[0],[58,128]]){const x=run(new Uint8Array(b),'player');assert.equal(Object.keys(x.done[0]).length,0);}
// A query containing another endpoint must not change endpoint selection.
const q=run(input,'player?next=1');assert.equal(types.player.fromBinary(q.done[0].body).adPlacements.length,0);
assert.equal(stats.network,0);assert.equal(stats.keyAccess,0);
fs.writeFileSync('test-results.json',JSON.stringify({...stats,scope:'Synthetic protobuf fixtures in Node VM; no iOS/device or real account testing'},null,2)+'\n');
console.log(stats);
