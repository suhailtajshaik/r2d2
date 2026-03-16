"""
feed_yoda.py — Feed PDFs directly to Yoda's knowledge base.
Works without an Anthropic API key using local extraction.
Run: python3 feed_yoda.py
"""
import sys, os, datetime
sys.path.insert(0, os.path.dirname(__file__))

from learner.resource_parser import ResourceParser
from learner.local_extractor import extract_knowledge_local
from learner.knowledge_updater import KnowledgeUpdater

RESOURCES = [
    ("resources/reading-list.pdf", "VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)"),
    ("resources/vl-jepa-learning-path.pdf", "VL-JEPA Learning Path — Senior ML Researcher structured guide"),
]

def feed():
    parser = ResourceParser()
    updater = KnowledgeUpdater()
    
    for path, label in RESOURCES:
        if not os.path.exists(path):
            print(f"[SKIP] {path} not found")
            continue

        print(f"\n{'='*60}")
        print(f"[FEEDING] {label}")
        print(f"{'='*60}")
        
        # Parse PDF
        parsed = parser.parse_pdf(path)
        content = parsed["content"]
        print(f"  Parsed: {len(content):,} characters")

        # Extract knowledge locally
        knowledge = extract_knowledge_local(content, label)
        
        # Show what was found
        for cat in ["concepts", "architecture", "training", "datasets"]:
            items = knowledge.get(cat, [])
            if items:
                print(f"\n  [{cat.upper()}] {len(items)} insights found")
                for item in items[:2]:
                    print(f"    • {item[:100]}...")

        if knowledge.get("code_improvements"):
            print(f"\n  [CODE IMPROVEMENTS] {len(knowledge['code_improvements'])} suggestions")
            for imp in knowledge["code_improvements"]:
                print(f"    → {imp}")

        # Update knowledge base
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        for cat in ["concepts", "architecture", "training", "datasets"]:
            items = knowledge.get(cat, [])
            if not items:
                continue
            kfile = f"knowledge/{cat if cat != 'training' else 'training_insights'}.md"
            if cat == "training":
                kfile = "knowledge/training_insights.md"
            
            with open(kfile, "a") as f:
                f.write(f"\n\n## [{timestamp}] Source: {label}\n\n")
                for item in items:
                    f.write(f"- {item}\n")
        
        # Update evolution log
        with open("knowledge/evolution_log.md", "a") as f:
            f.write(f"\n\n## [{timestamp}] Learning Event\n")
            f.write(f"**Source:** {label}\n")
            f.write(f"**Content size:** {len(content):,} chars\n")
            f.write(f"**Concepts extracted:** {len(knowledge.get('concepts',[]))}\n")
            f.write(f"**Architecture insights:** {len(knowledge.get('architecture',[]))}\n")
            f.write(f"**Code improvements suggested:** {len(knowledge.get('code_improvements',[]))}\n")
            if knowledge.get("code_improvements"):
                f.write(f"**Improvements:**\n")
                for imp in knowledge["code_improvements"]:
                    f.write(f"- {imp}\n")

        print(f"\n  ✅ Knowledge base updated")

    print(f"\n{'='*60}")
    print("✅ Yoda has been fed. Knowledge base updated.")
    print("Run: python3 agent.py status")
    print(f"{'='*60}")

if __name__ == "__main__":
    feed()
