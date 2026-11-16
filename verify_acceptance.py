import sys
import datetime
from pathlib import Path
import httpx

# Ensure backend directory in sys.path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app

from fastapi.testclient import TestClient

def run_acceptance_test():
    print("=" * 60)
    print("STARTING 14-STEP END-TO-END ACCEPTANCE VERIFICATION")
    print("=" * 60)

    with TestClient(app) as client:
        # Step 1: Student 1 registers
        print("\n[Step 1] Student 1 (Alice) registers...")
        unique_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        alice_email = f"alice_{unique_suffix}@campus.edu"
        res = client.post("/api/v1/auth/register", json={
            "name": "Alice Green",
            "email": alice_email,
            "password": "SecurePassword123"
        })
        assert res.status_code == 201, f"Failed: {res.text}"
        alice_data = res.json()
        print(f"-> SUCCESS: Registered Alice ID {alice_data['id']} ({alice_data['email']})")

        # Step 2: Student 1 logs in
        print("\n[Step 2] Student 1 logs in...")
        res = client.post("/api/v1/auth/login", json={
            "email": alice_email,
            "password": "SecurePassword123"
        })
        assert res.status_code == 200, f"Failed: {res.text}"
        alice_token = res.json()["access_token"]
        alice_headers = {"Authorization": f"Bearer {alice_token}"}
        print("-> SUCCESS: Alice logged in and obtained JWT access token.")

        # Step 3: Student 1 submits LOST report for blue water bottle near Central Library
        print("\n[Step 3] Alice submits LOST report for blue water bottle...")
        res = client.post("/api/v1/reports", json={
            "item_name": "Blue Water Bottle",
            "category": "Bottle",
            "description": "Milton 750ml blue metallic water bottle with a small dent on cap and gym sticker",
            "report_type": "LOST",
            "approximate_date": str(datetime.date.today()),
            "location": "Central Library"
        }, headers=alice_headers)
        assert res.status_code == 201, f"Failed: {res.text}"
        lost_report = res.json()
        lost_id = lost_report["id"]
        print(f"-> SUCCESS: Created LOST report ID {lost_id}: '{lost_report['item_name']}' at {lost_report['location']}")

        # Step 4: Student 2 (Bob) registers and logs in
        print("\n[Step 4] Student 2 (Bob) registers and logs in...")
        bob_email = f"bob_{unique_suffix}@campus.edu"
        res = client.post("/api/v1/auth/register", json={
            "name": "Bob Miller",
            "email": bob_email,
            "password": "BobSecretPassword123"
        })
        assert res.status_code == 201, f"Failed: {res.text}"

        res = client.post("/api/v1/auth/login", json={
            "email": bob_email,
            "password": "BobSecretPassword123"
        })
        assert res.status_code == 200, f"Failed: {res.text}"
        bob_token = res.json()["access_token"]
        bob_headers = {"Authorization": f"Bearer {bob_token}"}
        print(f"-> SUCCESS: Bob logged in with email {bob_email}")

        # Step 5: Student 2 submits FOUND report for similar blue water bottle near Central Library
        print("\n[Step 5] Bob submits FOUND report for matching water bottle...")
        res = client.post("/api/v1/reports", json={
            "item_name": "Blue Milton Water Bottle",
            "category": "Bottle",
            "description": "Found a blue metallic Milton water bottle on study table on 2nd floor",
            "report_type": "FOUND",
            "approximate_date": str(datetime.date.today()),
            "location": "Central Library"
        }, headers=bob_headers)
        assert res.status_code == 201, f"Failed: {res.text}"
        found_report = res.json()
        found_id = found_report["id"]
        print(f"-> SUCCESS: Created FOUND report ID {found_id}: '{found_report['item_name']}' at {found_report['location']}")

        # Step 6: Student 1 browses reports
        print("\n[Step 6] Alice browses active reports...")
        res = client.get("/api/v1/reports")
        assert res.status_code == 200, f"Failed: {res.text}"
        reports_page = res.json()
        print(f"-> SUCCESS: Retrieved {len(reports_page['items'])} items (Total active: {reports_page['total']})")

        # Step 7 & 8: Alice retrieves potential matches for her LOST report
        print(f"\n[Step 7 & 8] Alice retrieves algorithmic matches for LOST report ID {lost_id}...")
        res = client.get(f"/api/v1/reports/{lost_id}/matches", headers=alice_headers)
        assert res.status_code == 200, f"Failed: {res.text}"
        matches_data = res.json()
        matches = matches_data["matches"]
        assert len(matches) > 0, "No matches surfaced!"
        top_match = matches[0]
        assert top_match["found_report_id"] == found_id, f"Expected top match to be Bob's found item {found_id}, got {top_match['found_report_id']}"
        print(f"-> SUCCESS: Matching Engine identified FOUND report ID {top_match['found_report_id']}!")
        print(f"   Similarity Score: {top_match['similarity_score']}% (Status: {top_match['match_status']})")
        print(f"   Attribute Breakdown:")
        print(f"     - Category:    {top_match['score_breakdown']['category']}%")
        print(f"     - Item Name:   {top_match['score_breakdown']['item_name']}%")
        print(f"     - Description: {top_match['score_breakdown']['description']}%")
        print(f"     - Location:    {top_match['score_breakdown']['location']}%")
        print(f"     - Date:        {top_match['score_breakdown']['date']}%")

        # Step 9 & 10: Alice submits claim with private identifying information
        print(f"\n[Step 9 & 10] Alice submits claim against FOUND report ID {found_id}...")
        claim_payload = {
            "report_id": found_id,
            "lost_report_id": lost_id,
            "verification_details": "Under the bottom base there is a yellow barcode sticker and a tiny scratch near the cap."
        }
        res = client.post("/api/v1/claims", json=claim_payload, headers=alice_headers)
        assert res.status_code == 201, f"Failed: {res.text}"
        claim = res.json()
        claim_id = claim["id"]
        assert claim["status"] == "PENDING"
        print(f"-> SUCCESS: Claim #{claim_id} created with status: {claim['status']}")

        # Step 11: Alice can view the claim status
        print(f"\n[Step 11] Alice views her claims list and specific claim...")
        res = client.get("/api/v1/claims/my", headers=alice_headers)
        assert res.status_code == 200
        my_claims = res.json()
        assert any(c["id"] == claim_id for c in my_claims)

        res = client.get(f"/api/v1/claims/{claim_id}", headers=alice_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "PENDING"
        print(f"-> SUCCESS: Alice confirmed Claim #{claim_id} is in status PENDING.")

        # Step 13: Bob (or another user) CANNOT access Alice's private claim details
        print(f"\n[Step 13] Checking privacy: Bob attempts to access Alice's Claim #{claim_id}...")
        res = client.get(f"/api/v1/claims/{claim_id}", headers=bob_headers)
        assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}"
        print("-> SUCCESS: 403 Forbidden correctly returned! Private verification details are secured.")

        # Step 14: Verify FOUND report is NOT automatically resolved or declared owned
        print(f"\n[Step 14] Verifying FOUND report ID {found_id} status remains ACTIVE (no automatic ownership handover)...")
        res = client.get(f"/api/v1/reports/{found_id}")
        assert res.status_code == 200
        found_status = res.json()["status"]
        assert found_status == "ACTIVE", f"Report status changed prematurely to {found_status}!"
        print(f"-> SUCCESS: FOUND report status is '{found_status}'. No automatic declaration of ownership.")

        # Step 12: Alice withdraws her pending claim
        print(f"\n[Step 12] Alice withdraws her pending claim #{claim_id}...")
        res = client.post(f"/api/v1/claims/{claim_id}/withdraw", headers=alice_headers)
        assert res.status_code == 200, f"Failed: {res.text}"
        withdrawn_claim = res.json()
        assert withdrawn_claim["status"] == "WITHDRAWN"
        print(f"-> SUCCESS: Claim #{claim_id} status updated to {withdrawn_claim['status']}")

        # Verify withdrawn claim cannot be withdrawn again
        res = client.post(f"/api/v1/claims/{claim_id}/withdraw", headers=alice_headers)
        assert res.status_code == 400
        print("-> SUCCESS: Re-withdrawal correctly rejected with 400 Bad Request.")

    print("\n" + "=" * 60)
    print("ALL 14 ACCEPTANCE CRITERIA SCENARIOS VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_acceptance_test()
