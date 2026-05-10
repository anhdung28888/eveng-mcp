"""Lab management tools for EVE-NG MCP Server."""

import asyncio
from typing import Any, TYPE_CHECKING

from mcp.types import TextContent
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP
    from ..core.eveng_client import EVENGClientWrapper

from ..config import get_logger


logger = get_logger("LabManagementTools")


def _as_mapping(payload: Any) -> dict[str, Any]:
    """Normalize an EVE-NG payload to a mapping."""
    if isinstance(payload, dict):
        return payload
    return {}


def _as_sequence(payload: Any) -> list[Any]:
    """Normalize an EVE-NG payload to a sequence."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return list(payload.values())
    return []


class ListLabsArgs(BaseModel):
    """Arguments for list_labs tool."""

    path: str = Field(default="/", description="Path to list labs from (default: /)")


class CreateLabArgs(BaseModel):
    """Arguments for create_lab tool."""

    name: str = Field(description="Name of the lab")
    path: str = Field(default="/", description="Path where to create the lab (default: /)")
    description: str = Field(default="", description="Lab description")
    author: str = Field(default="", description="Lab author")
    version: str = Field(default="1", description="Lab version")


class GetLabDetailsArgs(BaseModel):
    """Arguments for get_lab_details tool."""

    lab_path: str = Field(description="Full path to the lab (e.g., /lab_name.unl)")


class DeleteLabArgs(BaseModel):
    """Arguments for delete_lab tool."""

    lab_path: str = Field(description="Full path to the lab to delete")


def register_lab_tools(mcp: "FastMCP", eveng_client: "EVENGClientWrapper") -> None:
    """Register lab management tools."""

    @mcp.tool()
    async def list_labs(path: str = "/") -> list[TextContent]:
        """List available labs in EVE-NG."""
        try:
            logger.info(f"Listing labs in path: {path}")

            if not eveng_client.is_connected:
                return [
                    TextContent(
                        type="text",
                        text="Not connected to EVE-NG server. Use connect_eveng_server tool first.",
                    )
                ]

            labs = await eveng_client.list_labs(path)
            if not labs:
                return [TextContent(type="text", text=f"No labs found in path: {path}")]

            labs_text = f"Labs in {path}:\n\n"
            for lab in labs:
                labs_text += f"- {lab.get('name', 'Unknown')}\n"
                labs_text += f"  File: {lab.get('file', 'Unknown')}\n"
                labs_text += f"  Path: {lab.get('path', 'Unknown')}\n"
                labs_text += f"  Full Path: {lab.get('full_path', 'Unknown')}\n"
                labs_text += f"  Modified: {lab.get('mtime', 'Unknown')}\n"
                labs_text += (
                    f"  Use 'get_lab_details' with path '{lab.get('full_path', '')}' "
                    "for detailed metadata\n\n"
                )

            return [TextContent(type="text", text=labs_text)]
        except Exception as e:
            logger.error(f"Failed to list labs: {e}")
            return [TextContent(type="text", text=f"Failed to list labs: {str(e)}")]

    @mcp.tool()
    async def create_lab(
        name: str,
        path: str = "/",
        description: str = "",
        author: str = "",
        version: str = "1",
    ) -> list[TextContent]:
        """Create a new lab in EVE-NG."""
        try:
            logger.info(f"Creating lab: {name} in {path}")

            if not eveng_client.is_connected:
                return [
                    TextContent(
                        type="text",
                        text="Not connected to EVE-NG server. Use connect_eveng_server tool first.",
                    )
                ]

            await eveng_client.create_lab(
                name=name,
                path=path,
                description=description,
                author=author,
                version=version,
            )

            return [
                TextContent(
                    type="text",
                    text=(
                        "Successfully created lab!\n\n"
                        f"Name: {name}\n"
                        f"Path: {path}\n"
                        f"Description: {description}\n"
                        f"Author: {author}\n"
                        f"Version: {version}\n\n"
                        "Lab is ready for adding nodes and networks."
                    ),
                )
            ]
        except Exception as e:
            logger.error(f"Failed to create lab: {e}")
            return [TextContent(type="text", text=f"Failed to create lab: {str(e)}")]

    @mcp.tool()
    async def get_lab_details(lab_path: str) -> list[TextContent]:
        """Get detailed information about a specific lab."""
        try:
            logger.info(f"Getting details for lab: {lab_path}")

            if not eveng_client.is_connected:
                return [
                    TextContent(
                        type="text",
                        text="Not connected to EVE-NG server. Use connect_eveng_server tool first.",
                    )
                ]

            lab_response = await eveng_client.get_lab(lab_path)
            lab = _as_mapping(lab_response.get("data", {}))

            try:
                nodes_response = await asyncio.to_thread(eveng_client.api.list_nodes, lab_path)
                raw_nodes = nodes_response.get("data", {})
            except Exception as e:
                logger.warning(f"Failed to get nodes for lab {lab_path}: {e}")
                raw_nodes = {}

            try:
                networks_response = await asyncio.to_thread(
                    eveng_client.api.list_lab_networks, lab_path
                )
                raw_networks = networks_response.get("data", {})
            except Exception as e:
                logger.warning(f"Failed to get networks for lab {lab_path}: {e}")
                raw_networks = {}

            try:
                links_response = await asyncio.to_thread(eveng_client.api.list_lab_links, lab_path)
                links = _as_mapping(links_response.get("data", {}))
            except Exception as e:
                logger.warning(f"Failed to get links for lab {lab_path}: {e}")
                links = {}

            if isinstance(raw_nodes, dict):
                nodes_by_id = {
                    str(node_id): _as_mapping(node) for node_id, node in raw_nodes.items()
                }
            else:
                nodes_by_id = {}
                for index, node in enumerate(_as_sequence(raw_nodes), start=1):
                    node_data = _as_mapping(node)
                    node_id = str(node_data.get("id") or node_data.get("node_id") or index)
                    nodes_by_id[node_id] = node_data

            if isinstance(raw_networks, dict):
                networks_by_id = {
                    str(net_id): _as_mapping(network)
                    for net_id, network in raw_networks.items()
                }
            else:
                networks_by_id = {}
                for index, network in enumerate(_as_sequence(raw_networks), start=1):
                    network_data = _as_mapping(network)
                    network_id = str(
                        network_data.get("id") or network_data.get("network_id") or index
                    )
                    networks_by_id[network_id] = network_data

            node_interfaces: dict[str, dict[str, Any]] = {}
            for node_id in nodes_by_id:
                try:
                    interfaces_response = await asyncio.to_thread(
                        eveng_client.api.get_node_interfaces, lab_path, node_id
                    )
                    node_interfaces[node_id] = _as_mapping(interfaces_response.get("data", {}))
                except Exception as e:
                    logger.warning(f"Failed to get interfaces for node {node_id}: {e}")
                    node_interfaces[node_id] = {}

            details_text = f"Lab Details: {lab.get('name', 'Unknown')}\n\n"
            details_text += "Basic Information:\n"
            details_text += f"  Name: {lab.get('name', 'Unknown')}\n"
            details_text += f"  Filename: {lab.get('filename', 'Unknown')}\n"
            details_text += f"  Path: {lab_path}\n"
            details_text += f"  Description: {lab.get('description', 'No description')}\n"
            details_text += f"  Author: {lab.get('author', 'Unknown')}\n"
            details_text += f"  Version: {lab.get('version', 'Unknown')}\n"
            details_text += f"  ID: {lab.get('id', 'Unknown')}\n"
            details_text += (
                f"  Script Timeout: {lab.get('scripttimeout', 'Unknown')} seconds\n"
            )
            details_text += (
                f"  Lock Status: {'Locked' if lab.get('lock', 0) else 'Unlocked'}\n\n"
            )

            details_text += f"Nodes ({len(nodes_by_id)}):\n"
            if nodes_by_id:
                for node_id, node in nodes_by_id.items():
                    status_map = {0: "Stopped", 1: "Starting", 2: "Running", 3: "Stopping"}
                    status = status_map.get(node.get("status", 0), f"Unknown ({node.get('status', 0)})")
                    console_url = node.get("url", "")
                    console_port = console_url.split(":")[-1] if ":" in console_url else ""

                    details_text += f"  - {node.get('name', f'Node {node_id}')}\n"
                    details_text += f"    ID: {node_id}\n"
                    details_text += f"    Type: {node.get('type', 'Unknown')}\n"
                    details_text += f"    Template: {node.get('template', 'Unknown')}\n"
                    details_text += f"    Image: {node.get('image', 'Unknown')}\n"
                    details_text += f"    Status: {status}\n"
                    details_text += f"    CPU: {node.get('cpu', 'Unknown')}\n"
                    details_text += f"    RAM: {node.get('ram', 'Unknown')} MB\n"
                    details_text += f"    Ethernet Ports: {node.get('ethernet', 'Unknown')}\n"
                    details_text += f"    Console Type: {node.get('console', 'None')}\n"
                    if console_url:
                        details_text += f"    Console URL: {console_url}\n"
                    if console_port:
                        details_text += f"    Console Port: {console_port}\n"
                    details_text += f"    UUID: {node.get('uuid', 'Unknown')}\n"

                    interfaces = node_interfaces.get(node_id, {})
                    ethernet_interfaces = _as_sequence(interfaces.get("ethernet", []))
                    serial_interfaces = _as_sequence(interfaces.get("serial", []))
                    if ethernet_interfaces or serial_interfaces:
                        details_text += "    Interfaces:\n"
                        for eth_int in ethernet_interfaces:
                            int_name = eth_int.get("name", "Unknown")
                            net_id = eth_int.get("network_id", 0)
                            if net_id == 0:
                                connection = "Not connected"
                            else:
                                network_name = networks_by_id.get(str(net_id), {}).get(
                                    "name", f"Network {net_id}"
                                )
                                connection = f"Connected to {network_name}"
                            details_text += f"      - {int_name}: {connection}\n"

                        for ser_int in serial_interfaces:
                            int_name = ser_int.get("name", "Unknown")
                            details_text += f"      - {int_name} (Serial): Not connected\n"
                    details_text += "\n"
            else:
                details_text += "  No nodes configured\n\n"

            details_text += f"Networks ({len(networks_by_id)}):\n"
            if networks_by_id:
                for net_id, network in networks_by_id.items():
                    details_text += f"  - {network.get('name', f'Network {net_id}')}\n"
                    details_text += f"    ID: {net_id}\n"
                    details_text += f"    Type: {network.get('type', 'Unknown')}\n"
                    details_text += f"    Connected Devices: {network.get('count', 0)}\n"
                    details_text += (
                        f"    Visibility: {'Visible' if network.get('visibility', 1) else 'Hidden'}\n"
                    )
                    details_text += f"    Icon: {network.get('icon', 'Unknown')}\n"
                    details_text += (
                        f"    Position: ({network.get('left', 'Unknown')}, {network.get('top', 'Unknown')})\n\n"
                    )
            else:
                details_text += "  No networks configured\n"

            details_text += "\nTopology & Connections:\n"
            ethernet_links = links.get("ethernet", {})
            serial_links = _as_sequence(links.get("serial", []))
            if ethernet_links:
                details_text += "  Ethernet Connections:\n"
                for net_id, net_name in ethernet_links.items():
                    details_text += f"    - Network {net_id} ({net_name})\n"
            if serial_links:
                details_text += "  Serial Connections:\n"
                for serial_link in serial_links:
                    details_text += f"    - {serial_link}\n"
            if not ethernet_links and not serial_links:
                details_text += "  No connections configured\n"

            return [TextContent(type="text", text=details_text)]
        except Exception as e:
            logger.error(f"Failed to get lab details: {e}")
            return [TextContent(type="text", text=f"Failed to get lab details: {str(e)}")]

    @mcp.tool()
    async def delete_lab(lab_path: str) -> list[TextContent]:
        """Delete a lab from EVE-NG."""
        try:
            logger.info(f"Deleting lab: {lab_path}")

            if not eveng_client.is_connected:
                return [
                    TextContent(
                        type="text",
                        text="Not connected to EVE-NG server. Use connect_eveng_server tool first.",
                    )
                ]

            await eveng_client.delete_lab(lab_path)
            return [
                TextContent(
                    type="text",
                    text=(
                        f"Successfully deleted lab: {lab_path}\n\n"
                        "This action cannot be undone. The lab and all its associated "
                        "resources have been permanently removed."
                    ),
                )
            ]
        except Exception as e:
            logger.error(f"Failed to delete lab: {e}")
            return [TextContent(type="text", text=f"Failed to delete lab: {str(e)}")]
