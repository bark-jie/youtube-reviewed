const fs=require('fs'),crypto=require('crypto');
const dir='.';fs.mkdirSync(dir+'/scripts',{recursive:true});
let s=fs.readFileSync('maintenance/upstream.response.js','utf8');
const original=crypto.createHash('sha256').update(s).digest('hex');
function replace(a,b){if(s.split(a).length!==2)throw Error('Patch mismatch: '+a.slice(0,60));s=s.replace(a,b);}
replace('function Br(l,e){Ni(l),Si(l),Pi(l,e)}','function Br(l,e){Ni(l)}');
replace(',{path:"guide",msgType:Zr,handler:$i},{path:"get_setting",msgType:Qr,handler:ji}','');
replace(',{path:"config",msgType:kr,handler:ri},{path:"log_event",msgType:kr,handler:ri}','');
replace('Mi.find(r=>l.url.includes(r.path))','Mi.find(r=>l.url.split("?")[0].split("/").pop()===r.path)');
replace('let l={adCache:si(),config:ci()}','let l={adCache:si(),config:{}}');
replace('platformKey:Wr()','platformKey:"youtube"');
replace('e.changed&&(li(e.state.adCache),ui(e.state.config))','e.changed&&li(e.state.adCache)');
replace('advertiseInfo:"YouTubeAdvertiseInfo"','advertiseInfo:"YouTubeReviewedAdvertiseInfo"');
replace('console.log(String(l)),F.exit()','F.exit()');
s='// Modified 2026-09-21: ad-only entry points; no key capture, relay, translation or playback unlock.\n// Source Maasea/sgmodule 65075cdb388fc5e3094afd7e7314c67b243f3525; Apache-2.0.\n'+s;
fs.writeFileSync(dir+'/scripts/youtube.response.js',s);
const moduleText=String.raw`#!name=YouTube Reviewed Private
#!desc=私有仓库审查更新版。首次需填写仓库只读令牌并启用本机证书；播放效果及私库刷新需实机验证。
#!arguments=GitHub只读令牌:PLEASE_SET_READ_ONLY_TOKEN
#!arguments-desc=仅填写 fine-grained PAT：bark-jie/youtube-reviewed 的 Contents Read-only。不要使用有写权限或覆盖其他私库的令牌。不要分享填写后的参数。

[Rule]
AND,((DOMAIN-SUFFIX,googlevideo.com),(PROTOCOL,UDP)),REJECT
AND,((DOMAIN,youtubei.googleapis.com),(PROTOCOL,UDP)),REJECT

[Header Rewrite]
http-request ^https:\/\/raw\.githubusercontent\.com/bark-jie/youtube-reviewed/ header-replace Authorization "token {{{GitHub只读令牌}}}"

[Script]
youtube.reviewed = type=http-response,pattern=^https:\/\/youtubei\.googleapis\.com\/youtubei\/v1\/(browse|next|player|search|reel\/reel_watch_sequence|get_watch)(\?.*)?$,requires-body=1,max-size=4194304,binary-body-mode=1,timeout=10,script-update-interval=86400,script-path=https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/scripts/youtube.response.js

[Map Local]
^https?:\/\/[\w-]+\.googlevideo\.com\/initplayback.+&oad data-type=text data="" status-code=200

[MITM]
hostname = %APPEND% *.googlevideo.com, youtubei.googleapis.com, raw.githubusercontent.com
`;
fs.writeFileSync(dir+'/YouTube-Reviewed-Private.sgmodule',moduleText);

const manifest={version:'1.0.0',date:'2026-09-21',upstreamRepo:'Maasea/sgmodule',upstreamCommit:'65075cdb388fc5e3094afd7e7314c67b243f3525',upstreamResponseBlob:'becad8eaa6094c189ea8db6d644de68ac2d66f61',upstreamResponseSha256:original,publishedResponseSha256:crypto.createHash('sha256').update(s).digest('hex'),status:'reviewed-with-restrictions-device-validation-pending',excluded:['youtube.request.js','third-party init-stream.maasea.workers.dev relay','config/log_event capture','playback unlocking','translation','guide/settings modifications'],deviceValidation:{privateDownload:false,automaticRefresh:false,adBlocking:false}};
fs.writeFileSync(dir+'/review-state.json',JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify(manifest,null,2));
