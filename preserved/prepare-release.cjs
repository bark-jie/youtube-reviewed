const fs=require('fs'),crypto=require('crypto'),assert=require('assert/strict');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function mature(stagedAt,now){const t=Date.parse(stagedAt);return Number.isFinite(t)&&now-t>=86400000;}
if(process.argv[2]==='--test'){
 const t='2026-09-21T10:00:00Z',start=Date.parse(t);
 assert.equal(mature(t,start+86400000-1),false);
 assert.equal(mature(t,start+86400000),true);
 assert.equal(mature(t,start-1),false);assert.equal(mature('invalid',start),false);
 console.log('24-hour boundary tests passed');process.exit(0);
}
// Supply the actual GitHub candidate commit's committer.date, after fetching
// and verifying that exact commit and candidate hashes. Never use planned time.
if(!mature(process.argv[2],Date.now()))throw Error('Candidate has not been stored in GitHub for 24 hours');
const state=JSON.parse(fs.readFileSync('preserved/state.json','utf8'));
const script=fs.readFileSync('preserved/candidate/youtube.response.js');
const moduleBytes=fs.readFileSync('preserved/candidate/YouTube-Original-Reviewed.sgmodule');
assert.equal(hash(script),state.candidate.scriptSha256);
assert.equal(hash(moduleBytes),state.candidate.moduleSha256);
fs.mkdirSync('scripts',{recursive:true});
fs.writeFileSync('scripts/youtube.original.response.js',script);
fs.writeFileSync('YouTube-Original-Reviewed.sgmodule',moduleBytes);
state.status='released';state.published={...state.candidate,stagedAt:process.argv[2],preparedAt:new Date().toISOString()};
fs.writeFileSync('preserved/state.json',JSON.stringify(state,null,2)+'\n');
console.log('Prepared release; publish script, module, and state in ONE GitHub commit, then verify anonymous raw hashes.');
