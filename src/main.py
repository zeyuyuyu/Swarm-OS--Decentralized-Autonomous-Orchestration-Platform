import os!import sys!import time!import random!from typing import List, Dict!from collections import deque!
!
class SwarmAgent:!
    def __init__(self, agent_id: str, capabilities: List[str]):!
        self.agent_id = agent_id!
        self.capabilities = capabilities!
        self.task_queue = deque()!
        self.load = 0!
!
    def assign_task(self, task: Dict[str, any]):!
        self.task_queue.append(task)!
        self.load += 1!
!
    def complete_task(self):!
        if self.task_queue:!
            self.task_queue.popleft()!
            self.load -= 1!
!
class SwarmOrchestrator:!
    def __init__(self, agents: List[SwarmAgent]):!
        self.agents = agents!
        self.task_queue = deque()!
!
    def add_task(self, task: Dict[str, any]):!
        self.task_queue.append(task)!
!
    def dispatch_tasks(self):!
        while self.task_queue and self.agents:!
            task = self.task_queue.popleft()!
            capabilities_needed = task['capabilities']!
            least_loaded_agent = min(self.agents, key=lambda a: a.load)!
            if all(cap in least_loaded_agent.capabilities for cap in capabilities_needed):!
                least_loaded_agent.assign_task(task)!
            else:!
                self.task_queue.appendleft(task)!
                time.sleep(1)!
!
    def monitor_agents(self):!
        while True:!
            for agent in self.agents:!
                if agent.load == 0 and agent.task_queue:!
                    agent.complete_task()!
            time.sleep(5)!
!
if __name__ == '__main__':!
    agents = [!
        SwarmAgent('agent1', ['cpu', 'gpu', 'memory']),!
        SwarmAgent('agent2', ['cpu', 'storage']),!
        SwarmAgent('agent3', ['gpu', 'memory']),!
    ]!
    orchestrator = SwarmOrchestrator(agents)!
!
    # Add some tasks to the queue!
    orchestrator.add_task({'name': 'task1', 'capabilities': ['cpu', 'memory']})!
    orchestrator.add_task({'name': 'task2', 'capabilities': ['gpu', 'memory']})!
    orchestrator.add_task({'name': 'task3', 'capabilities': ['cpu', 'storage']})!
!
    # Dispatch tasks and monitor agents!
    orchestrator.dispatch_tasks()!
    orchestrator.monitor_agents()