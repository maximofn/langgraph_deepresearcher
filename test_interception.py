#!/usr/bin/env python3
"""
Test script for message interception system

This script verifies that the message interceptor is working correctly
by simulating format_messages() calls and checking if events are captured.
"""

import sys
sys.path.append('src')

# IMPORTANTE: Importar el módulo, NO la función directamente
from langchain_core.messages import HumanMessage, SystemMessage
from front.message_interceptor import enable_interception
from front.event_tracker import get_tracker, reset_tracker

print("=" * 60)
print("Message Interception Test")
print("=" * 60)

# Habilitar interceptor ANTES de importar format_messages
print("\n1. Enabling message interception...")
enable_interception()

# AHORA importar el módulo para usar la función parchada
from utils import message_utils

# Reset tracker
reset_tracker()
tracker = get_tracker()

# Test 1: Scope Agent - Need clarification
print("\n2. Testing Scope Agent messages...")
print("-" * 60)
test_message_1 = HumanMessage(content="This is a test clarification message")
message_utils.format_messages([test_message_1], title="Scope Assistant - need clarification?")

# Test 2: Scope System Message
print("-" * 60)
test_message_2 = SystemMessage(content="No necesita aclaración")
message_utils.format_messages([test_message_2], title="Scope System Message")

# Test 3: Scope Research Brief
print("-" * 60)
test_message_3 = HumanMessage(content="Research brief content here...")
message_utils.format_messages([test_message_3], title="Scope Assistant - Research brief generated")

# Test 4: Supervisor
print("-" * 60)
test_message_4 = HumanMessage(content="Supervisor coordination message")
message_utils.format_messages([test_message_4], title="Supervisor Agent")

# Verificar eventos capturados
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

events = tracker.get_events()

print(f"\n✓ Total events captured: {len(events)}")

if len(events) == 0:
    print("\n❌ ERROR: No events were captured!")
    print("   The interceptor is not working correctly.")
    print("   Check that enable_interception() was called successfully.")
else:
    print("\n✓ SUCCESS: Events were captured!\n")
    for i, event in enumerate(events, 1):
        print(f"{i}. Event Type: {event.event_type.value}")
        print(f"   Title: {event.title}")
        print(f"   Content (first 80 chars): {event.content[:80]}...")
        print(f"   Is Intermediate: {event.is_intermediate}")
        print()

    # Expected results
    expected = 4
    if len(events) == expected:
        print(f"✓ All {expected} expected events were captured correctly!")
    else:
        print(f"⚠ Warning: Expected {expected} events but got {len(events)}")

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
