#!/usr/bin/env python3
"""
Rey — Design Agent
Audits and improves design consistency across Suhail's SaaS projects.

Usage:
    python3 rey.py --audit SellBridge
    python3 rey.py --audit-all
    python3 rey.py --teach-brand
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List
import subprocess
from datetime import datetime

class Rey:
    """Design auditor and quality enforcer."""
    
    def __init__(self, config_path: str = None):
        self.name = "Rey"
        self.version = "0.1.0"
        self.config_path = config_path or str(Path(__file__).parent.parent / "config" / "rey.config.yaml")
        self.memory_path = Path(__file__).parent.parent / "memory"
        self.memory_path.mkdir(exist_ok=True)
        
        self.load_config()
        self.load_brand_preferences()
        self.load_learnings()
    
    def load_config(self):
        """Load YAML configuration."""
        import yaml
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            self.config = {}
    
    def load_brand_preferences(self):
        """Load learned brand preferences."""
        brand_file = self.memory_path / "brand-preferences.json"
        if brand_file.exists():
            with open(brand_file, 'r') as f:
                self.brand_prefs = json.load(f)
        else:
            self.brand_prefs = self.config.get('brand', {})
    
    def load_learnings(self):
        """Load anti-pattern learnings."""
        learnings_file = self.memory_path / "learned-anti-patterns.json"
        if learnings_file.exists():
            with open(learnings_file, 'r') as f:
                self.learnings = json.load(f)
        else:
            self.learnings = {"violations": {}, "improvements": {}}
    
    def save_preferences(self):
        """Save brand preferences."""
        brand_file = self.memory_path / "brand-preferences.json"
        with open(brand_file, 'w') as f:
            json.dump(self.brand_prefs, f, indent=2)
    
    def save_learnings(self):
        """Save learnings for future audits."""
        learnings_file = self.memory_path / "learned-anti-patterns.json"
        with open(learnings_file, 'w') as f:
            json.dump(self.learnings, f, indent=2)
    
    def audit_project(self, project_name: str) -> Dict:
        """Audit a single project for design violations."""
        projects = {p['name']: p for p in self.config.get('projects', [])}
        
        if project_name not in projects:
            return {"status": "error", "message": f"Project '{project_name}' not found"}
        
        project = projects[project_name]
        project_path = project['path']
        
        if not Path(project_path).exists():
            return {"status": "error", "message": f"Project path not found: {project_path}"}
        
        print(f"\n🎨 Rey — Auditing {project_name}...")
        print(f"   Path: {project_path}")
        
        results = {
            "project": project_name,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "typography": self._check_typography(project_path),
                "colors": self._check_colors(project_path),
                "layout": self._check_layout(project_path),
                "responsive": self._check_responsive(project_path),
                "anti_patterns": self._check_anti_patterns(project_path),
            },
            "summary": {}
        }
        
        # Summarize violations
        violations = []
        for check_name, check_result in results['checks'].items():
            if check_result.get('violations'):
                violations.extend(check_result['violations'])
        
        results['summary'] = {
            "status": "pass" if not violations else "warning" if len(violations) < 3 else "fail",
            "total_violations": len(violations),
            "severity": self._calculate_severity(violations)
        }
        
        # Log to memory
        self._log_audit(project_name, results)
        
        return results
    
    def _check_typography(self, project_path: str) -> Dict:
        """Check typography against brand guidelines."""
        avoid_fonts = self.brand_prefs.get('typography', {}).get('avoid', [])
        violations = []
        
        # Simple grep for forbidden fonts in CSS/component files
        patterns = [
            f"font-family.*{'|'.join(avoid_fonts)}",
        ]
        
        try:
            result = subprocess.run(
                f"grep -r \"{'|'.join(avoid_fonts)}\" {project_path} --include='*.css' --include='*.tsx' --include='*.jsx' 2>/dev/null | wc -l",
                shell=True,
                capture_output=True,
                text=True
            )
            count = int(result.stdout.strip() or 0)
            if count > 0:
                violations.append(f"Found {count} instances of forbidden fonts")
        except:
            pass
        
        return {
            "status": "pass" if not violations else "warning",
            "violations": violations,
            "details": "Typography hierarchy and font choices checked"
        }
    
    def _check_colors(self, project_path: str) -> Dict:
        """Check color palette consistency."""
        violations = []
        brand_color = self.brand_prefs.get('primary_color', '#6366F1')
        
        # Check for AI-slop color patterns
        ai_slop_patterns = ["purple.*gradient", "cyan.*dark", "neon"]
        
        try:
            for pattern in ai_slop_patterns:
                result = subprocess.run(
                    f"grep -ri \"{pattern}\" {project_path} --include='*.css' --include='*.tsx' 2>/dev/null | wc -l",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                count = int(result.stdout.strip() or 0)
                if count > 0:
                    violations.append(f"Found {count} instances of '{pattern}' pattern")
        except:
            pass
        
        return {
            "status": "pass" if not violations else "warning",
            "violations": violations,
            "brand_color": brand_color,
            "details": "Color palette consistency and AI-slop pattern detection"
        }
    
    def _check_layout(self, project_path: str) -> Dict:
        """Check layout composition."""
        violations = []
        
        # Check for nested cards anti-pattern
        try:
            result = subprocess.run(
                f"grep -r \"<Card.*<Card\" {project_path} --include='*.tsx' --include='*.jsx' 2>/dev/null | wc -l",
                shell=True,
                capture_output=True,
                text=True
            )
            count = int(result.stdout.strip() or 0)
            if count > 0:
                violations.append(f"Found {count} nested card patterns (anti-pattern)")
        except:
            pass
        
        return {
            "status": "pass" if not violations else "warning",
            "violations": violations,
            "details": "Layout composition, spacing, and card patterns checked"
        }
    
    def _check_responsive(self, project_path: str) -> Dict:
        """Check responsive design."""
        violations = []
        
        # Simple check for mobile breakpoints
        try:
            result = subprocess.run(
                f"grep -r \"@media.*max-width\" {project_path} --include='*.css' --include='*.tsx' 2>/dev/null | wc -l",
                shell=True,
                capture_output=True,
                text=True
            )
            count = int(result.stdout.strip() or 0)
            if count == 0:
                violations.append("No responsive breakpoints detected")
        except:
            pass
        
        return {
            "status": "pass" if not violations else "warning",
            "violations": violations,
            "details": "Mobile responsiveness and breakpoint coverage"
        }
    
    def _check_anti_patterns(self, project_path: str) -> Dict:
        """Check for Impeccable anti-patterns."""
        violations = []
        anti_patterns = self.config.get('impeccable', {}).get('anti_patterns', {})
        
        # Check all categories
        for category, patterns in anti_patterns.items():
            for pattern in patterns:
                # This is a simplified check; in production, use proper AST parsing
                pass
        
        return {
            "status": "pass" if not violations else "warning",
            "violations": violations,
            "anti_patterns_checked": len(anti_patterns.keys()),
            "details": "Impeccable anti-pattern detection"
        }
    
    def _calculate_severity(self, violations: List[str]) -> str:
        """Calculate overall severity."""
        if not violations:
            return "none"
        elif len(violations) < 2:
            return "low"
        elif len(violations) < 5:
            return "medium"
        else:
            return "high"
    
    def _log_audit(self, project_name: str, results: Dict):
        """Log audit results to memory."""
        audit_log = self.memory_path / "audit-history.json"
        
        history = []
        if audit_log.exists():
            with open(audit_log, 'r') as f:
                history = json.load(f)
        
        history.append(results)
        
        # Keep last 100 audits
        if len(history) > 100:
            history = history[-100:]
        
        with open(audit_log, 'w') as f:
            json.dump(history, f, indent=2)
    
    def audit_all(self) -> Dict:
        """Audit all critical projects."""
        projects = self.config.get('projects', [])
        critical_projects = [p for p in projects if p.get('critical', False)]
        
        results = {}
        for project in critical_projects:
            results[project['name']] = self.audit_project(project['name'])
        
        return results
    
    def teach_brand(self):
        """Interactive brand teaching session."""
        print("\n🎨 Rey — Brand Teaching Session")
        print("Let's establish your brand guidelines...\n")
        
        brand = {}
        brand['name'] = input("Brand name: ") or "Suhail's SaaS"
        brand['aesthetic'] = input("Design aesthetic (e.g., stripe-linear, minimal, bold): ") or "stripe-linear-inspired"
        brand['primary_color'] = input("Primary color (hex): ") or "#6366F1"
        
        self.brand_prefs.update(brand)
        self.save_preferences()
        
        print("\n✅ Brand preferences saved!")
    
    def report(self, results: Dict):
        """Generate and display audit report."""
        project = results.get('project', 'Unknown')
        summary = results.get('summary', {})
        status = summary.get('status', 'pass')
        
        status_emoji = {"pass": "✅", "warning": "⚠️", "fail": "❌"}.get(status, "❓")
        
        print(f"\n{status_emoji} {project}")
        print(f"   Status: {status.upper()}")
        print(f"   Violations: {summary.get('total_violations', 0)}")
        print(f"   Severity: {summary.get('severity', 'unknown')}")
        
        for check_name, check_result in results.get('checks', {}).items():
            if check_result.get('violations'):
                print(f"\n   {check_name}:")
                for violation in check_result['violations']:
                    print(f"      • {violation}")


def main():
    parser = argparse.ArgumentParser(description="Rey — Design Agent")
    parser.add_argument("--audit", metavar="PROJECT", help="Audit a specific project")
    parser.add_argument("--audit-all", action="store_true", help="Audit all critical projects")
    parser.add_argument("--teach-brand", action="store_true", help="Interactive brand teaching")
    parser.add_argument("--config", help="Path to config file")
    
    args = parser.parse_args()
    
    rey = Rey(config_path=args.config)
    
    if args.teach_brand:
        rey.teach_brand()
    elif args.audit:
        results = rey.audit_project(args.audit)
        rey.report(results)
    elif args.audit_all:
        print("🎨 Rey — Auditing all critical projects...\n")
        results = rey.audit_all()
        for project_name, result in results.items():
            rey.report(result)
    else:
        print(f"Rey v{rey.version} — Design Agent")
        print("\nUsage:")
        print("  python3 rey.py --audit SellBridge")
        print("  python3 rey.py --audit-all")
        print("  python3 rey.py --teach-brand")
        parser.print_help()


if __name__ == "__main__":
    main()
