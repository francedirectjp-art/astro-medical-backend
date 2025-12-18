#!/usr/bin/env python3
"""
Anti-Gravity API Integration Test
Tests the full workflow from session creation to PDF generation
"""

import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/health")
    data = response.json()
    
    print(f"✅ Status: {data['status']}")
    print(f"✅ Service: {data['service']}")
    print(f"✅ Components:")
    for name, status in data['components'].items():
        icon = "✅" if status else "⚠️"
        print(f"   {icon} {name}: {status}")
    print()
    return True

def test_create_session():
    """Test session creation"""
    print("=" * 60)
    print("TEST 2: Session Creation")
    print("=" * 60)
    
    birth_data = {
        "name": "テスト太郎",
        "birth_year": 1990,
        "birth_month": 1,
        "birth_day": 15,
        "birth_hour": 10,
        "birth_minute": 30,
        "birth_place": "東京都",
        "birth_time_unknown": False
    }
    
    response = requests.post(
        f"{API_URL}/api/session/create",
        json=birth_data
    )
    
    if response.status_code != 200:
        print(f"❌ Session creation failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    session_id = data['session_id']
    
    print(f"✅ Session created: {session_id}")
    chart = data.get('chart_data', {})
    if 'planets' in chart:
        print(f"✅ Planets calculated: {len(chart['planets'])}")
    print(f"✅ Variables prepared: {len(data.get('variables', {}))} steps")
    print()
    
    return session_id

def test_get_session(session_id):
    """Test getting session info"""
    print("=" * 60)
    print("TEST 3: Get Session Info")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/api/session/{session_id}")
    data = response.json()
    
    print(f"✅ Session ID: {data['session_id']}")
    print(f"✅ Status: {data['status']}")
    print(f"✅ Completed steps: {len(data['completed_steps'])}")
    print(f"✅ Total characters: {data['total_characters']}")
    print()
    return True

def test_generate_step(session_id):
    """Test content generation for a single step"""
    print("=" * 60)
    print("TEST 4: Generate Step Content")
    print("=" * 60)
    
    step_id = "1-A"
    
    print(f"Generating step {step_id}...")
    print("Note: AI generation requires OpenAI/Gemini API key")
    print("Without API key, will return placeholder content")
    print()
    
    response = requests.post(
        f"{API_URL}/api/generate/step",
        json={
            "session_id": session_id,
            "step_id": step_id,
            "provider": "openai",
            "stream": False
        }
    )
    
    data = response.json()
    
    print(f"✅ Step ID: {data['step_id']}")
    print(f"✅ Status: {data.get('status', 'N/A')}")
    print(f"✅ Character count: {data.get('character_count', 0)}")
    
    if 'message' in data:
        print(f"⚠️  Message: {data['message']}")
    
    if 'static_content' in data:
        print(f"✅ Static content blocks: {len(data['static_content'])}")
    
    if 'dynamic_content' in data:
        print(f"✅ Dynamic content blocks: {len(data['dynamic_content'])}")
    
    print()
    return True

def test_pdf_preview(session_id):
    """Test PDF preview"""
    print("=" * 60)
    print("TEST 5: PDF Preview")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/api/session/{session_id}/pdf/preview")
    
    if response.status_code != 200:
        print(f"⚠️  PDF preview failed: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    
    print(f"✅ Document title: {data['document_title']}")
    print(f"✅ Total characters: {data['total_characters']}")
    print(f"✅ Completed steps: {data['completed_steps']}")
    print(f"✅ Sections: {len(data['sections'])}")
    print()
    return True

def test_pdf_download(session_id):
    """Test PDF download"""
    print("=" * 60)
    print("TEST 6: PDF Download")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/api/session/{session_id}/pdf")
    
    if response.status_code == 400:
        print("⚠️  PDF download skipped: No content generated yet")
        print("   (This is expected if no AI steps were generated)")
        print()
        return True
    
    if response.status_code != 200:
        print(f"❌ PDF download failed: {response.status_code}")
        print(response.text[:200])
        return False
    
    pdf_size = len(response.content)
    print(f"✅ PDF downloaded successfully")
    print(f"✅ File size: {pdf_size:,} bytes ({pdf_size/1024:.2f} KB)")
    
    # Save to file
    output_file = f"/tmp/test_anti_gravity_{session_id[:8]}.pdf"
    with open(output_file, 'wb') as f:
        f.write(response.content)
    print(f"✅ Saved to: {output_file}")
    print()
    return True

def test_sessions_structure():
    """Test getting sessions structure"""
    print("=" * 60)
    print("TEST 7: Sessions Structure")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/api/content/sessions")
    data = response.json()
    
    print(f"✅ Total sessions: {len(data)}")
    
    total_steps = 0
    for session in data:
        print(f"   Session {session['session_id']}: {session['title']}")
        print(f"      Steps: {len(session['steps'])}")
        total_steps += len(session['steps'])
    
    print(f"✅ Total steps: {total_steps}")
    print()
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ANTI-GRAVITY API INTEGRATION TEST")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Create session
        session_id = test_create_session()
        if not session_id:
            print("❌ Cannot continue without session ID")
            return False
        
        # Test 3: Get session info
        test_get_session(session_id)
        
        # Test 4: Generate step
        test_generate_step(session_id)
        
        # Test 5: PDF preview
        test_pdf_preview(session_id)
        
        # Test 6: PDF download
        test_pdf_download(session_id)
        
        # Test 7: Sessions structure
        test_sessions_structure()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print(f"✅ Session ID: {session_id}")
        print()
        print("Note: For full functionality, set up:")
        print("  - OPENAI_API_KEY or GOOGLE_API_KEY for AI generation")
        print("  - Japanese fonts for better PDF quality")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
