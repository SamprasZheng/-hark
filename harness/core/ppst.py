"""
PPST Core - Minimal Python implementation for layer validation and CALL SKILL parsing.
This is engineering core: no philosophy, pure structure for Projects, Programs, Skills, Targets.
Open for extension.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import json

@dataclass
class PPSTLayers:
    project: str
    program: str
    skill: str
    target: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "PROJECT": self.project,
            "PROGRAM": self.program,
            "SKILL": self.skill,
            "TARGET": self.target
        }

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "PPSTLayers":
        return cls(
            project=d.get("PROJECT", ""),
            program=d.get("PROGRAM", ""),
            skill=d.get("SKILL", ""),
            target=d.get("TARGET", "")
        )

def validate_layers(layers: PPSTLayers) -> bool:
    """Basic validation: all fields non-empty."""
    return all([
        layers.project.strip(),
        layers.program.strip(),
        layers.skill.strip(),
        layers.target.strip()
    ])

def parse_call_skill(text: str) -> Optional[PPSTLayers]:
    """Parse a [CALL SKILL] block into PPSTLayers."""
    layers = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("PROJECT:"):
            layers["PROJECT"] = line.split(":", 1)[1].strip()
        elif line.startswith("PROGRAM:"):
            layers["PROGRAM"] = line.split(":", 1)[1].strip()
        elif line.startswith("SKILL:"):
            layers["SKILL"] = line.split(":", 1)[1].strip()
        elif line.startswith("TARGET:"):
            layers["TARGET"] = line.split(":", 1)[1].strip()
    if len(layers) == 4:
        ppst = PPSTLayers.from_dict(layers)
        if validate_layers(ppst):
            return ppst
    return None

def format_call_skill(layers: PPSTLayers, context: str = "") -> str:
    """Format a CALL SKILL block."""
    s = "[CALL SKILL]\n"
    for k, v in layers.to_dict().items():
        s += f"{k}: {v}\n"
    if context:
        s += f"CONTEXT: {context}\n"
    return s

# Example usage for agents
if __name__ == "__main__":
    layers = PPSTLayers(
        project="Build a new CLI data processing tool",
        program="src/data_processor.py",
        skill="CSV parser skill",
        target="Implement robust CSV reader with tests"
    )
    print("Validated:", validate_layers(layers))
    print(format_call_skill(layers, "Previous output: ..."))
