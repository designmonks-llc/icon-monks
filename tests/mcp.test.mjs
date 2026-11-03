// Drives the MCP server in @icon-monks/core over stdio the way an MCP client does.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

function session() {
  const p = spawn(process.execPath, [fileURLToPath(new URL('../packages/core/dist/mcp.js', import.meta.url))]);
  let buf = '';
  const waiting = new Map();
  p.stdout.on('data', (d) => {
    buf += d;
    let k;
    while ((k = buf.indexOf('\n')) >= 0) { const m = JSON.parse(buf.slice(0, k)); buf = buf.slice(k + 1); waiting.get(m.id)?.(m); }
  });
  let id = 0;
  const rpc = (method, params) => new Promise((res) => { id += 1; waiting.set(id, res); p.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n'); });
  return { rpc, notify: (method) => p.stdin.write(JSON.stringify({ jsonrpc: '2.0', method }) + '\n'), close: () => p.kill() };
}

test('MCP server lists tools and answers calls', async () => {
  const s = session();
  try {
    const init = await s.rpc('initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'test', version: '1' } });
    assert.equal(init.result.serverInfo.name, 'icon-monks');
    assert.ok(init.result.capabilities.tools);
    s.notify('notifications/initialized');
    const tools = (await s.rpc('tools/list', {})).result.tools.map((t) => t.name);
    assert.deepEqual(tools, ['search_icons', 'get_icon_svg', 'get_icon_code', 'list_categories']);
    const found = (await s.rpc('tools/call', { name: 'search_icons', arguments: { query: 'house', limit: 3 } })).result.content[0].text;
    assert.match(found.split('\n')[0], /^house \(/);
    const svg = (await s.rpc('tools/call', { name: 'get_icon_svg', arguments: { name: 'heart', weight: 'fill', size: 32 } })).result.content[0].text;
    assert.match(svg, /^<svg [^>]*width="32"/);
    const code = (await s.rpc('tools/call', { name: 'get_icon_code', arguments: { name: 'shopping-cart', platform: 'react', weight: 'bold' } })).result.content[0].text;
    assert.match(code, /import \{ ShoppingCart \} from '@icon-monks\/react'/);
    const miss = (await s.rpc('tools/call', { name: 'get_icon_svg', arguments: { name: 'hous' } })).result;
    assert.equal(miss.isError, true);
    assert.equal((await s.rpc('nope', {})).error.code, -32601);
  } finally { s.close(); }
});
