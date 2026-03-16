"""
Learner module for VL-JEPA autonomous learning and code evolution.

Provides tools to parse research resources, extract knowledge,
update a persistent knowledge base, and evolve the codebase
based on accumulated insights.
"""

from learner.resource_parser import ResourceParser
from learner.knowledge_extractor import KnowledgeExtractor
from learner.knowledge_updater import KnowledgeUpdater
from learner.code_evolver import CodeEvolver
from learner.evolution_tracker import EvolutionTracker

__all__ = [
    "ResourceParser",
    "KnowledgeExtractor",
    "KnowledgeUpdater",
    "CodeEvolver",
    "EvolutionTracker",
]
