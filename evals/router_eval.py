from app.graph.nodes import router

CASES = [
    ("How many candidates are in each status?", "sql"),
    ("Which candidates know Kafka?", "sql"),
    ("List candidates in the interview stage", "sql"),
    ("Who are the best fits for a senior backend role with Kafka?", "match"),
    ("Rank candidates for a React frontend position", "match"),
    ("Email the top 3 devops candidates about the opening", "outreach"),
    ("Delete all rejected candidates", "write"),
    ("Update the status of candidate 5 to offer", "write"),
    ("Hi there!", "chat"),
    ("What's the weather today?", "chat"),
]

passed = 0
for question, expected in CASES:
    got = router({"question": question})["intent"]
    ok = got == expected
    passed += ok
    print(("PASS" if ok else "FAIL"), f"[{expected} vs {got}]", question)
print(f"\nScore: {passed}/{len(CASES)}")