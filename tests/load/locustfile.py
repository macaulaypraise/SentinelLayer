from locust import HttpUser, between, task


class SentinelLoadTest(HttpUser):
    # Simulates a user waiting 1 to 2 seconds between requests
    wait_time = between(1, 2)

    # Replace with the exact key you restored to your database
    headers = {"X-API-Key": "sl_live_testkey123", "Content-Type": "application/json"}

    @task(3)
    def test_clean_transaction(self) -> None:
        """Simulates 75% of traffic: normal, clean users."""
        payload = {
            "phone_number": "+2348011111111",
            "account_id": "load_clean_001",
            "transaction_amount": 15000,
            "expected_region": "Lagos",
            "name": "Load Tester",
            "dob": "1990-01-01",
            "address": "12 Test Street",
            "account_registered_at": "2023-06-01",
        }
        # The catch_response parameter lets us log custom success/failure metrics
        with self.client.post(
            "/v1/sentinel/check", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200 and not response.json().get("fast_path"):
                response.success()

    @task(1)
    def test_fraud_transaction(self) -> None:
        """Simulates 25% of traffic: active SIM swap attacks triggering fast-path."""
        payload = {
            "phone_number": "+2348022222222",  # Assume this triggers NaC sandbox fraud response
            "account_id": "load_fraud_002",
            "transaction_amount": 500000,
            "expected_region": "Lagos",
            "name": "Fraud Tester",
            "dob": "1985-01-01",
            "address": "15 Broad Street",
            "account_registered_at": "2024-01-10",
        }
        self.client.post("/v1/sentinel/check", json=payload, headers=self.headers)
