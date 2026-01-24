from typing import Dict, List, Literal
from pydantic import BaseModel, Field

Depth = Literal["quick", "standard", "deep"]

class Plan(BaseModel):
    categories: List[str] = Field(..., description="Subset of: bias, privacy, explainability, governance")
    depth: Dict[str, Depth] = Field(..., description="Depth per category")
    follow_up_questions: List[str] = Field(default_factory=list, description="Questions to clarify missing info")
