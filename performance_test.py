"""
Performance Testing Script for Anti-Gravity API
Tests API response times, throughput, and resource usage
"""

import asyncio
import time
import statistics
import json
from typing import List, Dict
import aiohttp
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

# Test data
TEST_BIRTH_DATA = {
    "name": "パフォーマンステスト太郎",
    "birth_date": "1990-05-15",
    "birth_time": "14:30",
    "prefecture": "東京都",
    "city": "渋谷区"
}

class PerformanceMetrics:
    def __init__(self):
        self.response_times = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def add_response_time(self, duration: float):
        self.response_times.append(duration)
    
    def add_error(self, error: str):
        self.errors.append(error)
    
    def get_statistics(self) -> Dict:
        if not self.response_times:
            return {"error": "No data collected"}
        
        return {
            "total_requests": len(self.response_times) + len(self.errors),
            "successful_requests": len(self.response_times),
            "failed_requests": len(self.errors),
            "success_rate": len(self.response_times) / (len(self.response_times) + len(self.errors)) * 100,
            "response_times": {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "stdev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
                "p95": sorted(self.response_times)[int(len(self.response_times) * 0.95)] if len(self.response_times) > 1 else self.response_times[0],
                "p99": sorted(self.response_times)[int(len(self.response_times) * 0.99)] if len(self.response_times) > 1 else self.response_times[0],
            },
            "throughput": len(self.response_times) / (self.end_time - self.start_time) if self.end_time and self.start_time else 0,
            "duration": self.end_time - self.start_time if self.end_time and self.start_time else 0
        }


async def test_health_check(session: aiohttp.ClientSession, metrics: PerformanceMetrics):
    """Test health check endpoint"""
    start = time.time()
    try:
        async with session.get(f"{API_BASE_URL}/health") as response:
            if response.status == 200:
                metrics.add_response_time(time.time() - start)
            else:
                metrics.add_error(f"Health check failed: {response.status}")
    except Exception as e:
        metrics.add_error(f"Health check error: {str(e)}")


async def test_session_creation(session: aiohttp.ClientSession, metrics: PerformanceMetrics):
    """Test session creation endpoint"""
    start = time.time()
    try:
        async with session.post(
            f"{API_BASE_URL}/api/session/create",
            json=TEST_BIRTH_DATA
        ) as response:
            if response.status == 200:
                metrics.add_response_time(time.time() - start)
                data = await response.json()
                return data.get("session_id")
            else:
                metrics.add_error(f"Session creation failed: {response.status}")
                return None
    except Exception as e:
        metrics.add_error(f"Session creation error: {str(e)}")
        return None


async def test_content_generation(session: aiohttp.ClientSession, session_id: str, metrics: PerformanceMetrics):
    """Test content generation endpoint"""
    start = time.time()
    try:
        async with session.post(
            f"{API_BASE_URL}/api/generate/step",
            json={
                "session_id": session_id,
                "step_id": "1-A"
            }
        ) as response:
            if response.status == 200:
                metrics.add_response_time(time.time() - start)
            else:
                metrics.add_error(f"Content generation failed: {response.status}")
    except Exception as e:
        metrics.add_error(f"Content generation error: {str(e)}")


async def test_pdf_generation(session: aiohttp.ClientSession, session_id: str, metrics: PerformanceMetrics):
    """Test PDF generation endpoint"""
    start = time.time()
    try:
        async with session.get(
            f"{API_BASE_URL}/api/session/{session_id}/pdf"
        ) as response:
            if response.status == 200:
                # Read the entire PDF to measure full response time
                pdf_data = await response.read()
                metrics.add_response_time(time.time() - start)
                return len(pdf_data)
            else:
                metrics.add_error(f"PDF generation failed: {response.status}")
                return 0
    except Exception as e:
        metrics.add_error(f"PDF generation error: {str(e)}")
        return 0


async def run_load_test(num_concurrent: int, num_iterations: int):
    """
    Run load test with concurrent requests
    
    Args:
        num_concurrent: Number of concurrent requests
        num_iterations: Number of iterations per concurrent worker
    """
    print(f"\n{'='*60}")
    print(f"LOAD TEST: {num_concurrent} concurrent users, {num_iterations} iterations each")
    print(f"{'='*60}\n")
    
    metrics = {
        "health": PerformanceMetrics(),
        "session": PerformanceMetrics(),
        "content": PerformanceMetrics(),
        "pdf": PerformanceMetrics()
    }
    
    async with aiohttp.ClientSession() as session:
        # Health check test
        print("Testing health check endpoint...")
        metrics["health"].start_time = time.time()
        health_tasks = [
            test_health_check(session, metrics["health"])
            for _ in range(num_concurrent * num_iterations)
        ]
        await asyncio.gather(*health_tasks)
        metrics["health"].end_time = time.time()
        
        # Session creation test
        print("Testing session creation endpoint...")
        metrics["session"].start_time = time.time()
        session_tasks = [
            test_session_creation(session, metrics["session"])
            for _ in range(num_concurrent * num_iterations)
        ]
        session_ids = await asyncio.gather(*session_tasks)
        metrics["session"].end_time = time.time()
        
        # Filter valid session IDs
        valid_session_ids = [sid for sid in session_ids if sid]
        
        if valid_session_ids:
            # Content generation test (use first session)
            print("Testing content generation endpoint...")
            metrics["content"].start_time = time.time()
            content_tasks = [
                test_content_generation(session, valid_session_ids[0], metrics["content"])
                for _ in range(min(num_concurrent, len(valid_session_ids)))
            ]
            await asyncio.gather(*content_tasks)
            metrics["content"].end_time = time.time()
            
            # PDF generation test (use first session)
            print("Testing PDF generation endpoint...")
            metrics["pdf"].start_time = time.time()
            pdf_sizes = []
            pdf_tasks = [
                test_pdf_generation(session, valid_session_ids[0], metrics["pdf"])
                for _ in range(min(num_concurrent, len(valid_session_ids)))
            ]
            pdf_sizes = await asyncio.gather(*pdf_tasks)
            metrics["pdf"].end_time = time.time()
            
            if pdf_sizes and any(pdf_sizes):
                avg_pdf_size = statistics.mean([s for s in pdf_sizes if s > 0])
                print(f"\nAverage PDF size: {avg_pdf_size / 1024:.2f} KB")
    
    return metrics


def print_metrics_report(metrics: Dict[str, PerformanceMetrics]):
    """Print formatted metrics report"""
    print(f"\n{'='*60}")
    print("PERFORMANCE TEST RESULTS")
    print(f"{'='*60}\n")
    
    for endpoint_name, metric in metrics.items():
        stats = metric.get_statistics()
        
        print(f"Endpoint: {endpoint_name.upper()}")
        print("-" * 60)
        
        if "error" in stats:
            print(f"  ❌ {stats['error']}\n")
            continue
        
        print(f"  Total Requests:      {stats['total_requests']}")
        print(f"  Successful:          {stats['successful_requests']} ({stats['success_rate']:.1f}%)")
        print(f"  Failed:              {stats['failed_requests']}")
        print(f"  Duration:            {stats['duration']:.2f}s")
        print(f"  Throughput:          {stats['throughput']:.2f} req/s")
        print()
        print("  Response Times (ms):")
        print(f"    Min:               {stats['response_times']['min'] * 1000:.2f}")
        print(f"    Max:               {stats['response_times']['max'] * 1000:.2f}")
        print(f"    Mean:              {stats['response_times']['mean'] * 1000:.2f}")
        print(f"    Median:            {stats['response_times']['median'] * 1000:.2f}")
        print(f"    Std Dev:           {stats['response_times']['stdev'] * 1000:.2f}")
        print(f"    95th Percentile:   {stats['response_times']['p95'] * 1000:.2f}")
        print(f"    99th Percentile:   {stats['response_times']['p99'] * 1000:.2f}")
        print()
        
        # Performance rating
        mean_ms = stats['response_times']['mean'] * 1000
        if mean_ms < 100:
            rating = "🟢 Excellent"
        elif mean_ms < 500:
            rating = "🟡 Good"
        elif mean_ms < 1000:
            rating = "🟠 Acceptable"
        else:
            rating = "🔴 Needs Improvement"
        
        print(f"  Performance Rating:  {rating}")
        print()


async def run_full_workflow_test():
    """Test complete workflow from session creation to PDF download"""
    print(f"\n{'='*60}")
    print("FULL WORKFLOW TEST")
    print(f"{'='*60}\n")
    
    workflow_times = {
        "session_creation": 0,
        "horoscope_calculation": 0,
        "content_generation": 0,
        "pdf_generation": 0
    }
    
    async with aiohttp.ClientSession() as session:
        # 1. Create session
        print("1. Creating session...")
        start = time.time()
        async with session.post(
            f"{API_BASE_URL}/api/session/create",
            json=TEST_BIRTH_DATA
        ) as response:
            if response.status != 200:
                print("❌ Session creation failed")
                return
            data = await response.json()
            session_id = data.get("session_id")
            workflow_times["session_creation"] = time.time() - start
            print(f"   ✅ Session created: {session_id}")
            print(f"   ⏱️  Time: {workflow_times['session_creation'] * 1000:.2f}ms\n")
        
        # 2. Generate content for first step
        print("2. Generating content (Step 1-A)...")
        start = time.time()
        async with session.post(
            f"{API_BASE_URL}/api/generate/step",
            json={"session_id": session_id, "step_id": "1-A"}
        ) as response:
            if response.status != 200:
                print("❌ Content generation failed")
                return
            data = await response.json()
            workflow_times["content_generation"] = time.time() - start
            print(f"   ✅ Content generated: {data.get('character_count', 0)} characters")
            print(f"   ⏱️  Time: {workflow_times['content_generation'] * 1000:.2f}ms\n")
        
        # 3. Generate PDF
        print("3. Generating PDF...")
        start = time.time()
        async with session.get(
            f"{API_BASE_URL}/api/session/{session_id}/pdf"
        ) as response:
            if response.status != 200:
                print("❌ PDF generation failed")
                return
            pdf_data = await response.read()
            workflow_times["pdf_generation"] = time.time() - start
            print(f"   ✅ PDF generated: {len(pdf_data) / 1024:.2f} KB")
            print(f"   ⏱️  Time: {workflow_times['pdf_generation'] * 1000:.2f}ms\n")
    
    # Summary
    total_time = sum(workflow_times.values())
    print("-" * 60)
    print("Workflow Summary:")
    print(f"  Total Time:          {total_time * 1000:.2f}ms ({total_time:.2f}s)")
    print(f"  Session Creation:    {workflow_times['session_creation'] * 1000:.2f}ms")
    print(f"  Content Generation:  {workflow_times['content_generation'] * 1000:.2f}ms")
    print(f"  PDF Generation:      {workflow_times['pdf_generation'] * 1000:.2f}ms")
    print()


async def main():
    """Main performance test runner"""
    print(f"\n{'='*60}")
    print("ANTI-GRAVITY API PERFORMANCE TEST")
    print(f"{'='*60}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_BASE_URL}")
    print(f"{'='*60}\n")
    
    # Test 1: Full workflow
    await run_full_workflow_test()
    
    # Test 2: Light load (5 concurrent users, 10 iterations each)
    metrics_light = await run_load_test(num_concurrent=5, num_iterations=10)
    print_metrics_report(metrics_light)
    
    # Test 3: Medium load (10 concurrent users, 20 iterations each)
    print("\n\n")
    metrics_medium = await run_load_test(num_concurrent=10, num_iterations=20)
    print_metrics_report(metrics_medium)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST COMPLETED")
    print(f"{'='*60}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Recommendations:")
    print("  - For production, aim for <500ms mean response time")
    print("  - Monitor memory usage during load tests")
    print("  - Consider Redis for session storage under heavy load")
    print("  - Implement caching for static content")
    print("  - Use CDN for PDF delivery")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError running tests: {e}")
