from collections import defaultdict
import json

class ResourceAllocationGraph:
    def __init__(self):
        self.processes = set()
        self.resources = {}
        self.allocations = defaultdict(int)
        self.requests = defaultdict(int)
        self.next_process_id = 1
        self.next_resource_id = 1

    def get_auto_process_name(self):
        while f"P{self.next_process_id}" in self.processes:
            self.next_process_id += 1
        return f"P{self.next_process_id}"

    def get_auto_resource_name(self):
        while f"R{self.next_resource_id}" in self.resources:
            self.next_resource_id += 1
        return f"R{self.next_resource_id}"

    def add_process(self, process_id=None):
        if not process_id:
            process_id = self.get_auto_process_name()
        if process_id in self.processes:
            raise ValueError(f"Process {process_id} already exists")
        self.processes.add(process_id)
        return process_id

    def add_resource(self, resource_id=None, instances=1):
        if not resource_id:
            resource_id = self.get_auto_resource_name()
        if resource_id in self.resources:
            raise ValueError(f"Resource {resource_id} already exists")
        self.resources[resource_id] = {'total': instances, 'available': instances}
        return resource_id

    def add_request(self, process, resource, count=1):
        if process not in self.processes:
            raise ValueError(f"Process {process} does not exist")
        if resource not in self.resources:
            raise ValueError(f"Resource {resource} does not exist")
        self.requests[(process, resource)] += count

    def add_allocation(self, process, resource, count=1):
        if process not in self.processes:
            raise ValueError(f"Process {process} does not exist")
        if resource not in self.resources:
            raise ValueError(f"Resource {resource} does not exist")
        available = self.resources[resource]['available']
        if count > available:
            raise ValueError(f"Not enough instances available ({available}) in {resource}")
        self.allocations[(process, resource)] += count
        self.resources[resource]['available'] -= count

    def remove_allocation(self, process, resource, count=1):
        if (process, resource) in self.allocations:
            self.allocations[(process, resource)] -= count
            self.resources[resource]['available'] += count
            if self.allocations[(process, resource)] <= 0:
                del self.allocations[(process, resource)]

    def detect_deadlock(self):
        work = {r: info['available'] for r, info in self.resources.items()}
        allocation = defaultdict(lambda: defaultdict(int))
        request = defaultdict(lambda: defaultdict(int))
        for (p, r), cnt in self.allocations.items():
            allocation[p][r] = cnt
        for (p, r), cnt in self.requests.items():
            request[p][r] = cnt
        finish = {p: False for p in self.processes}
        while True:
            found = False
            for p in self.processes:
                if not finish[p] and all(request[p][r] <= work[r] for r in self.resources):
                    for r in self.resources:
                        work[r] += allocation[p][r]
                    finish[p] = True
                    found = True
            if not found:
                break
        deadlocked = [p for p, done in finish.items() if not done]
        return len(deadlocked) > 0, deadlocked

    def export_state(self):
        state = {
            "processes": list(self.processes),
            "resources": self.resources,
            "allocations": dict(self.allocations),
            "requests": dict(self.requests)
        }
        return json.dumps(state, indent=4)

    def import_state(self, state_json):
        state = json.loads(state_json)
        self.processes = set(state["processes"])
        self.resources = state["resources"]
        self.allocations = defaultdict(int, state["allocations"])
        self.requests = defaultdict(int, state["requests"])