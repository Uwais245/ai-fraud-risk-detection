from sqlalchemy import select, func, and_, or_, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional, Set
from app.models.transaction import Transaction
from app.models.risk_assessment import RiskAssessment
from app.schemas.network import NetworkNode, NetworkEdge, NetworkGraphResponse, NetworkCluster, NetworkClustersResponse


class NetworkService:
    """Service for fraud network graph data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_network_graph(
        self,
        customer_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        depth: int = 2,
        risk_level: Optional[str] = None,
        limit: int = 500
    ) -> NetworkGraphResponse:
        """Get network graph data for visualization"""
        # Find seed entities
        seed_customers = set()
        seed_devices = set()
        seed_ips = set()
        
        if customer_id:
            seed_customers.add(customer_id)
        if transaction_id:
            # Find customer, device, IP for this transaction
            stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
            result = await self.db.execute(stmt)
            txn = result.scalar_one_or_none()
            if txn:
                if txn.customer_id:
                    seed_customers.add(txn.customer_id)
                if txn.device_id:
                    seed_devices.add(txn.device_id)
                if txn.ip_address:
                    seed_ips.add(txn.ip_address)
        if device_id:
            seed_devices.add(device_id)
        if ip_address:
            seed_ips.add(ip_address)
        
        # If no seeds, get high-risk entities
        if not seed_customers and not seed_devices and not seed_ips:
            stmt = (
                select(Transaction.customer_id)
                .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
                .where(RiskAssessment.risk_level == "HIGH")
                .distinct()
                .limit(10)
            )
            result = await self.db.execute(stmt)
            seed_customers = set(row[0] for row in result.all())
        
        # Expand graph by depth
        all_customers = set(seed_customers)
        all_devices = set(seed_devices)
        all_ips = set(seed_ips)
        all_transactions = set()
        all_locations = set()
        
        for _ in range(depth):
            # Find transactions for current customers
            if all_customers:
                stmt = (
                    select(Transaction.transaction_id, Transaction.device_id, Transaction.ip_address, Transaction.location)
                    .where(Transaction.customer_id.in_(all_customers))
                    .limit(limit)
                )
                result = await self.db.execute(stmt)
                for row in result.all():
                    all_transactions.add(row.transaction_id)
                    if row.device_id:
                        all_devices.add(row.device_id)
                    if row.ip_address:
                        all_ips.add(row.ip_address)
                    if row.location:
                        all_locations.add(row.location)
            
            # Find customers for current devices
            if all_devices:
                stmt = (
                    select(Transaction.customer_id, Transaction.ip_address, Transaction.location)
                    .where(Transaction.device_id.in_(all_devices))
                    .limit(limit)
                )
                result = await self.db.execute(stmt)
                for row in result.all():
                    all_customers.add(row.customer_id)
                    if row.ip_address:
                        all_ips.add(row.ip_address)
                    if row.location:
                        all_locations.add(row.location)
            
            # Find customers for current IPs
            if all_ips:
                stmt = (
                    select(Transaction.customer_id, Transaction.device_id, Transaction.location)
                    .where(Transaction.ip_address.in_(all_ips))
                    .limit(limit)
                )
                result = await self.db.execute(stmt)
                for row in result.all():
                    all_customers.add(row.customer_id)
                    if row.device_id:
                        all_devices.add(row.device_id)
                    if row.location:
                        all_locations.add(row.location)
        
        # Get risk levels for entities
        customer_risk = await self._get_customer_risk(all_customers)
        device_risk = await self._get_device_risk(all_devices)
        ip_risk = await self._get_ip_risk(all_ips)
        txn_risk = await self._get_transaction_risk(all_transactions)
        location_risk = await self._get_location_risk(all_locations)
        
        # Build nodes
        nodes = []
        for cust_id in list(all_customers)[:limit//5]:
            risk = customer_risk.get(cust_id, "LOW")
            if risk_level and risk != risk_level:
                continue
            nodes.append(NetworkNode(
                id=f"cust_{cust_id}",
                type="customer",
                label=cust_id,
                risk_level=risk,
                metadata={"entity_type": "customer", "customer_id": cust_id}
            ))
        
        for dev_id in list(all_devices)[:limit//5]:
            risk = device_risk.get(dev_id, "LOW")
            if risk_level and risk != risk_level:
                continue
            nodes.append(NetworkNode(
                id=f"dev_{dev_id}",
                type="device",
                label=dev_id[:20] + "..." if len(dev_id) > 20 else dev_id,
                risk_level=risk,
                metadata={"entity_type": "device", "device_id": dev_id}
            ))
        
        for ip in list(all_ips)[:limit//5]:
            risk = ip_risk.get(ip, "LOW")
            if risk_level and risk != risk_level:
                continue
            nodes.append(NetworkNode(
                id=f"ip_{ip}",
                type="ip",
                label=ip,
                risk_level=risk,
                metadata={"entity_type": "ip", "ip_address": ip}
            ))
        
        for txn_id in list(all_transactions)[:limit//5]:
            risk = txn_risk.get(txn_id, "LOW")
            if risk_level and risk != risk_level:
                continue
            nodes.append(NetworkNode(
                id=f"txn_{txn_id}",
                type="transaction",
                label=txn_id,
                risk_level=risk,
                metadata={"entity_type": "transaction", "transaction_id": txn_id}
            ))
        
        for loc in list(all_locations)[:limit//5]:
            risk = location_risk.get(loc, "LOW")
            if risk_level and risk != risk_level:
                continue
            nodes.append(NetworkNode(
                id=f"loc_{loc}",
                type="location",
                label=loc,
                risk_level=risk,
                metadata={"entity_type": "location", "location": loc}
            ))
        
        # Build edges
        edges = []
        # Customer -> Device
        stmt = (
            select(Transaction.customer_id, Transaction.device_id)
            .where(
                and_(
                    Transaction.customer_id.in_(all_customers),
                    Transaction.device_id.in_(all_devices)
                )
            )
            .distinct()
        )
        result = await self.db.execute(stmt)
        for row in result.all():
            edges.append(NetworkEdge(
                source=f"cust_{row.customer_id}",
                target=f"dev_{row.device_id}",
                type="uses_device",
                weight=1
            ))
        
        # Device -> IP
        stmt = (
            select(Transaction.device_id, Transaction.ip_address)
            .where(
                and_(
                    Transaction.device_id.in_(all_devices),
                    Transaction.ip_address.in_(all_ips)
                )
            )
            .distinct()
        )
        result = await self.db.execute(stmt)
        for row in result.all():
            edges.append(NetworkEdge(
                source=f"dev_{row.device_id}",
                target=f"ip_{row.ip_address}",
                type="uses_ip",
                weight=1
            ))
        
        # Customer -> IP (direct)
        stmt = (
            select(Transaction.customer_id, Transaction.ip_address)
            .where(
                and_(
                    Transaction.customer_id.in_(all_customers),
                    Transaction.ip_address.in_(all_ips)
                )
            )
            .distinct()
        )
        result = await self.db.execute(stmt)
        for row in result.all():
            edges.append(NetworkEdge(
                source=f"cust_{row.customer_id}",
                target=f"ip_{row.ip_address}",
                type="uses_ip",
                weight=1
            ))
        
        # Customer -> Transaction
        for txn_id in all_transactions:
            stmt = select(Transaction.customer_id).where(Transaction.transaction_id == txn_id)
            result = await self.db.execute(stmt)
            cust_id = result.scalar_one_or_none()
            if cust_id and cust_id in all_customers:
                edges.append(NetworkEdge(
                    source=f"cust_{cust_id}",
                    target=f"txn_{txn_id}",
                    type="made_transaction",
                    weight=1
                ))
        
        # Transaction -> Location
        for txn_id in all_transactions:
            stmt = select(Transaction.location).where(Transaction.transaction_id == txn_id)
            result = await self.db.execute(stmt)
            loc = result.scalar_one_or_none()
            if loc and loc in all_locations:
                edges.append(NetworkEdge(
                    source=f"txn_{txn_id}",
                    target=f"loc_{loc}",
                    type="from_location",
                    weight=1
                ))
        
        return NetworkGraphResponse(nodes=nodes, edges=edges)
    
    async def _get_customer_risk(self, customer_ids: Set[str]) -> Dict[str, str]:
        if not customer_ids:
            return {}
        stmt = (
            select(Transaction.customer_id, func.max(RiskAssessment.risk_level))
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.customer_id.in_(customer_ids))
            .group_by(Transaction.customer_id)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
    
    async def _get_device_risk(self, device_ids: Set[str]) -> Dict[str, str]:
        if not device_ids:
            return {}
        stmt = (
            select(Transaction.device_id, func.max(RiskAssessment.risk_level))
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.device_id.in_(device_ids))
            .group_by(Transaction.device_id)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
    
    async def _get_ip_risk(self, ip_addresses: Set[str]) -> Dict[str, str]:
        if not ip_addresses:
            return {}
        stmt = (
            select(Transaction.ip_address, func.max(RiskAssessment.risk_level))
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.ip_address.in_(ip_addresses))
            .group_by(Transaction.ip_address)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
    
    async def _get_transaction_risk(self, txn_ids: Set[str]) -> Dict[str, str]:
        if not txn_ids:
            return {}
        stmt = (
            select(RiskAssessment.transaction_id, RiskAssessment.risk_level)
            .where(RiskAssessment.transaction_id.in_(txn_ids))
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
    
    async def _get_location_risk(self, locations: Set[str]) -> Dict[str, str]:
        if not locations:
            return {}
        stmt = (
            select(Transaction.location, func.max(RiskAssessment.risk_level))
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.location.in_(locations))
            .group_by(Transaction.location)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
    
    async def get_suspicious_clusters(self, min_size: int = 3, risk_threshold: str = "HIGH") -> NetworkClustersResponse:
        """Find connected components with high-risk density"""
        # Simplified: find IPs shared by multiple high-risk customers
        stmt = (
            select(Transaction.ip_address, func.count(distinct(Transaction.customer_id)).label("customer_count"))
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(RiskAssessment.risk_level == risk_threshold)
            .group_by(Transaction.ip_address)
            .having(func.count(distinct(Transaction.customer_id)) >= min_size)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        clusters = []
        for i, row in enumerate(rows):
            # Get all customers for this IP
            stmt2 = (
                select(distinct(Transaction.customer_id))
                .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
                .where(
                    Transaction.ip_address == row.ip_address,
                    RiskAssessment.risk_level == risk_threshold
                )
            )
            result2 = await self.db.execute(stmt2)
            customers = [r[0] for r in result2.all()]
            
            clusters.append(NetworkCluster(
                cluster_id=f"cluster_{i}",
                nodes=customers,
                risk_score=90.0,  # High risk for shared IP
                entity_count=len(customers),
                entity_types={"customer": len(customers)}
            ))
        
        return NetworkClustersResponse(clusters=clusters)