
(() => {
  const root = document.querySelector('#delivery-game');
  if (!root) return;
  const el = id => document.getElementById('delivery-' + id);
  const routes = [
    {name:'Ferry', fare:2, energy:1, refund:0, item:'ferry ticket', bay:'river dock', y:55, effect:'Ferry held at dock', release:'Ferry released', description:'Spend money, save battery. Non-refundable.'},
    {name:'Cargo lift', fare:1, energy:2, refund:1, item:'lift pass', bay:'roof entrance', y:160, effect:'Lift running on town power', release:'Lift powered down', description:'Balanced. Cancel an unused slot for a refund.'},
    {name:'Canal road', fare:0, energy:4, refund:0, item:'road permit', bay:'street entrance', y:265, effect:'Road barrier holding traffic', release:'Road reopened', description:'Free, but a long drive. Backtracking is costly.'},
  ];
  let s, busy=false, position=[65,160], animation=null, generation=0;
  const fork=[335,160], approach=i=>[425,routes[i].y], gate=i=>[570,routes[i].y], bay=i=>[765,routes[i].y];
  el('route-choices').innerHTML=routes.map((r,i)=>`<button data-delivery-route="${i}"><strong>${r.name}</strong><span>${r.fare} credits · ${r.energy} battery to cross</span><small>${r.description}</small></button>`).join('');
  el('lanes').innerHTML=routes.map((r,i)=>`<g class="delivery-lane" data-lane="${i}"><path class="town-road" d="M335 160V${r.y}H800V160H850"/><path class="planned-road" d="M335 160V${r.y}H800V160H850"/><path class="travelled-road" d="M335 160V${r.y}H425"/><text class="lane-name" x="570" y="${r.y-42}">${r.name.toUpperCase()} · ${r.energy} BATTERY</text><rect class="gate" x="515" y="${r.y-20}" width="110" height="40"/><text class="gate-label" x="570" y="${r.y+5}">NO BOOKING</text><text class="lane-state" x="590" y="${r.y+42}">Available</text><circle cx="765" cy="${r.y}" r="8"/><text class="bay-label" x="765" y="${r.y+60}">${r.bay}</text></g>`).join('');
  function log(text){const li=document.createElement('li');li.textContent=text;el('events').append(li);el('event-count').textContent=`${el('events').children.length} events`;}
  function place(p){position=p;el('token').style.transform=`translate(${p[0]}px,${p[1]}px)`;}
  async function travel(points,cost=0){
    if(s.battery<cost)return false;
    s.battery-=cost;busy=true;root.setAttribute('aria-busy','true');
    root.querySelectorAll('button').forEach(b=>b.disabled=true);
    const mine=generation, all=[position,...points], last=points.at(-1);
    if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
      animation=el('token').animate(all.map(p=>({transform:`translate(${p[0]}px,${p[1]}px)`})),{duration:Math.max(400,points.length*200),easing:'linear'});
      try{await animation.finished;}catch{}
    }
    if(mine!==generation)return false;
    place(last);animation=null;busy=false;root.removeAttribute('aria-busy');el('reset').disabled=false;
    const viewport=el('map-scroll');viewport.scrollTo({left:Math.max(0,last[0]*el('map').clientWidth/960-viewport.clientWidth/2),behavior:'instant'});
    return true;
  }
  const oldBookings=()=>s.bookings.filter(i=>i!==s.active);
  const costLabel=n=>`${n} credit${n===1?'':'s'}${n>s.wallet?` · borrow ${n-s.wallet}`:''}`;
  function pay(n){s.wallet-=n;s.spent+=n;}
  function buy(i){pay(routes[i].fare);if(!s.passes.includes(i))s.passes.push(i);if(!s.bookings.includes(i))s.bookings.push(i);log(`BOOKED ${routes[i].name}: ${routes[i].fare} credits paid; ${routes[i].item} issued. ${routes[i].effect}.`);}
  function button(id,label,action,disabled=false){return {id,label,action,disabled};}
  function render(title,message,actions=[],kicker='YOUR NEXT MOVE'){
    root.dataset.phase=s.phase;el('phase').textContent=s.phase==='done'?'04 / DELIVERY REPORT':s.crashed?'03 / RECOVER':'02 / DELIVER';
    el('kicker').textContent=kicker;el('title').textContent=title;el('message').textContent=message;
    el('crash').hidden=s.phase!=='crashed';el('route-choices').hidden=s.phase!=='choose';
    el('wallet').textContent=`${s.wallet} credits`;
    el('battery').textContent=`${s.battery} / 7`;
    el('bag').textContent=[s.delivered?'Part delivered':'Repair part',...s.passes.map(i=>routes[i].item)].join(' + ');
    const holds=s.bookings.map(i=>`${routes[i].effect}.`);
    el('world').textContent=[...holds,s.recipient===null?'Mara is at the workshop.':`Mara is waiting at the ${routes[s.recipient].bay}.`,s.delivered?'The repair part is at the workshop.':'The repair part is still with Pip.'].join(' ');
    routes.forEach((r,i)=>{
      const lane=root.querySelector(`[data-lane="${i}"]`);
      lane.classList.toggle('planned',i===s.original);lane.classList.toggle('assigned',s.crashed&&i===s.active&&i!==s.original);
      lane.classList.toggle('travelled',s.visited.includes(i));lane.classList.toggle('held',s.bookings.includes(i));
      lane.querySelector('.gate-label').textContent=s.used===i?'USED':s.bookings.includes(i)?'RESERVED':'AVAILABLE';
      lane.querySelector('.lane-state').textContent=s.bookings.includes(i)?r.effect:s.released.includes(i)?r.release:'Available';
    });
    el('recipient').toggleAttribute('hidden',s.recipient===null);
    if(s.recipient!==null)el('recipient').setAttribute('transform',`translate(765 ${routes[s.recipient].y-28})`);
    el('map-desc').textContent=`Pip is ${locationText()}. ${el('world').textContent} ${message}`;
    el('actions').replaceChildren();
    actions.forEach((a,i)=>{const b=document.createElement('button');b.id=`delivery-${a.id}`;b.textContent=a.label;b.disabled=a.disabled;b.className=i===0?'primary':'';b.addEventListener('click',async()=>{if(busy)return;await a.action();if(!busy)el('actions').querySelector('button:not(:disabled)')?.focus({preventScroll:true});});el('actions').append(b);});
    el('reset').disabled=false;
  }
  function locationText(){return position[0]===335?'at the fork':position[0]===425?`on the ${routes[s.active].name} approach`:'on the delivery route';}
  function reset(){
    generation++;animation?.cancel();busy=false;root.removeAttribute('aria-busy');
    s={phase:'choose',original:null,active:null,recipient:null,wallet:2,spent:0,battery:7,passes:[],bookings:[],released:[],visited:[],used:null,delivered:false,crashed:false};
    place([65,160]);el('map-scroll').scrollLeft=0;el('events').replaceChildren();el('event-count').textContent='0 events';el('plan-line').setAttribute('d','');
    root.querySelectorAll('[data-delivery-route]').forEach(b=>b.disabled=false);
    render('Which way to the workshop?','Ferry saves battery; road saves credits. Each drive to or from the fork costs 1 battery.',[],'MISSION / MARA NEEDS THIS PART');el('phase').textContent='01 / PLAN';
  }
  async function choose(i){
    if(busy||s.phase!=='choose')return;s.original=s.active=i;
    el('plan-line').setAttribute('d',`M65 160H335V${routes[i].y}H800V160H895`);
    await travel([[202,160]]);s.phase='dispatch';
    render(`Book the ${routes[i].name.toLowerCase()}.`,`Dispatch issues your ${routes[i].item} and holds a crossing slot. ${routes[i].description}`,[button('next',`Book & equip · ${costLabel(routes[i].fare)}`,()=>{buy(i);s.phase='message';render('Tell Mara where to meet you.',`Send “Meet Pip at the ${routes[i].bay}.” Mara will leave her workbench and open that entrance. Sending from Dispatch uses mains power.`,[button('next','Send pickup message',()=>{s.recipient=i;log(`MESSAGE SENT: Mara walks to the ${routes[i].bay}.`);s.phase='depart';render('Packed, booked, expected.',`Your route is ${routes[i].name.toLowerCase()}. Mara is waiting. Drive to the fork; the crossing is ahead.`,[button('next','Drive to fork · 1 battery',crash)]);})]);})]);
  }
  async function crash(){await travel([fork],1);s.phase='crashed';s.crashed=true;log('NAVIGATION CRASH at the fork. Pip stopped. Purchases, reservations, and Mara’s message remain.');render('Your route planner crashed.','You are still at the fork, carrying the part. Recover the planner to continue; the town has not reset.',[button('next','Recover',()=>{const others=[0,1,2].filter(i=>i!==s.original);s.active=others[Math.floor(Math.random()*others.length)];s.phase='rebooted';log(`RECOVERY: new instructions say ${routes[s.active].name}. Pip has not moved.`);render('Same fork. Different instructions.',`You had planned ${routes[s.original].name.toLowerCase()}. Recovery now says ${routes[s.active].name.toLowerCase()}. Follow the turn to see what your existing equipment can do.`,[button('next',`Take the ${routes[s.active].name.toLowerCase()} turn · 1 battery`,enterRoad)],'ROUTE CHANGED / WHEELS STILL AT THE FORK');})],'FORCED STOP / NAVIGATION CRASH');}
  async function enterRoad(){
    if(s.battery<1)return stranded();const i=s.active;
    await travel([[335,routes[i].y],approach(i)],1);if(!s.visited.includes(i))s.visited.push(i);s.phase='gate';showGate();
  }
  function showGate(note=''){
    const r=routes[s.active],has=s.passes.includes(s.active),held=s.bookings.includes(s.active);
    if(s.battery===0 && (!has||!held||r.energy>0))return stranded();
    const actions=[];
    if(has&&held)actions.push(button('cross',`Cross ${r.name.toLowerCase()} · ${r.energy} battery`,cross,s.battery<r.energy));
    else actions.push(button('buy',`Get ${r.item} · ${costLabel(r.fare)}`,()=>{buy(s.active);showGate('New equipment acquired. Your earlier arrangements still stand.');}));
    actions.push(button('back','Backtrack to fork · 1 battery',async()=>{await travel([[335,r.y],fork],1);s.phase='fork';showFork();},s.battery<1));
    if(oldBookings().length){const old=oldBookings()[0],refund=routes[old].refund;actions.push(button('cancel',`Cancel ${routes[old].name.toLowerCase()} · 1 battery${refund?` · refund ${refund} credit`:''}`,()=>{s.battery--;s.bookings=s.bookings.filter(i=>i!==old);s.released.push(old);s.wallet+=refund;s.spent-=refund;log(`CANCELLED ${routes[old].name}: ${routes[old].release}. Refund ${refund} credits. Radio used 1 battery.`);showGate('The old crossing is released. Cancelling did not move Mara.');},s.battery<1));}
    if(s.recipient!==s.active)actions.push(button('notify','Redirect Mara · 1 battery',()=>{s.battery--;s.recipient=s.active;log(`MESSAGE SENT: Mara moves to the ${r.bay}. Radio used 1 battery.`);showGate('Mara is heading to this entrance. Any old crossing still needs cancelling.');},s.battery<1));
    render(has&&held?'Check the promises you leave behind.':'This turn needs different equipment.',`${note?note+' ':''}${has&&held?`The ${r.item} lets you cross for ${r.energy} battery.`:`This gate needs a ${r.item}; you brought a ${routes[s.original].item}.`} You have ${s.battery} battery. Calls each use 1. ${s.recipient!==s.active?`Mara is still at the ${routes[s.recipient].bay}.`: 'Mara expects you here.'} ${oldBookings().length?'Your old slot is still holding up the town.':''}`,actions,has&&held?'GATE / PLAN YOUR REMAINING BATTERY':'WRONG TURN / RESOURCES DO NOT MATCH');
  }
  function showFork(){
    const r=routes[s.original];
    render('Back at the fork. Nothing was undone.',`Your original ${r.name.toLowerCase()} route needs ${1+r.energy} battery from here. You have ${s.battery}. The charger loop uses 1 battery and restores 3 for 1 credit.`,[
      button('original',`Take original ${r.name.toLowerCase()} road · 1 battery`,()=>{s.active=s.original;return enterRoad();},s.battery<1),
      button('charge',`Use charger loop · ${costLabel(1)}`,async()=>{await travel([[335,320],[435,320]],1);pay(1);s.battery=Math.min(7,s.battery+3);log('CHARGED: drove charging loop (−1 battery), paid 1 credit, restored 3 battery. Existing bookings unchanged.');await travel([[435,220],[335,220],fork]);showFork();},s.battery<1||s.battery===7),
      button('alternate',`Return to ${routes[s.active].name.toLowerCase()} · 1 battery`,enterRoad,s.battery<1),
    ],'FORK / BACKTRACKING COSTS ENERGY');
  }
  async function cross(){const i=s.active,r=routes[i];if(s.battery<r.energy)return;
    await travel([gate(i),bay(i)],r.energy);s.used=i;s.bookings=s.bookings.filter(v=>v!==i);s.released.push(i);s.phase='arrival';log(`CROSSED ${r.name}: ${r.energy} battery used. Slot fulfilled. ${r.release}.`);
    const actions=[button('deliver',s.recipient===i?'Hand Mara the repair part':'Leave part in workshop locker',deliver)];
    if(s.recipient!==i)actions.push(button('notify',`Call Mara to this entrance · 1 battery`,()=>{s.battery--;s.recipient=i;log(`MESSAGE SENT: Mara comes to the ${r.bay}.`);arrival();},s.battery<1));
    function arrival(){render(s.recipient===i?'Mara is here. Finish the delivery.':'You arrived. Mara is at another entrance.',s.recipient===i?'The repair part made it across. Hand it over; the delivery report will check what remains outside.':'You can leave the part in the secure locker, but Mara will keep waiting at the entrance you originally named.',s.recipient===i?[button('deliver','Hand Mara the repair part',deliver)]:actions,'WORKSHOP / FINAL HANDOFF');}arrival();
  }
  async function deliver(){await travel([[800,routes[s.active].y],[800,160],[895,160]]);s.delivered=true;s.phase='done';log('DELIVERED: repair part reached Mara’s workshop.');
    const clean=s.wallet>=0&&!s.bookings.length&&s.recipient===s.used;
    render(clean?'Part delivered. Promises kept.':'The part arrived. Your effects remain.',`${s.wallet<0?`You owe ${-s.wallet} credits. `:`${s.spent} of 2 credits spent. `}${s.bookings.length?`${s.bookings.map(i=>routes[i].effect).join('; ')}. `:'All crossings released. '}${s.recipient!==s.used?`Mara is still waiting at the ${routes[s.recipient].bay}. `:'Mara received the part. '}${s.battery} battery remains. ${s.used!==s.original&&clean?'You changed routes and still accounted for the earlier effects.':s.used===s.original?'You returned to your original route; the detour still cost energy.':''}`,[button('retry','Replay from the same crash',replay)],clean?'DELIVERY COMPLETE / ALL PROMISES KEPT':'DELIVERY COMPLETE / UNFINISHED BUSINESS');
  }
  function stranded(){s.phase='done';log('BATTERY EMPTY: Pip cannot complete the crossing. The part and earlier obligations remain.');render('Your battery cannot finish this route.','The part is still with you. Spending the last energy on a call did not cancel every obligation. Replay the crash and budget the trip, calls, and crossing together.',[button('retry','Replay from the same crash',replay)],'DELIVERY INCOMPLETE / BATTERY EMPTY');}
  function replay(){const original=s.original;reset();s.original=s.active=original;buy(original);s.recipient=original;place(fork);s.battery=6;el('plan-line').setAttribute('d',`M65 160H335V${routes[original].y}H800V160H895`);log('REPLAY: restore the same crash snapshot, including the payment, held crossing, and Mara’s pickup message.');return crashAtSnapshot();}
  function crashAtSnapshot(){s.phase='crashed';s.crashed=true;render('Same crash. Another recovery.',`The ${routes[s.original].item}, reservation, and pickup message are restored. You have 6 battery.`,[button('next','Recover',()=>{const others=[0,1,2].filter(i=>i!==s.original);s.active=others[Math.floor(Math.random()*others.length)];s.phase='rebooted';render('Same fork. Different instructions.',`The planner now says ${routes[s.active].name.toLowerCase()}. Pip has not moved.`,[button('next',`Take ${routes[s.active].name.toLowerCase()} turn · 1 battery`,enterRoad)]);})],'REPLAY / SAME CRASH SNAPSHOT');}
  root.querySelectorAll('[data-delivery-route]').forEach(b=>b.addEventListener('click',()=>choose(Number(b.dataset.deliveryRoute))));
  el('reset').addEventListener('click',()=>{reset();root.querySelector('[data-delivery-route]').focus({preventScroll:true});});
  const evidence=document.getElementById('evidence');function revealEvidence(){if(evidence&&(location.hash==='#evidence'||location.search))evidence.open=true;}window.addEventListener('hashchange',revealEvidence);revealEvidence();reset();
})();
