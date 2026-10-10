"""Real HTTP transport test, using an isolated server and database."""
import asyncio
import os
import socket
import subprocess
import sys
import time

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


def test_mcp_http_lifecycle(tmp_path):
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    token = 'isolated-test-token'
    env = {**os.environ, 'HOMERELAY_DB': str(tmp_path/'mcp.db'), 'HOMERELAY_TOKEN': token}
    server = subprocess.Popen([sys.executable,'-m','uvicorn','homerelay.app:app','--host','127.0.0.1','--port',str(port)],
                              env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with httpx.Client(base_url=base,headers={'Authorization':'Bearer '+token}) as http:
            for _ in range(100):
                if server.poll() is not None:
                    raise AssertionError('MCP server exited before startup')
                try:
                    if http.get('/health').status_code == 200:
                        break
                except httpx.ConnectError:
                    time.sleep(.1)
            else:
                raise AssertionError('MCP server did not become healthy')
            alex = http.post('/api/members',json={'name':'Alex'}).json()
            mira = http.post('/api/members',json={'name':'Mira'}).json()

        async def workflow():
            async with httpx.AsyncClient(headers={'Authorization':'Bearer '+token}) as http:
                async with streamable_http_client(base+'/mcp/', http_client=http) as (read, write, _):
                    async with ClientSession(read, write) as client:
                        initialized = await client.initialize()
                        assert initialized.protocolVersion == '2025-11-25'
                        tools = await client.list_tools()
                        assert len(tools.tools) == 6
                        created = await client.call_tool('create_household_task', {'title':'Take recycling out','owner_id':alex['id'],
                            'due_at':'2026-10-15T10:00:00+05:30','priority':2,'request_id':'mcp-recycling'})
                        assert not created.isError
                        task = created.structuredContent
                        proposed = await client.call_tool('propose_handoff', {'task_id':task['id'],'actor_id':alex['id'],
                            'recipient_id':mira['id'],'version':1})
                        assert proposed.structuredContent['owner_id'] == alex['id']
                        stale = await client.call_tool('respond_to_handoff', {'task_id':task['id'],'actor_id':mira['id'],
                            'version':1,'accept':True})
                        assert stale.isError
                        accepted = await client.call_tool('respond_to_handoff', {'task_id':task['id'],'actor_id':mira['id'],
                            'version':2,'accept':True})
                        assert accepted.structuredContent['owner_id'] == mira['id']
                        briefing = await client.call_tool('household_briefing', {'member_id':mira['id']})
                        assert len(briefing.structuredContent['open_tasks']) == 1
                        done = await client.call_tool('complete_household_task', {'task_id':task['id'],'actor_id':mira['id'],'version':3})
                        assert done.structuredContent['status'] == 'done'
                        result = await client.call_tool('household_board', {})
                        assert result.structuredContent['tasks'][0]['status'] == 'done'
        asyncio.run(workflow())
    finally:
        server.terminate()
        server.wait(timeout=10)
