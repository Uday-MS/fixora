from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.service_map import ServiceNode
from app.models.project import Project
from app.schemas.service_map import ServiceNodeCreate, ServiceGraphResponse, ServiceGraphEdge, ServiceNodeResponse

class ServiceMapService:

    @staticmethod
    async def get_service_graph(db: AsyncSession, project_id: str) -> ServiceGraphResponse:
        stmt = select(ServiceNode).where(ServiceNode.project_id == project_id)
        nodes = list((await db.execute(stmt)).scalars().all())

        edges: List[ServiceGraphEdge] = []
        for node in nodes:
            if node.dependencies:
                for dep in node.dependencies:
                    edges.append(ServiceGraphEdge(source=node.name, target=dep))

        node_responses = [
            ServiceNodeResponse(
                id=n.id,
                projectId=n.project_id,
                repositoryId=n.repository_id,
                name=n.name,
                tier=n.tier,
                status=n.status,
                runtime=n.runtime,
                dependencies=n.dependencies,
                metadataJson=n.metadata_json,
                createdAt=n.created_at,
            )
            for n in nodes
        ]

        return ServiceGraphResponse(nodes=node_responses, edges=edges)

    @staticmethod
    async def create_service_node(db: AsyncSession, project_id: str, data: ServiceNodeCreate) -> ServiceNode:
        proj_stmt = select(Project).where(Project.id == project_id)
        proj = (await db.execute(proj_stmt)).scalars().first()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        node = ServiceNode(
            project_id=project_id,
            repository_id=data.repositoryId,
            name=data.name,
            tier=data.tier,
            status=data.status,
            runtime=data.runtime,
            dependencies=data.dependencies,
            metadata_json=data.metadataJson,
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node
