#!/usr/bin/env python3
"""
Test script for the Research Agent.

Run example queries and validate output structure.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_basic_query():
    """Test basic research query."""
    print("\n" + "="*60)
    print("TEST 1: Basic Query (AI Safety)")
    print("="*60)
    
    cmd = [
        "python3", "research.py",
        "--topic", "What's the latest in AI safety research?",
        "--keywords", "alignment, AGI, safety",
        "--depth", "2",
        "--format", "pretty"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        validate_output(data)
        print("✅ Test passed!")
        print_summary(data)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON output: {e}")
        return False


def test_different_depth():
    """Test different depth levels."""
    print("\n" + "="*60)
    print("TEST 2: Different Depth Levels")
    print("="*60)
    
    for depth in [1, 2, 3]:
        print(f"\nTesting depth level {depth}...")
        
        cmd = [
            "python3", "research.py",
            "--topic", "Climate change impacts",
            "--depth", str(depth)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ❌ Depth {depth} failed: {result.stderr}")
            return False
        
        try:
            data = json.loads(result.stdout)
            validate_output(data)
            source_count = len(data.get('sources', []))
            print(f"  ✅ Depth {depth}: {source_count} sources analyzed")
        except json.JSONDecodeError as e:
            print(f"  ❌ Depth {depth} invalid JSON: {e}")
            return False
    
    return True


def test_output_file():
    """Test file output."""
    print("\n" + "="*60)
    print("TEST 3: File Output")
    print("="*60)
    
    output_file = Path("/tmp/test_research_output.json")
    
    cmd = [
        "python3", "research.py",
        "--topic", "Machine learning trends",
        "--depth", "1",
        "--output", str(output_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        return False
    
    if not output_file.exists():
        print(f"❌ Output file not created: {output_file}")
        return False
    
    try:
        with open(output_file) as f:
            data = json.load(f)
        validate_output(data)
        print(f"✅ Output file created successfully")
        print(f"  File: {output_file}")
        print(f"  Size: {output_file.stat().st_size} bytes")
        output_file.unlink()  # Clean up
        return True
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Failed to read output file: {e}")
        return False


def validate_output(data):
    """Validate research output structure."""
    
    required_keys = {
        'topic', 'keywords', 'timestamp', 'depth',
        'key_findings', 'sources', 'credibility_analysis',
        'consensus', 'contradictions', 'metadata'
    }
    
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"Missing required keys: {missing}")
    
    # Validate types
    assert isinstance(data['topic'], str), "topic must be string"
    assert isinstance(data['keywords'], list), "keywords must be list"
    assert isinstance(data['depth'], int), "depth must be int"
    assert isinstance(data['key_findings'], list), "key_findings must be list"
    assert isinstance(data['sources'], list), "sources must be list"
    assert isinstance(data['credibility_analysis'], dict), "credibility_analysis must be dict"
    assert isinstance(data['consensus'], str), "consensus must be string"
    assert isinstance(data['contradictions'], list), "contradictions must be list"


def print_summary(data):
    """Print a summary of research results."""
    
    print("\n📊 RESEARCH SUMMARY")
    print("-" * 60)
    
    print(f"\n📌 Topic: {data['topic']}")
    if data['keywords']:
        print(f"🔑 Keywords: {', '.join(data['keywords'])}")
    
    print(f"\n📚 Sources: {len(data['sources'])} analyzed")
    if data['sources']:
        print("  Top sources (by credibility):")
        for i, source in enumerate(data['sources'][:3], 1):
            print(f"    {i}. {source['domain']} ({source['credibility_score']})")
    
    print(f"\n💡 Key Findings: {len(data['key_findings'])}")
    if data['key_findings']:
        print("  Top findings:")
        for i, finding in enumerate(data['key_findings'][:2], 1):
            print(f"    {i}. {finding['statement'][:80]}...")
    
    cred = data['credibility_analysis']
    print(f"\n📈 Credibility Analysis:")
    print(f"  Average: {cred.get('average_score', 'N/A')}")
    print(f"  High credibility sources: {cred.get('high_credibility_count', 0)}")
    print(f"  Medium credibility sources: {cred.get('medium_credibility_count', 0)}")
    print(f"  Low credibility sources: {cred.get('low_credibility_count', 0)}")
    
    print(f"\n🤝 Consensus: {data['consensus']}")
    
    if data['contradictions']:
        print(f"\n⚠️  Contradictions: {len(data['contradictions'])}")
        for i, contra in enumerate(data['contradictions'][:1], 1):
            print(f"    {i}. {contra['claim_1'][:60]}... ({contra['severity']})")
    else:
        print("\n✅ No major contradictions detected")


def main():
    """Run all tests."""
    
    print("\n🧪 RESEARCH AGENT TEST SUITE")
    print("=" * 60)
    
    # Check if research.py exists
    if not Path("research.py").exists():
        print("❌ research.py not found in current directory")
        return 1
    
    tests = [
        ("Basic Query", test_basic_query),
        ("Depth Levels", test_different_depth),
        ("File Output", test_output_file),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ Test {name} failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, passed_test in results:
        status = "✅" if passed_test else "❌"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
