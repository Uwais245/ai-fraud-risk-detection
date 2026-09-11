from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class NetworkNode(BaseModel):
    id: str
    type: str  # customer, device, ip, transaction, location
    label: str
    risk_level: str  # LOW, MEDIUM, HIGH
    metadata: Dict[str, Any] = {}


class NetworkEdge(BaseModel):
    source: str
    target: str
    type: str  # uses_device, uses_ip, made_transaction, from_location
    weight: int = 1


class NetworkGraphResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]


class NetworkCluster(BaseModel):
    cluster_id: str
    nodes: List[str]
    risk_score: float
    entity_count: int
    entity_types: Dict[str, int]


class NetworkClustersResponse(BaseModel):
    clusters: List[NetworkCluster]


class NetworkGraphRequest(BaseModel):
    customer_id: Optional[str] = None
    transaction_id: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    depth: int = Field(default=2, ge=1, le=5)
    risk_level: Optional[str] = None
    limit: int = Field(default=500, ge=10, le=2000)