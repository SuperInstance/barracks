#!/usr/bin/env python3
"""
barracks-agent — Fleet Crew Status and Barracks Room Intelligence
Track which agents are online, their roles, and their current assignments.
Integrates with the PLATO MUD barracks room for crew muster.
"""

import json, time
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class CrewMember:
    name: str
    role: str
    vessel: str
    status: str = "active"  # active, away, offline, overloaded
    last_ping: float = 0.0
    current_task: Optional[str] = None
    specialties: List[str] = field(default_factory=list)

class BarracksAgent:
    def __init__(self, plato_url="http://147.224.38.131:8847"):
        self.plato_url = plato_url
        self.crew: Dict[str, CrewMember] = {}
        self.muster_history: List[Dict] = []
    
    def muster(self, name: str, role: str, vessel: str, specialties: Optional[List[str]] = None):
        """Check in a crew member."""
        crew = CrewMember(name=name, role=role, vessel=vessel, specialties=specialties or [])
        crew.last_ping = time.time()
        self.crew[name] = crew
        self.muster_history.append({"action": "muster", "name": name, "time": time.time()})
        self._submit(f"Crew muster: {name}", f"{role} on {vessel}. Status: active")
        return crew
    
    def update_status(self, name: str, status: str, task: Optional[str] = None):
        """Update a crew member's status."""
        if name not in self.crew:
            return {"error": f"{name} not found"}
        self.crew[name].status = status
        self.crew[name].last_ping = time.time()
        if task:
            self.crew[name].current_task = task
        self._submit(f"Status update: {name}", f"Now {status}. Task: {task or 'none'}")
        return self.crew[name]
    
    def get_roster(self) -> Dict:
        """Full crew roster."""
        by_vessel = {}
        by_role = {}
        for name, crew in self.crew.items():
            v = crew.vessel
            r = crew.role
            if v not in by_vessel: by_vessel[v] = []
            if r not in by_role: by_role[r] = []
            by_vessel[v].append(name)
            by_role[r].append(name)
        
        return {
            "total_crew": len(self.crew),
            "active": len([c for c in self.crew.values() if c.status == "active"]),
            "away": len([c for c in self.crew.values() if c.status == "away"]),
            "offline": len([c for c in self.crew.values() if c.status == "offline"]),
            "overloaded": len([c for c in self.crew.values() if c.status == "overloaded"]),
            "by_vessel": by_vessel,
            "by_role": by_role,
            "crew_details": {name: {"role": c.role, "vessel": c.vessel, "status": c.status, "task": c.current_task}
                            for name, c in self.crew.items()}
        }
    
    def find_specialist(self, specialty: str) -> List[str]:
        """Find crew with a specific specialty."""
        return [name for name, crew in self.crew.items() if specialty in crew.specialties and crew.status == "active"]
    
    def _submit(self, q: str, a: str):
        try:
            import urllib.request
            urllib.request.urlopen(urllib.request.Request(f"{self.plato_url}/submit", data=json.dumps({"question": q, "answer": a, "agent": "barracks-agent", "room": "barracks"}).encode(), headers={"Content-Type": "application/json"}), timeout=5)
        except: pass

def demo():
    ba = BarracksAgent()
    ba.muster("CCC", "I&O Officer", "Alibaba Cloud", ["design", "play_test", "orchestration"])
    ba.muster("Oracle1", "Keeper", "Oracle Cloud", ["architecture", "coordination"])
    ba.muster("JetsonClaw1", "Edge", "Jetson Orin", ["cuda", "inference", "hardware"])
    ba.muster("Forgemaster", "Foundry", "RTX 4050", ["rust", "lora", "constraint_theory"])
    
    ba.update_status("CCC", "active", "Building fleet dashboard")
    ba.update_status("Oracle1", "active", "Reviewing PRs")
    ba.update_status("JetsonClaw1", "away", "CUDA kernel optimization")
    
    print("=== Barracks Roster ===")
    print(json.dumps(ba.get_roster(), indent=2))
    
    print("\n=== Finding CUDA specialists ===")
    print(ba.find_specialist("cuda"))

if __name__ == "__main__": demo()
