import os
import time
import shutil
import json
from pathlib import Path

from bananalyzer.memory.store import MemoryStore
from bananalyzer.privacy import check_before_persistence
from bananalyzer.memory.summarizer import generate_session_summary, should_skip_update, periodic_memory_update
from bananalyzer.memory.retrieval import retrieve_memory_context
from bananalyzer.constants import DATA_DIR, MEMORY_DIR, LOGS_DIR
from bananalyzer.config import load_settings_safe, get_config_paths

def print_scenario(name):
    print(f"\n{'='*50}\nRunning Scenario: {name}\n{'-'*50}")

def clear_memory():
    if MEMORY_DIR.exists():
        shutil.rmtree(MEMORY_DIR)

def test_scenario_1():
    print_scenario("Scenario 1: Memory Store Initialization and Degraded Mode")
    clear_memory()
    
    # 1. Initialize
    store = MemoryStore()
    print(f"memory.md exists: {(MEMORY_DIR / 'memory.md').exists()}")
    print(f"session_summary.md exists: {(MEMORY_DIR / 'session_summary.md').exists()}")
    print(f"banana_debt.json exists: {(MEMORY_DIR / 'banana_debt.json').exists()}")
    
    # 2. Recreate missing
    (MEMORY_DIR / 'memory.md').unlink()
    print(f"Deleted memory.md. Reading goals...")
    goals = store.read_memory()
    print(f"Goals read (should be empty): '{goals}'")
    print(f"memory.md recreated: {(MEMORY_DIR / 'memory.md').exists()}")
    
    # 3. Simulate OSError on write
    print("Simulating OSError on write (making directory read-only temporarily)...")
    original_write = Path.write_text
    def raise_oserror(*args, **kwargs):
        raise OSError("Simulated Permission Denied")
    Path.write_text = raise_oserror
    
    try:
        store.add_goal("This should fail gracefully")
        print(f"Store available status after error: {store.available}")
    finally:
        Path.write_text = original_write

def test_scenario_2():
    print_scenario("Scenario 2: Markdown Section Appending and Privacy Filtering")
    store = MemoryStore()
    
    print("Adding goal and mistake...")
    store.add_goal("Test goal 1")
    store.record_mistake("Test mistake 1")
    
    content = (MEMORY_DIR / 'memory.md').read_text(encoding='utf-8')
    print("memory.md content:")
    print(content)
    
    print("Attempting to save oversized string...")
    oversized = "A" * 1000
    store.add_goal(oversized)
    
    print("Checking if oversized string is in memory.md...")
    new_content = (MEMORY_DIR / 'memory.md').read_text(encoding='utf-8')
    if oversized in new_content:
        print("FAIL: Oversized string was saved!")
    else:
        print("PASS: Oversized string was blocked.")

def test_scenario_3():
    print_scenario("Scenario 3: Periodic Summarization and Bounded Retrieval")
    store = MemoryStore()
    store.add_goal("Learn Python")
    store.record_progress("Wrote some tests")
    
    print("Retrieving memory context...")
    context = retrieve_memory_context(store, "coding")
    print("Retrieved Context:")
    print(context)
    
    print("Running periodic summarization skip check...")
    
    # Should be False initially because we have goals/progress
    skip = should_skip_update(store, "", "coding")
    print(f"Should skip update initially: {skip}")
    
def test_scenario_4():
    print_scenario("Scenario 4: Identity Inspection and Sync Defaults")
    
    paths = get_config_paths()
    print("Config Paths:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
        
    settings = load_settings_safe()
    print(f"\nSync Enabled: {settings.sync_enabled}")

if __name__ == "__main__":
    print("Starting Manual Test Execution Simulation...")
    test_scenario_1()
    test_scenario_2()
    test_scenario_3()
    test_scenario_4()
    print("\n" + "="*50)
    print("All Scenarios Executed Successfully.")
