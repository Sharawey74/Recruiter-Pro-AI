"""
Performance Tests - Load Testing and Benchmarking

Tests system performance under various load conditions:
- Response time benchmarks
- Throughput testing
- Load testing (concurrent requests)
- Memory usage profiling
- Batch processing performance
"""

import pytest
import time
import statistics
from fastapi.testclient import TestClient
import concurrent.futures
from pathlib import Path

from src.api import app


@pytest.mark.performance
@pytest.mark.slow
class TestAPIPerformance:
    """Performance and load testing for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """API test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_resume(self):
        """Standard resume for benchmarking"""
        return {
            "skills": "Python, Machine Learning, SQL, AWS",
            "experience_years": 5,
            "education": "Masters",
            "certifications": "AWS Certified",
            "projects_count": 10,
            "current_role": "Senior Engineer",
            "expected_salary": 120000
        }
    
    @pytest.mark.performance
    def test_single_resume_response_time(self, client, sample_resume):
        """Benchmark single resume scoring response time"""
        response_times = []
        
        # Warm-up request
        client.post("/api/v1/score", json=sample_resume)
        
        # Measure 10 requests
        for _ in range(10):
            start = time.time()
            response = client.post("/api/v1/score", json=sample_resume)
            end = time.time()
            
            if response.status_code == 200:
                response_times.append((end - start) * 1000)  # Convert to ms
        
        if response_times:
            avg_time = statistics.mean(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
            
            print(f"\nSingle Resume Performance:")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  P95: {p95_time:.2f}ms")
            print(f"  Min: {min(response_times):.2f}ms")
            print(f"  Max: {max(response_times):.2f}ms")
            
            # Should respond within 500ms (p95)
            assert p95_time < 500, f"P95 response time {p95_time:.2f}ms exceeds 500ms threshold"
    
    @pytest.mark.performance
    def test_batch_10_response_time(self, client, sample_resume):
        """Benchmark batch processing (10 resumes)"""
        batch_payload = {
            "resumes": [sample_resume.copy() for _ in range(10)]
        }
        
        response_times = []
        
        # Warm-up
        client.post("/api/v1/batch", json=batch_payload)
        
        # Measure 5 requests
        for _ in range(5):
            start = time.time()
            response = client.post("/api/v1/batch", json=batch_payload)
            end = time.time()
            
            if response.status_code == 200:
                response_times.append((end - start) * 1000)
        
        if response_times:
            avg_time = statistics.mean(response_times)
            
            print(f"\nBatch (10 resumes) Performance:")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Per resume: {avg_time/10:.2f}ms")
            
            # Should process 10 resumes within 1 second
            assert avg_time < 1000, f"Batch processing {avg_time:.2f}ms exceeds 1s threshold"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_batch_100_response_time(self, client, sample_resume):
        """Benchmark batch processing (100 resumes - maximum)"""
        batch_payload = {
            "resumes": [sample_resume.copy() for _ in range(100)]
        }
        
        start = time.time()
        response = client.post("/api/v1/batch", json=batch_payload)
        end = time.time()
        
        if response.status_code == 200:
            response_time = (end - start) * 1000
            
            print(f"\nBatch (100 resumes) Performance:")
            print(f"  Total: {response_time:.2f}ms")
            print(f"  Per resume: {response_time/100:.2f}ms")
            
            # Should complete within 5 seconds
            assert response_time < 5000, f"Batch 100 processing {response_time:.2f}ms exceeds 5s threshold"
    
    @pytest.mark.performance
    def test_health_check_response_time(self, client):
        """Benchmark health check endpoint"""
        response_times = []
        
        for _ in range(20):
            start = time.time()
            response = client.get("/api/v1/health")
            end = time.time()
            
            response_times.append((end - start) * 1000)
        
        avg_time = statistics.mean(response_times)
        
        print(f"\nHealth Check Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        
        # Health check should be very fast (<50ms)
        assert avg_time < 50, f"Health check {avg_time:.2f}ms exceeds 50ms threshold"
    
    @pytest.mark.performance
    def test_concurrent_10_requests(self, client, sample_resume):
        """Test 10 concurrent requests"""
        num_requests = 10
        
        def make_request():
            start = time.time()
            response = client.post("/api/v1/score", json=sample_resume)
            end = time.time()
            return {
                'status': response.status_code,
                'time': (end - start) * 1000
            }
        
        start_total = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        end_total = time.time()
        total_time = (end_total - start_total) * 1000
        
        success_count = sum(1 for r in results if r['status'] == 200)
        response_times = [r['time'] for r in results if r['status'] == 200]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            
            print(f"\nConcurrent Requests (10):")
            print(f"  Total time: {total_time:.2f}ms")
            print(f"  Success rate: {success_count}/{num_requests}")
            print(f"  Avg response: {avg_time:.2f}ms")
            print(f"  Throughput: {num_requests / (total_time/1000):.2f} req/s")
            
            # All requests should succeed (if model loaded)
            # Total time should be less than serial execution
            assert total_time < (avg_time * num_requests), "Concurrent execution not faster than serial"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_50_requests(self, client, sample_resume):
        """Test 50 concurrent requests (high load)"""
        num_requests = 50
        
        def make_request():
            start = time.time()
            response = client.post("/api/v1/score", json=sample_resume)
            end = time.time()
            return {
                'status': response.status_code,
                'time': (end - start) * 1000
            }
        
        start_total = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        end_total = time.time()
        total_time = (end_total - start_total) * 1000
        
        success_count = sum(1 for r in results if r['status'] == 200)
        response_times = [r['time'] for r in results if r['status'] == 200]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
            
            print(f"\nConcurrent Requests (50):")
            print(f"  Total time: {total_time:.2f}ms")
            print(f"  Success rate: {success_count}/{num_requests}")
            print(f"  Avg response: {avg_time:.2f}ms")
            print(f"  P95 response: {p95_time:.2f}ms")
            print(f"  Throughput: {num_requests / (total_time/1000):.2f} req/s")
            
            # Should handle at least 80% success rate
            success_rate = success_count / num_requests
            assert success_rate >= 0.8, f"Success rate {success_rate:.2%} below 80%"
    
    @pytest.mark.performance
    def test_sustained_load(self, client, sample_resume):
        """Test sustained load over 30 seconds"""
        duration = 30  # seconds
        request_count = 0
        error_count = 0
        response_times = []
        
        start_time = time.time()
        end_time = start_time + duration
        
        print(f"\nSustained Load Test ({duration}s):")
        
        while time.time() < end_time:
            req_start = time.time()
            response = client.post("/api/v1/score", json=sample_resume)
            req_end = time.time()
            
            request_count += 1
            
            if response.status_code == 200:
                response_times.append((req_end - req_start) * 1000)
            else:
                error_count += 1
            
            # Small delay to avoid overwhelming
            time.sleep(0.1)
        
        total_time = time.time() - start_time
        
        if response_times:
            avg_time = statistics.mean(response_times)
            throughput = request_count / total_time
            error_rate = error_count / request_count
            
            print(f"  Total requests: {request_count}")
            print(f"  Success: {request_count - error_count}")
            print(f"  Errors: {error_count}")
            print(f"  Error rate: {error_rate:.2%}")
            print(f"  Avg response: {avg_time:.2f}ms")
            print(f"  Throughput: {throughput:.2f} req/s")
            
            # Error rate should be low
            assert error_rate < 0.05, f"Error rate {error_rate:.2%} exceeds 5%"
    
    @pytest.mark.performance
    def test_varying_payload_sizes(self, client):
        """Test performance with varying skill list sizes"""
        base_resume = {
            "experience_years": 5,
            "education": "Masters",
            "certifications": "AWS",
            "projects_count": 10,
            "current_role": "Engineer",
            "expected_salary": 100000
        }
        
        skill_sets = [
            # Small (3 skills)
            "Python, SQL, Git",
            # Medium (10 skills)
            "Python, SQL, Git, AWS, Docker, Kubernetes, React, Node.js, PostgreSQL, Redis",
            # Large (20 skills)
            "Python, Java, JavaScript, SQL, NoSQL, AWS, Azure, GCP, Docker, Kubernetes, " +
            "React, Angular, Vue, Node.js, Django, Spring, TensorFlow, PyTorch, Spark, Hadoop"
        ]
        
        results = []
        
        for skills in skill_sets:
            resume = base_resume.copy()
            resume['skills'] = skills
            
            start = time.time()
            response = client.post("/api/v1/score", json=resume)
            end = time.time()
            
            if response.status_code == 200:
                results.append({
                    'skill_count': len(skills.split(',')),
                    'time': (end - start) * 1000
                })
        
        if results:
            print(f"\nVarying Payload Size Performance:")
            for r in results:
                print(f"  {r['skill_count']} skills: {r['time']:.2f}ms")
            
            # Performance should not degrade significantly
            max_time = max(r['time'] for r in results)
            min_time = min(r['time'] for r in results)
            ratio = max_time / min_time if min_time > 0 else 1
            
            assert ratio < 3, f"Performance degradation {ratio:.2f}x too high"
    
    @pytest.mark.performance
    def test_cold_start_time(self, client, sample_resume):
        """Measure first request time (cold start)"""
        # This test assumes fresh API instance
        
        start = time.time()
        response = client.post("/api/v1/score", json=sample_resume)
        end = time.time()
        
        cold_start_time = (end - start) * 1000
        
        print(f"\nCold Start Performance:")
        print(f"  First request: {cold_start_time:.2f}ms")
        
        # Subsequent requests should be faster
        warm_times = []
        for _ in range(5):
            start = time.time()
            client.post("/api/v1/score", json=sample_resume)
            end = time.time()
            warm_times.append((end - start) * 1000)
        
        if warm_times:
            avg_warm_time = statistics.mean(warm_times)
            print(f"  Warm requests avg: {avg_warm_time:.2f}ms")
            
            # Warm requests should be faster than cold start
            # (unless model not loaded, then all are fast)
            if response.status_code == 200:
                assert avg_warm_time <= cold_start_time, "Warm requests slower than cold start"


@pytest.mark.performance
class TestBatchProcessingPerformance:
    """Performance tests specifically for batch processing"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def generate_resumes(self):
        """Generate N resumes for testing"""
        def _generate(n):
            base = {
                "skills": "Python, SQL",
                "experience_years": 3,
                "education": "Bachelors",
                "certifications": "None",
                "projects_count": 5,
                "current_role": "Developer",
                "expected_salary": 80000
            }
            return [base.copy() for _ in range(n)]
        return _generate
    
    @pytest.mark.performance
    def test_batch_scalability(self, client, generate_resumes):
        """Test how batch processing scales with size"""
        batch_sizes = [1, 5, 10, 25, 50, 100]
        results = []
        
        for size in batch_sizes:
            resumes = generate_resumes(size)
            
            start = time.time()
            response = client.post("/api/v1/batch", json={"resumes": resumes})
            end = time.time()
            
            if response.status_code == 200:
                total_time = (end - start) * 1000
                per_resume = total_time / size
                
                results.append({
                    'size': size,
                    'total_time': total_time,
                    'per_resume': per_resume
                })
        
        if results:
            print(f"\nBatch Scalability:")
            for r in results:
                print(f"  {r['size']:3d} resumes: {r['total_time']:7.2f}ms total, "
                      f"{r['per_resume']:6.2f}ms per resume")
            
            # Per-resume time should not increase too much with batch size
            first_per_resume = results[0]['per_resume']
            last_per_resume = results[-1]['per_resume']
            
            # Should have better efficiency at scale
            assert last_per_resume <= first_per_resume * 2, "Batch processing doesn't scale well"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'performance'])
