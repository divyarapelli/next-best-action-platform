"""Integration smoke test for the Next Best Action platform."""

from backend.agents.planner_agent import run_planner
from backend.memory.memory_store import init_db, save_action, get_memory_summary

TEST_INPUT = (
    "Customer said they are considering a competitor. "
    "Renewal is due in 10 days. They complained about "
    "slow support response times."
)


def report(step: str, ok: bool, details: str = ""):
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {step}{(' - ' + details) if details else ''}")


def main():
    try:
        result = run_planner(TEST_INPUT)
        report("run_planner() completed", True)
    except Exception as exc:
        report("run_planner() completed", False, str(exc))
        return

    planner_mode = result.get("planner_mode")
    print(f"planner_mode: {planner_mode}")
    report("planner_mode is gpt-5.5", planner_mode == "gpt-5.5", f"got {planner_mode}")
    report("planner_mode is not mock", planner_mode != "mock", f"got {planner_mode}")

    recommendations = result.get("recommendations", [])
    print("recommendations:")
    for index, rec in enumerate(recommendations[:3], 1):
        print(f"{index}. {rec.get('action_title')} | confidence={rec.get('confidence')}")
    report("3 recommendations returned", len(recommendations) == 3, f"got {len(recommendations)}")
    report("rag_hits present", "rag_hits" in result, f"got {result.get('rag_hits')}")
    report("memory_hits present", "memory_hits" in result, f"got {result.get('memory_hits')}")
    print(f"rag_hits: {result.get('rag_hits')}")
    print(f"memory_hits: {result.get('memory_hits')}")

    try:
        init_db()
        first_action = recommendations[0] if recommendations else {}
        save_action(
            situation=TEST_INPUT[:100],
            action=first_action.get("action_title", "Approved action"),
            confidence=float(first_action.get("confidence", 0)),
            decision="approved",
        )
        report("save_action() stored approved action", True)
    except Exception as exc:
        report("save_action() stored approved action", False, str(exc))
        return

    try:
        memory_summary = get_memory_summary(TEST_INPUT)
        print(f"memory_summary: {memory_summary}")
        report("get_memory_summary() returned text", bool(memory_summary), memory_summary)
        report("memory summary indicates history", memory_summary != "No similar past actions found.", memory_summary)
    except Exception as exc:
        report("get_memory_summary() returned text", False, str(exc))


if __name__ == "__main__":
    main()
