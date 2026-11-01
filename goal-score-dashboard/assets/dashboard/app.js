(() => {
  'use strict';
  const el=id=>document.getElementById(id);
  const statusName={observed:'Observed',self_reported:'Self-reported',unassessed:'Unassessed',unavailable:'Source unavailable',stale:'Evidence is stale'};
  const date=value=>value?new Date(value).toLocaleString():null;
  let snapshot=null;
  function render(data){
    if(!data||data.schema_version!==1||!Array.isArray(data.dimensions)||!data.scale)throw Error('Invalid snapshot');
    document.title=data.goal+' · Progress';el('goal').textContent=data.goal;
    const isRange=data.score===null&&data.unknown_policy==='range';
    el('score').classList.toggle('range',isRange);
    el('score').replaceChildren(document.createTextNode(isRange?data.lower+'–'+data.upper:String(data.score??'—')));
    const maximum=document.createElement('small');maximum.textContent='/ '+Number(data.scale.maximum).toLocaleString();el('score').append(maximum);
    el('meaning').textContent=data.score_meaning;
    el('coverage').textContent=data.assessed+' of '+data.dimension_count+' dimensions assessed'+(data.synthetic?' · SYNTHETIC EXAMPLE':'');
    el('dimensions').replaceChildren();
    for(const row of data.dimensions){
      const article=document.createElement('article');article.className='dimension';
      const line=document.createElement('div');line.className='line';
      const label=document.createElement('h2');label.textContent=row.label;
      const weight=document.createElement('span');weight.className='weight';weight.textContent=Math.round(row.weight*100)+'%';label.append(weight);
      const score=document.createElement('strong');score.textContent=row.score??'—';line.append(label,score);
      const track=document.createElement('div');track.className='track';track.setAttribute('aria-hidden','true');
      const fill=document.createElement('div');fill.className='fill';fill.style.width=Math.max(0,Math.min(100,(row.fraction??0)*100))+'%';track.append(fill);
      const note=document.createElement('p');note.textContent=(statusName[row.status]||'Unassessed')+(row.source?' · '+row.source:'')+(row.observed_at?' · '+date(row.observed_at):'');
      article.append(line,track,note);el('dimensions').append(article);
    }
    el('action').textContent=data.next_action||'No next action recorded.';
    el('method').textContent=({withhold:'The overall score stays unassessed until all dimensions have usable evidence.',range:'Missing dimensions produce a possible rubric range. This is not a statistical confidence interval.',evidence_floor:'Unassessed dimensions add no confirmed points. This is a documented-evidence score, not a judgment of ability.'})[data.unknown_policy];
    el('mode').textContent=data.synthetic?'SYNTHETIC EXAMPLE':'READ ONLY · SNAPSHOT';
    el('status').textContent='Snapshot view. Automated collection and chat input are not connected by this template.';
    el('updated').textContent='Calculated: '+date(data.calculated_at)+(data.last_observed_at?' · Latest observation: '+date(data.last_observed_at):'');
  }
  async function refresh(){
    try{const r=await fetch('./state.json',{cache:'no-store'});if(!r.ok)throw Error('Read failed');const data=await r.json();render(data);snapshot=data;}
    catch{el('status').textContent=snapshot?'Could not refresh. Showing the last loaded snapshot.':'Could not load state.json. Serve this directory over HTTP and check the snapshot file.';}
  }
  refresh();document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refresh();});
})();
