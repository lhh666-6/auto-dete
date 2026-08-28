import pytest

from auto_decte_agent_benchmark.mcp_server import create_server
from auto_decte_agent_benchmark.tool_surface import (
    assert_logical_tool_equivalence,
    canonical_tool_surface,
)


class StubBridge:
    def model(self, operation: str, **values):
        return {"operation": operation, **values}


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_server_exposes_exactly_the_two_canonical_model_tools() -> None:
    server = create_server(StubBridge())

    tools = sorted(await server.list_tools(), key=lambda item: item.name)

    assert [tool.name for tool in tools] == ["auto_decte_propose", "auto_decte_verify"]
    propose = tools[0]
    assert set(propose.inputSchema["properties"]["value"]) <= {"title"}
    assert propose.inputSchema["additionalProperties"] is False
    assert_logical_tool_equivalence(
        canonical_tool_surface(),
        {
            "fastmcp": [
                {"name": tool.name, "inputSchema": tool.inputSchema}
                for tool in tools
            ]
        },
    )
