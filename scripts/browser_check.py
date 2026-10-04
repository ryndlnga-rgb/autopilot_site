"""Optional Playwright browser checks; screenshots are written to /tmp/arcade-*.png."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import sys
layout_only = "--layout-only" in sys.argv
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
 errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('http**/*',lambda route:(requests.append(route.request.url),route.abort()))
 for name in ([] if layout_only else ['index','e1','e2','e3','theatre','lab','field-guide']):
  page.goto((root/f'{name}.html').as_uri());page.wait_for_timeout(150)
  assert page.locator('h1').count()==1,name
  if name in ['e1','lab']:
   page.screenshot(path=f'/tmp/arcade-{name}-start.png',full_page=True)
   # Every initial route must preserve its effects through a forced reroute.
   # Exercise both recovery decisions from the same crash snapshot.
   for initial in range(3):
    page.locator('#tutorial-reset').click()
    page.locator(f'[data-tutorial-route="{initial}"]').click()
    page.locator('#tutorial-next').press('Space')
    assert page.locator('#tutorial-wallet').inner_text()=='0 credits'
    bag=page.locator('#tutorial-bag').inner_text()
    booking=page.locator('#tutorial-world').inner_text()
    page.locator('#tutorial-next').click()
    assert page.locator('#tutorial-crash').is_visible()
    assert page.locator('#tutorial-bag').inner_text()==bag
    assert page.locator('#tutorial-world').inner_text()==booking
    for decision in ['restore','rebuy']:
     if decision=='rebuy':page.locator('#tutorial-retry').click()
     # Deterministic random values cover both possible replacement routes.
     page.evaluate('Math.random = () => '+('0' if decision=='restore' else '0.99'))
     page.locator('#tutorial-next').click()
     assert page.locator('#tutorial-game .delivery-lane.assigned').get_attribute('data-lane')!=str(initial)
     assert page.locator('#tutorial-bag').inner_text()==bag
     assert page.locator('#tutorial-world').inner_text()==booking
     page.locator('#tutorial-next').click()
     assert page.locator('#tutorial-game').get_attribute('data-phase')=='blocked'
     page.locator(f'#tutorial-{decision}').click()
     page.locator('#tutorial-next').click();page.locator('#tutorial-next').click()
     assert page.locator('#tutorial-game').get_attribute('data-phase')=='done'
     assert ('3 OF 3' if decision=='restore' else '1 OF 3') in page.locator('#tutorial-kicker').inner_text()
     assert page.locator('#tutorial-wallet').inner_text()==('0 credits' if decision=='restore' else '-2 credits')
     assert page.locator('#tutorial-world').inner_text()==('All bookings fulfilled' if decision=='restore' else booking)
   page.locator('#tutorial-reset').click()
   # The expert tab preserves tutorial progress and starts an independent run.
   page.locator('#expert-tab').click()
   assert page.locator('#expert-panel').is_visible()
   page.screenshot(path=f'/tmp/arcade-{name}-expert.png',full_page=True)
   def act(action):
    page.locator('#delivery-'+action).click()
    page.wait_for_function("!document.getElementById('delivery-game').hasAttribute('aria-busy')")
   def expert_start(initial,random_value=0):
    act('reset')
    page.evaluate('Math.random = () => '+str(random_value))
    page.locator(f'[data-delivery-route="{initial}"]').click()
    page.wait_for_function("!document.getElementById('delivery-game').hasAttribute('aria-busy')")
    for _ in range(3):act('next')
    assert page.locator('#delivery-crash').is_visible()
    effects=page.locator('#delivery-world').inner_text()
    pos=page.locator('#delivery-token').get_attribute('style')
    act('next')
    assert page.locator('#delivery-token').get_attribute('style')==pos,'reboot teleported Pip'
    assert page.locator('#delivery-world').inner_text()==effects
    act('next')
    assert page.locator('#delivery-game').get_attribute('data-phase')=='gate'
    assert page.locator('#delivery-battery').inner_text()=='5 / 7'
   # Original ferry: backtrack, re-use booking, preserve money and release crossing.
   expert_start(0)
   page.screenshot(path=f'/tmp/arcade-{name}-expert-wrong-turn.png',full_page=True)
   act('back');act('original');act('cross');act('deliver')
   assert 'ALL PROMISES KEPT' in page.locator('#delivery-kicker').inner_text()
   assert page.locator('#delivery-battery').inner_text()=='2 / 7'
   # Lift to ferry: refund the lift, redirect Mara, release power, finish cleanly.
   expert_start(1)
   act('buy');assert page.locator('#delivery-wallet').inner_text()=='-1 credits'
   act('cancel');act('notify');act('cross');act('deliver')
   assert 'ALL PROMISES KEPT' in page.locator('#delivery-kicker').inner_text()
   assert 'changed routes' in page.locator('#delivery-message').inner_text()
   assert page.locator('#delivery-wallet').inner_text()=='0 credits'
   # Canal return cannot cross after the detour without using the charger.
   expert_start(2)
   act('back');act('original');assert page.locator('#delivery-cross').is_disabled()
   act('back');act('charge');act('charge');act('original');act('cross');act('deliver')
   assert 'ALL PROMISES KEPT' in page.locator('#delivery-kicker').inner_text()
   # Ignoring the original slot and pickup message leaves concrete effects.
   expert_start(0)
   act('buy');act('cross');act('deliver')
   assert 'UNFINISHED BUSINESS' in page.locator('#delivery-kicker').inner_text()
   assert 'Ferry held at dock' in page.locator('#delivery-message').inner_text()
   assert 'Mara is still waiting' in page.locator('#delivery-message').inner_text()
   # Replay restores the complete crash snapshot, not just the avatar.
   act('retry');assert page.locator('#delivery-battery').inner_text()=='6 / 7'
   assert page.locator('#delivery-wallet').inner_text()=='0 credits'
   assert 'river dock' in page.locator('#delivery-world').inner_text()
   page.locator('#tutorial-tab').click()
   assert page.locator('#tutorial-game').get_attribute('data-phase')=='choose'
   page.locator('#tutorial-tab').press('ArrowRight')
   assert page.locator('#expert-tab').get_attribute('aria-selected')=='true'
   assert page.locator('#delivery-game').get_attribute('data-phase')=='crashed'
   page.locator('#tutorial-tab').click()
  if name=='e1':page.locator('#evidence > summary').click()
  if page.locator('[data-explorer]').count():
   assert page.locator('.graph-stage svg .route-lane').count()>0,name
   page.locator('[data-action="start"]').click();page.get_by_role('button',name='Step →',exact=True).click();assert 'Call 1 /' in page.locator('.step-readout').inner_text()
   page.locator('[data-action="play"]').click();page.wait_for_timeout(850);page.locator('[data-action="play"]').click()
   page.locator('[data-route]').first.click();assert page.locator('[data-route]').first.get_attribute('aria-pressed')=='true'
   page.locator('[data-action="all"]').click()
   page.locator('[data-action="expand"]').click();assert page.locator('.explorer.expanded').count()==1
   page.locator('[data-action="expand"]').click()
   if name in ['e2','e3']:
    page.locator('[data-action="crash"]').click();assert page.locator('.crash-marker').count()>0
   page.locator('[data-select="metric"]').select_option('coverage')
   page.locator('[data-matrix-drawer] summary').click();page.locator('[data-cell]').last.click()
   if name in ['index','theatre']:
    for exp in ['e2','e3','e1']:page.locator(f'[data-exp="{exp}"]').click();assert page.locator('.graph-stage svg').count()==1
   if name in ['e2','e3']:
    for v in ['autopilot','react-agent-state','react-external-state','durable-execution','plan-and-execute']:
     page.locator('[data-select="variant"]').select_option(v)
     assert page.locator('.metric .value').count()==6
   page.locator('[data-matrix-drawer] summary').click()
  page.screenshot(path=f'/tmp/arcade-{name}.png',full_page=True)
  print(name,'ok',flush=True)
 page.set_viewport_size({'width':390,'height':844})
 for name in ([] if layout_only else ['index','e1','e2','e3','theatre','lab','field-guide']):
  page.goto((root/f'{name}.html').as_uri());page.wait_for_timeout(100)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'mobile overflow {name}'
  page.screenshot(path=f'/tmp/arcade-{name}-mobile.png',full_page=True)
  if name in ['e1','lab']:
   page.locator('[data-tutorial-route="0"]').click()
   for _ in range(4):page.locator('#tutorial-next').click()
   assert page.locator('#tutorial-game').get_attribute('data-phase')=='blocked'
   assert page.locator('#tutorial-restore').is_visible()
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'mobile game overflow {name}'
   page.locator('#expert-tab').click()
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'mobile expert overflow {name}'
   page.screenshot(path=f'/tmp/arcade-{name}-expert-mobile.png',full_page=True)
 # Keep the complete Expert cabinet visible at common laptop sizes.
 page.emulate_media(reduced_motion='reduce')
 for width,height in [(1366,768),(1280,720)]:
  page.set_viewport_size({'width':width,'height':height})
  page.goto((root/'e1.html').as_uri())
  tutorial_height=page.locator('#tutorial-game').bounding_box()['height']
  page.locator('#expert-tab').click()
  def check_cabinet():
   box=page.locator('#delivery-game').bounding_box()
   assert box['height'] <= height-16,(width,height,box['height'])
   assert box['height'] <= tutorial_height+16,('expert exceeds tutorial',box['height'],tutorial_height)
   screen=page.locator('#delivery-game .delivery-screen').bounding_box()
   console=page.locator('#delivery-game .delivery-console').bounding_box()
   assert console['y'] >= screen['y']+screen['height'],'expert controls are above the map'
   page.locator('#delivery-game').evaluate("e => e.scrollIntoView({block:'start'})")
   hud=page.locator('#delivery-game .delivery-hud').bounding_box()
   controls=page.locator('#delivery-game .delivery-console').bounding_box()
   assert hud['y'] >= 0 and controls['y']+controls['height'] <= height
  check_cabinet()
  page.locator('[data-delivery-route="0"]').click()
  for _ in range(5):page.locator('#delivery-next').click()
  check_cabinet()
  page.locator('#delivery-buy').click()
  check_cabinet()
  page.screenshot(path=f'/tmp/arcade-expert-fit-{width}.png')
 print(json.dumps({'errors':errors,'external_requests':requests}))
 assert not errors
 assert not requests
 browser.close()
