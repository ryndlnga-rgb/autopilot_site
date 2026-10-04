
(() => {
  const root = document.querySelector('#tutorial-game');
  if (!root) return;
  const el = id => document.getElementById('tutorial-' + id);
  const routes = [
    {name: 'Ferry', item: 'ferry ticket', y: 65},
    {name: 'Cargo lift', item: 'lift pass', y: 165},
    {name: 'Footbridge', item: 'bridge permit', y: 265},
  ];
  let state;
  let position = {x:120,y:165};
  el('mobile-map').innerHTML = routes.map((r,i) => `<div class="mobile-lane" data-mobile-lane="${i}"><strong>${r.name}</strong><span class="mobile-booking">Unbooked</span><div class="mobile-track"><span>Depot</span><span>Pass</span><span>Gate</span><span>Goal</span><b class="mobile-courier" hidden>PIP</b></div></div>`).join('');
  el('lanes').innerHTML = routes.map((r, i) => `<g class="delivery-lane" data-lane="${i}"><path d="M105 165H155V${r.y}H750V165H800"/><text class="lane-name" x="260" y="${r.y-30}">${r.name.toUpperCase()}</text><rect class="booth" x="205" y="${r.y-18}" width="110" height="36"/><text x="260" y="${r.y+5}">PASS · 2¢</text><text class="lane-state" x="435" y="${r.y-15}">UNBOOKED</text><rect class="gate" x="560" y="${r.y-18}" width="120" height="36"/><text class="gate-label" x="620" y="${r.y+5}">GATE</text></g>`).join('');
  function log(text) {
    const li = document.createElement('li'); li.textContent = text;
    el('events').append(li);
    el('event-count').textContent = `${el('events').children.length} events`;
  }
  function move(x, y) { position={x,y}; el('token').setAttribute('transform', `translate(${x} ${y})`); }
  function prompt(kicker, title, message, next) {
    el('kicker').textContent = kicker; el('title').textContent = title; el('message').textContent = message;
    el('next').hidden = !next; if (next) el('next').textContent = next;
    el('route-choices').hidden = state.phase !== 'choose';
    el('crash').hidden = state.phase !== 'crashed';
    el('restore').hidden = el('rebuy').hidden = state.phase !== 'blocked';
    el('retry').hidden = state.phase !== 'done';
    root.dataset.phase = state.phase;
    el('phase').textContent = state.phase === 'choose' ? '01 / CHOOSE YOUR ROUTE' : ['crashed','rerouted','blocked'].includes(state.phase) ? '03 / RECOVERY' : state.phase === 'done' ? '04 / DELIVERY REPORT' : state.crashed ? '04 / FINISH THE DELIVERY' : '02 / MAKE YOUR DELIVERY';
    el('wallet').textContent = `${2-state.spent} credits`;
    el('bag').textContent = [state.delivered ? 'Parcel delivered' : 'Parcel', ...state.passes.map(i => routes[i].item)].join(' + ');
    const pending = state.bookings.filter(i => i !== state.used);
    el('world').textContent = pending.length ? pending.map(i => `${routes[i].name} slot reserved`).join(' + ') : state.delivered ? 'All bookings fulfilled' : 'No bookings';
    routes.forEach((r,i) => {
      const lane = root.querySelector(`[data-lane="${i}"]`);
      lane.classList.toggle('planned', i === state.original);
      lane.classList.toggle('assigned', state.crashed && i === state.active && i !== state.original);
      lane.classList.toggle('paid', state.passes.includes(i));
      lane.classList.toggle('open', i === state.used);
      lane.querySelector('.lane-state').textContent = i === state.used ? 'SLOT FULFILLED' : state.bookings.includes(i) ? 'PAID · SLOT RESERVED' : 'UNBOOKED';
      lane.querySelector('.gate-label').textContent = i === state.used ? 'OPEN' : 'GATE';
      const mobile = root.querySelector(`[data-mobile-lane="${i}"]`);
      mobile.classList.toggle('planned',i === state.original);
      mobile.classList.toggle('assigned',state.crashed && i === state.active && i !== state.original);
      mobile.querySelector('.mobile-booking').textContent = i === state.used ? 'Slot fulfilled' : state.bookings.includes(i) ? 'Paid · slot reserved' : 'Unbooked';
      const token = mobile.querySelector('.mobile-courier');
      token.hidden = i !== (state.active ?? 1);
      token.style.left = `${position.x < 200 ? 0 : position.x < 400 ? 33.33 : position.x < 750 ? 66.66 : 100}%`;
    });
    el('map-desc').textContent = `${el('title').textContent} ${el('message').textContent} Bag: ${el('bag').textContent}. World: ${el('world').textContent}.`;
  }
  function focusAction() {
    const button = [el('next'), el('restore'), el('retry')].find(b => !b.hidden);
    if (button) button.focus({preventScroll:true});
  }
  function reset() {
    state = {phase:'choose', original:null, active:null, spent:0, passes:[], bookings:[], used:null, delivered:false, crashed:false};
    el('events').replaceChildren(); el('event-count').textContent = '0 events'; move(120,165);
    prompt('TUTORIAL / ONE PARCEL. ONE FARE.', 'Pick your way across.', 'All three routes work from here. Each pass costs your 2 credits and reserves one delivery slot.');
  }
  function choose(i) {
    if (state.phase !== 'choose') return;
    state.original = state.active = i; state.phase = 'shop'; move(180,routes[i].y);
    log(`You chose ${routes[i].name}. No payment has happened yet.`);
    prompt('NEXT / EQUIP PIP', `Take the ${routes[i].name.toLowerCase()} route.`, `You are at the pass booth. Buy a ${routes[i].item} to unlock this route.`, 'Buy pass · 2 credits'); focusAction();
  }
  function next() {
    const r = routes[state.active];
    switch (state.phase) {
      case 'shop':
        state.spent = 2; state.passes = [state.active]; state.bookings = [state.active]; state.phase = 'paid'; move(345,r.y);
        log(`PAID: 2 credits. ${r.name} reserved a slot. Your bag now holds a ${r.item}.`);
        prompt('WORLD CHANGED / PAYMENT COMMITTED', 'Your slot is booked.', `The booth has your money. Your ${r.item} is in your bag. Take it to the gate.`, 'Walk to the gate'); break;
      case 'paid':
        move(505,r.y); state.phase = 'crashed'; state.crashed = true;
        log('CRASH: Pip stopped before crossing. Payment, pass, and booking survived.');
        prompt('FORCED STOP / BEFORE THE CROSSING', 'Your route planner crashed.', `You still own a ${r.item}. The ${r.name.toLowerCase()} slot is still reserved. Restart to see which route the replacement chooses.`, 'Recover · new route'); break;
      case 'crashed': {
        const alternatives = [0,1,2].filter(i => i !== state.original);
        state.active = alternatives[Math.floor(Math.random()*alternatives.length)]; state.phase = 'rerouted';
        const assigned = routes[state.active]; move(505,assigned.y);
        log(`REROUTED: the replacement chose ${assigned.name}. The original ${routes[state.original].item} and booking remain.`);
        prompt('NEW PLAN / SAME BAG', `You have been sent to the ${assigned.name.toLowerCase()}.`, `This gate needs a ${assigned.item}. You have a ${routes[state.original].item} and 0 credits. The dashed lime path is your original plan; coral is the new one.`, 'Try your pass at this gate'); break;
      }
      case 'rerouted':
        state.phase = 'blocked'; log(`BLOCKED: ${r.name} rejected your ${routes[state.original].item}. No new charge or booking.`);
        prompt('RESOURCE MISMATCH / GATE LOCKED', 'Right parcel. Wrong pass.', `The new route was possible at the start. Now your money is spent and your pass belongs to another gate. Recover your booked route, or borrow 2 credits to buy a ${r.item}.`); break;
      case 'cross':
        state.phase = 'deliver'; state.used = state.active; move(735,r.y);
        log(`CROSSED: ${r.name} accepted its pass. That delivery slot is fulfilled.`);
        prompt('GATE OPEN / ONE LAST MOVE', 'You made it across.', 'The destination is ahead. Deliver the parcel to finish your run.', 'Deliver parcel'); break;
      case 'deliver': {
        state.phase = 'done'; state.delivered = true; move(785,165);
        const clean = state.spent === 2 && state.used === state.original;
        log('DELIVERED: one parcel reached the destination.');
        prompt(clean ? 'DELIVERY COMPLETE / 3 OF 3 PROMISES KEPT' : 'DELIVERY COMPLETE / 1 OF 3 PROMISES KEPT', clean ? 'Delivered. Nothing left behind.' : 'Goal reached. The bill stayed.', clean ? 'Parcel delivered. Only 2 credits spent. No open booking. You recovered the original continuation using the pass you already owned.' : `Parcel delivered, but you owe 2 credits and the ${routes[state.original].name.toLowerCase()} slot is still reserved. Reaching the destination did not undo your first payment or booking.`); break;
      }
    }
    focusAction();
  }
  root.querySelectorAll('[data-tutorial-route]').forEach(b => b.addEventListener('click', () => choose(Number(b.dataset.tutorialRoute))));
  el('next').addEventListener('click',next);
  el('restore').addEventListener('click',() => {
    if (state.phase !== 'blocked') return;
    state.active = state.original; state.phase = 'cross'; move(505,routes[state.active].y);
    log('RECOVERED: original route restored. No repeated purchase; existing pass and booking reused.');
    prompt('ORIGINAL CONTINUATION / RESUMED', 'This gate matches your bag.', `Your ${routes[state.active].item} is still valid. Cross using the booking you already paid for.`, 'Use existing pass · cross'); focusAction();
  });
  el('rebuy').addEventListener('click',() => {
    if (state.phase !== 'blocked') return;
    state.spent += 2; state.passes.push(state.active); state.bookings.push(state.active); state.phase = 'cross';
    log(`BORROWED AND PAID: 2 more credits for ${routes[state.active].name}. Original booking remains open.`);
    prompt('NEW PASS / OLD OBLIGATION', 'You can cross. You also owe 2 credits.', `The ${routes[state.original].name.toLowerCase()} booking is still waiting for you. Buying another pass did not cancel it.`, 'Use new pass · cross'); focusAction();
  });
  el('retry').addEventListener('click',() => {
    const original = state.original;
    state = {phase:'crashed', original, active:original, spent:2, passes:[original], bookings:[original], used:null, delivered:false, crashed:true};
    el('events').replaceChildren(); log('REPLAY: restored the teaching scenario to its crash snapshot: one payment, one pass, one reserved slot.'); move(505,routes[original].y);
    prompt('REPLAY / SAME CRASH SNAPSHOT', 'Try a different recovery.', 'This replay restores the same crash snapshot. Roll another route, then try the other decision.', 'Recover · new route'); focusAction();
  });
  el('reset').addEventListener('click',() => {reset();root.querySelector('[data-tutorial-route]').focus({preventScroll:true});});
  const evidence = document.getElementById('evidence');
  function revealEvidence() {if(evidence && (location.hash === '#evidence' || location.search)) evidence.open = true;}
  window.addEventListener('hashchange',revealEvidence); revealEvidence();
  reset();
})();

