# Cluster Health Monitor for Swarmic-Ops
# Provides real-time health metrics, predictive analytics, and auto-healing capabilities

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import kubernetes.client as k8s
from prometheus_client import Counter, Gauge, start_http_server

@dataclass
class NodeHealth:
    node_name: str
    cpu_usage: float
    memory_usage: float
    pod_count: int
    last_heartbeat: datetime
    status: str

class ClusterHealthMonitor:
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.node_metrics: Dict[str, NodeHealth] = {}
        self.k8s_client = k8s.CoreV1Api()
        
        # Prometheus metrics
        self.node_health_score = Gauge('node_health_score', 'Overall node health score', ['node'])
        self.healing_actions = Counter('healing_actions_total', 'Number of auto-healing actions taken')
        
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self):
        """Start the continuous monitoring loop"""
        start_http_server(8000)  # Prometheus metrics endpoint
        self.logger.info("Starting cluster health monitoring")
        
        while True:
            try:
                await self.check_cluster_health()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {str(e)}")
                
    async def check_cluster_health(self):
        """Perform comprehensive health check of the cluster"""
        nodes = self.k8s_client.list_node().items
        
        for node in nodes:
            metrics = await self.collect_node_metrics(node)
            health_score = self.calculate_health_score(metrics)
            
            self.node_metrics[node.metadata.name] = metrics
            self.node_health_score.labels(node=node.metadata.name).set(health_score)
            
            if health_score < 0.6:  # Critical threshold
                await self.initiate_healing(node.metadata.name, metrics)
                
    async def collect_node_metrics(self, node) -> NodeHealth:
        """Collect detailed metrics for a specific node"""
        try:
            # Get node metrics using metrics-server API
            metrics_api = k8s.CustomObjectsApi()
            metrics = metrics_api.get_cluster_custom_object(
                'metrics.k8s.io',
                'v1beta1',
                'nodes',
                node.metadata.name
            )
            
            return NodeHealth(
                node_name=node.metadata.name,
                cpu_usage=float(metrics['usage']['cpu'].rstrip('n')) / 1000000000,
                memory_usage=float(metrics['usage']['memory'].rstrip('Ki')) / 1024,
                pod_count=len(self.k8s_client.list_pod_for_all_namespaces(
                    field_selector=f'spec.nodeName={node.metadata.name}'
                ).items),
                last_heartbeat=datetime.now(),
                status=node.status.conditions[-1].type
            )
        except Exception as e:
            self.logger.error(f"Error collecting metrics for node {node.metadata.name}: {str(e)}")
            return None
            
    def calculate_health_score(self, metrics: NodeHealth) -> float:
        """Calculate a normalized health score (0-1) based on multiple factors"""
        if not metrics:
            return 0.0
            
        scores = [
            1.0 if metrics.status == 'Ready' else 0.0,  # Node readiness
            max(0, 1 - metrics.cpu_usage / 100),        # CPU health
            max(0, 1 - metrics.memory_usage / 100),     # Memory health
            1.0 if metrics.last_heartbeat > datetime.now() - timedelta(minutes=5) else 0.0
        ]
        
        return sum(scores) / len(scores)
        
    async def initiate_healing(self, node_name: str, metrics: NodeHealth):
        """Attempt to heal node issues automatically"""
        self.logger.warning(f"Initiating healing procedures for node {node_name}")
        
        try:
            if metrics.cpu_usage > 90:
                await self.rebalance_workload(node_name)
            
            if metrics.status != 'Ready':
                await self.drain_and_restart_node(node_name)
                
            self.healing_actions.inc()
            
        except Exception as e:
            self.logger.error(f"Healing failed for node {node_name}: {str(e)}")
            
    async def rebalance_workload(self, node_name: str):
        """Redistribute pods from overloaded node"""
        pods = self.k8s_client.list_pod_for_all_namespaces(
            field_selector=f'spec.nodeName={node_name}'
        ).items
        
        for pod in pods:
            if pod.metadata.namespace not in ['kube-system']:
                try:
                    self.k8s_client.delete_namespaced_pod(
                        pod.metadata.name,
                        pod.metadata.namespace
                    )
                    self.logger.info(f"Rebalancing: Deleted pod {pod.metadata.name}")
                except Exception as e:
                    self.logger.error(f"Failed to delete pod: {str(e)}")
                    
    async def drain_and_restart_node(self, node_name: str):
        """Drain node and trigger restart through cloud provider"""
        try:
            # Mark node as unschedulable
            self.k8s_client.patch_node(
                node_name,
                {
                    "spec": {
                        "unschedulable": True
                    }
                }
            )
            
            # Drain pods
            pods = self.k8s_client.list_pod_for_all_namespaces(
                field_selector=f'spec.nodeName={node_name}'
            ).items
            
            for pod in pods:
                if not pod.metadata.namespace == 'kube-system':
                    self.k8s_client.delete_namespaced_pod(
                        pod.metadata.name,
                        pod.metadata.namespace
                    )
                    
            self.logger.info(f"Successfully drained node {node_name}")
            
            # TODO: Implement cloud provider-specific node restart logic
            
        except Exception as e:
            self.logger.error(f"Failed to drain node {node_name}: {str(e)}")

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = ClusterHealthMonitor()
    asyncio.run(monitor.start_monitoring())
