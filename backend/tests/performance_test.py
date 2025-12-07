"""
Nashama Vision - Performance Testing Script
Simple load testing for critical API endpoints

This is a standalone performance testing script, not a unit test.
Run it directly: python tests/performance_test.py
"""
import pytest

# Skip this file when running pytest - it's meant to be run standalone
pytestmark = pytest.mark.skip(reason="Performance test - run standalone with 'python tests/performance_test.py'")

import time
import statistics
import asyncio
import httpx
from typing import List, Dict

# Configuration
BASE_URL = "http://localhost:8000"
NUM_REQUESTS = 50
TIMEOUT = 30.0


async def test_endpoint(client: httpx.AsyncClient, method: str, url: str, payload: dict = None) -> Dict:
    """Test a single endpoint and measure response time"""
    start = time.time()
    try:
        if method == "GET":
            response = await client.get(url, timeout=TIMEOUT)
        else:
            response = await client.post(url, json=payload, timeout=TIMEOUT)
        
        elapsed = time.time() - start
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "elapsed": elapsed,
            "error": None
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "success": False,
            "status_code": 0,
            "elapsed": elapsed,
            "error": str(e)
        }


async def load_test_endpoint(endpoint: str, method: str = "GET", payload: dict = None, num_requests: int = NUM_REQUESTS) -> Dict:
    """Run load test on a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Requests: {num_requests}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        tasks = [test_endpoint(client, method, endpoint, payload) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    # Calculate statistics
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        response_times = [r["elapsed"] for r in successful]
        
        stats = {
            "endpoint": endpoint,
            "method": method,
            "total_requests": num_requests,
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / num_requests * 100,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": statistics.median(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
        }
    else:
        stats = {
            "endpoint": endpoint,
            "method": method,
            "total_requests": num_requests,
            "successful": 0,
            "failed": num_requests,
            "success_rate": 0,
            "avg_response_time": 0,
            "min_response_time": 0,
            "max_response_time": 0,
            "median_response_time": 0,
            "p95_response_time": 0,
        }
    
    # Print results
    print(f"\nResults:")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Successful: {stats['successful']} | Failed: {stats['failed']}")
    print(f"\nResponse Times (seconds):")
    print(f"  Average: {stats['avg_response_time']:.3f}s")
    print(f"  Median:  {stats['median_response_time']:.3f}s")
    print(f"  Min:     {stats['min_response_time']:.3f}s")
    print(f"  Max:     {stats['max_response_time']:.3f}s")
    print(f"  P95:     {stats['p95_response_time']:.3f}s")
    
    if failed:
        print(f"\nErrors:")
        error_counts = {}
        for r in failed:
            error_type = r.get("error") or f"HTTP {r['status_code']}"
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        for error, count in error_counts.items():
            print(f"  {error}: {count}")
    
    return stats


async def main():
    """Run performance tests on critical endpoints"""
    print("\n" + "="*60)
    print("Nashama Vision - Performance Testing")
    print("="*60)
    
    # Test a real match ID (you may need to create one first)
    # For this test, we'll use a placeholder that should return 404 or handle gracefully
    test_match_id = "00000000-0000-0000-0000-000000000000"
    
    # Define test scenarios
    tests = [
        {
            "endpoint": "/api/v1/matches",
            "method": "GET",
            "num_requests": NUM_REQUESTS
        },
        {
            "endpoint": f"/api/v1/matches/{test_match_id}",
            "method": "GET",
            "num_requests": NUM_REQUESTS // 2
        },
        {
            "endpoint": f"/api/v1/metrics/match/{test_match_id}",
            "method": "GET",
            "num_requests": NUM_REQUESTS // 2
        },
        {
            "endpoint": f"/api/v1/replay/match/{test_match_id}/timeline",
            "method": "GET",
            "num_requests": NUM_REQUESTS // 2
        },
        {
            "endpoint": "/api/v1/assistant/query",
            "method": "POST",
            "payload": {
                "query": "Who covered the most distance?",
                "match_id": test_match_id
            },
            "num_requests": 20  # Fewer requests for LLM endpoint
        }
    ]
    
    all_stats = []
    
    for test in tests:
        stats = await load_test_endpoint(
            test["endpoint"],
            test.get("method", "GET"),
            test.get("payload"),
            test.get("num_requests", NUM_REQUESTS)
        )
        all_stats.append(stats)
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\n{'Endpoint':<50} {'Success %':<12} {'Avg (s)':<10}")
    print("-" * 72)
    
    for stats in all_stats:
        endpoint = f"{stats['method']} {stats['endpoint']}"
        if len(endpoint) > 48:
            endpoint = endpoint[:45] + "..."
        print(f"{endpoint:<50} {stats['success_rate']:>6.1f}%      {stats['avg_response_time']:>6.3f}s")
    
    print("\n" + "="*60)
    print("Performance testing complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
