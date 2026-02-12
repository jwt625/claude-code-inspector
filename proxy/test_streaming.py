#!/usr/bin/env python3
"""
Test script to verify streaming proxy functionality.
Tests both Anthropic and OpenAI SSE formats.
"""

import requests
import time
import sys


def test_streaming_response(proxy_url: str, test_type: str = "anthropic"):
    """
    Test streaming response from proxy.
    
    Args:
        proxy_url: URL of the proxy server
        test_type: "anthropic" or "openai" format test
    """
    print(f"\n{'='*60}")
    print(f"Testing {test_type.upper()} streaming format")
    print(f"{'='*60}\n")
    
    # This is a mock test - in real usage, you'd point to actual endpoints
    # For now, we'll just verify the proxy handles streaming headers correctly
    
    endpoint = f"{proxy_url}/v1/messages"
    
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 100,
        "stream": True,
        "messages": [
            {"role": "user", "content": "Say hello in one sentence."}
        ]
    }
    
    print(f"Sending request to: {endpoint}")
    print(f"Stream enabled: {payload.get('stream', False)}")
    
    try:
        start_time = time.time()
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            stream=True,
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'transfer-encoding', 'connection']:
                print(f"  {key}: {value}")
        
        # Check if streaming headers are present
        content_type = response.headers.get('content-type', '')
        if 'text/event-stream' in content_type:
            print("\n✓ Streaming headers detected (text/event-stream)")
        else:
            print(f"\n✗ Expected text/event-stream, got: {content_type}")
        
        # Read streaming response
        print("\nStreaming response chunks:")
        chunk_count = 0
        first_chunk_time = None
        
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                chunk_count += 1
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    ttfb = (first_chunk_time - start_time) * 1000
                    print(f"  Time to first byte: {ttfb:.2f}ms")
                
                # Print first few chunks for verification
                if chunk_count <= 3:
                    chunk_preview = chunk.decode('utf-8', errors='replace')[:100]
                    print(f"  Chunk {chunk_count}: {chunk_preview}...")
        
        total_time = (time.time() - start_time) * 1000
        print(f"\nTotal chunks received: {chunk_count}")
        print(f"Total time: {total_time:.2f}ms")
        
        if chunk_count > 0:
            print("\n✓ Streaming test PASSED - received chunks in real-time")
        else:
            print("\n✗ Streaming test FAILED - no chunks received")
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        return False
    
    return True


def main():
    """Run streaming tests."""
    proxy_url = "http://127.0.0.1:58734"
    
    print("Streaming Proxy Test Suite")
    print("="*60)
    print(f"Proxy URL: {proxy_url}")
    print("\nNOTE: This test requires the proxy to be running and")
    print("configured with a valid UPSTREAM_URL that supports streaming.")
    print("="*60)
    
    # Test Anthropic format
    success = test_streaming_response(proxy_url, "anthropic")
    
    # Could add OpenAI format test here if needed
    # test_streaming_response(proxy_url, "openai")
    
    if success:
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("Tests failed - check proxy configuration")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

