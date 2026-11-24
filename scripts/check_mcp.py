"""Probar handshake, descubrimiento e invocación MCP real (no mock)."""
import asyncio
from dotenv import load_dotenv
load_dotenv()
from mcp import Client
from app.settings import Settings

async def main():
    cfg = Settings.read()
    async with Client(server=cfg.mcp_url) as client:
        catalog = await client.list_tools()
        names = [t.name for t in catalog.tools]
        print('Servidor MCP:', cfg.mcp_url)
        print('Herramientas descubiertas:', names)
        if not {'search_knowledge','get_ticket_categories'}.issubset(names):
            raise RuntimeError('El servidor MCP no ofrece todas las herramientas esperadas')
        result = await client.call_tool('get_ticket_categories', {})
        if result.is_error:
            raise RuntimeError('Error al invocar herramienta MCP')
        for content in result.content:
            if getattr(content, 'text', None): print(content.text)
        print('MCP: handshake + tools/list + tools/call verificados')

if __name__ == '__main__':
    asyncio.run(main())
