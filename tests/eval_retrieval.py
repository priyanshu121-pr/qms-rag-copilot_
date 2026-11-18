"""Step 8: retrieval check. Har sawaal ke liye dekho ki sahi document top-4 me aaya ya nahi.
Chalao: python -m tests.eval_retrieval   (API key ki zarurat nahi)"""
from src.rag import retrieve

CASES = [
    ("Weld me crack mile to kya karna hai?", "sop_welding.txt"),
    ("Batch B-4471 me porosity ka kya reason tha?", "capa_2026_009.txt"),
    ("Gas regulator kab replace hua?", "capa_2026_009.txt"),
    ("Calibration kitne time me ek baar hoti hai?", "sop_calibration.txt"),
    ("Supplier audit me kya fail hua?", "supplier_audit_2026_q2.txt"),
    ("Torque wrench ka calibration overdue tha kya?", "inspection_log_line2.txt"),
]

hit = 0
for question, expected in CASES:
    sources = [h["source"] for h in retrieve(question, k=4)]
    ok = expected in sources
    hit += ok
    print(("PASS" if ok else "FAIL"), "|", question, "->", sources[:2])
print(f"\nRetrieval hit rate: {hit}/{len(CASES)}")
