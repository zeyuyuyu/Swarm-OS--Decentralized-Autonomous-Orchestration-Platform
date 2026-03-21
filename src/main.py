import os
import asyncio
import logging
from swarm_os.core.cluster import SwarmCluster
from swarm_os.core.agent import SwarmAgent

# Initialize the Swarm-OS cluster
cluster = SwarmCluster()

# Register agents to the cluster
agent1 = SwarmAgent()
cluster.register_agent(agent1)

# Start the cluster orchestration
async def main():
    await cluster.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())