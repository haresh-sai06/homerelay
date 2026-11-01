const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');

// Execute the real task-submit listener, with only DOM/dialog/transport fixtures.
function form(transport) {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {value: '', textContent: '', disabled: false,
      handlers: {}, addEventListener(event, handler) { this.handlers[event] = handler; }});
    return elements.get(id);
  };
  let keys = 0;
  const calls = [];
  const context = vm.createContext({document: {getElementById: element, querySelectorAll: () => []},
    crypto: {randomUUID: () => `request-${++keys}`},
    fetch: async (url, options) => {
      const payload = JSON.parse(options.body);
      calls.push(payload);
      return transport(payload, calls.length);
    }});
  const source = readFileSync(join(__dirname, '../homerelay/static/app.js'), 'utf8');
  assert.match(source, /run\(load\);\s*$/);
  vm.runInContext(source.replace(/run\(load\);\s*$/, ''), context);
  vm.runInContext(`board = {members:[{id:'alex',name:'Alex'}],tasks:[],history:[]};
    load = async () => {}; confirm = async () => true;
    run = action => { globalThis.actionPromise = action().catch(error => notice(error.message)); };`, context);
  element('title').value = 'Collect parcel';
  element('owner').value = 'alex';
  element('due').value = '2026-11-05T12:00';
  element('priority').value = '2';
  return {element, calls, cancel: () => vm.runInContext('confirm = async () => false;', context),
    submit() { element('task-form').handlers.submit({preventDefault() {}}); return context.actionPromise; }};
}
const ack = id => ({ok:true, json:async () => ({id})});
const tick = () => new Promise(resolve => setImmediate(resolve));

test('retry after a committed but lost response uses the same key and one stored task', async () => {
  const saved = new Map();
  const f = form((payload, count) => {
    if (!saved.has(payload.request_id)) saved.set(payload.request_id, `task-${saved.size + 1}`);
    if (count === 1) throw new Error('Response lost after commit');
    return ack(saved.get(payload.request_id));
  });
  await f.submit();
  assert.equal(f.element('title').value, 'Collect parcel');
  await f.submit();
  assert.equal(f.calls[0].request_id, f.calls[1].request_id);
  assert.equal(saved.size, 1);
  assert.equal(f.element('title').value, '');
});

test('editing task details after a failed save starts a different request', async () => {
  const f = form((payload, count) => { if (count === 1) throw new Error('offline'); return ack('saved'); });
  await f.submit(); f.element('priority').value = '3'; await f.submit();
  assert.notEqual(f.calls[0].request_id, f.calls[1].request_id);
  assert.equal(f.calls[1].priority, 3);
});

test('unconfirmed successful HTTP response retains the draft and retry key', async () => {
  const f = form((payload, count) => count === 1 ? {ok:true,json:async () => ({})} : ack('saved'));
  await f.submit();
  assert.equal(f.element('title').value, 'Collect parcel');
  assert.match(f.element('notice').textContent, /not confirm/i);
  await f.submit(); assert.equal(f.calls[0].request_id, f.calls[1].request_id);
});

test('a confirmed earlier save preserves newer text entered while saving', async () => {
  let finish;
  const f = form(() => new Promise(resolve => { finish = resolve; }));
  const saving = f.submit(); await tick();
  f.element('title').value = 'Water the plants';
  finish(ack('saved')); await saving;
  assert.equal(f.element('title').value, 'Water the plants');
  assert.match(f.element('notice').textContent, /newer draft/i);
});

test('overlapping submits send only one task request and unlock after completion', async () => {
  let finish;
  const f = form(() => new Promise(resolve => { finish = resolve; }));
  const first = f.submit(); await tick(); const second = f.submit(); await tick();
  assert.equal(f.calls.length, 1);
  assert.equal(f.element('create-task').disabled, true);
  finish(ack('saved')); await Promise.all([first, second]);
  assert.equal(f.element('create-task').disabled, false);
});

test('cancelling confirmation sends nothing and leaves the draft editable', async () => {
  const f = form(() => ack('unused')); f.cancel(); await f.submit();
  assert.equal(f.calls.length, 0);
  assert.equal(f.element('title').value, 'Collect parcel');
  assert.equal(f.element('create-task').disabled, false);
});

test('an intentional new task after a confirmed save receives a fresh key', async () => {
  const f = form(() => ack('saved')); await f.submit();
  f.element('title').value = 'Collect parcel'; await f.submit();
  assert.notEqual(f.calls[0].request_id, f.calls[1].request_id);
});
