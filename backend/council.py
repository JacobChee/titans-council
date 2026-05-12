"""3-stage Titans Council orchestration."""

from typing import List, Dict, Any, Tuple
from .openrouter import query_titans_parallel, query_model
from .config import TITANS, CHAIRMAN_MODEL, CHAIRMAN_NAME


async def stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    """Stage 1: Each titan answers the question in their own voice."""
    messages = [{"role": "user", "content": user_query}]
    responses = await query_titans_parallel(TITANS, messages)

    return [
        {"model": name, "response": resp.get("content", "")}
        for name, resp in responses.items()
        if resp is not None
    ]


async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """Stage 2: Each titan ranks the anonymised responses."""
    labels = [chr(65 + i) for i in range(len(stage1_results))]

    label_to_model = {
        f"Response {label}": result["model"]
        for label, result in zip(labels, stage1_results)
    }

    responses_text = "\n\n".join([
        f"Response {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    ranking_prompt = f"""You are evaluating different responses to the following question:

Question: {user_query}

Here are the responses from different advisors (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Example of the correct format for your ENTIRE response:

Response A provides good detail on X but misses Y...
Response B is accurate but lacks depth on Z...
Response C offers the most comprehensive answer...

FINAL RANKING:
1. Response C
2. Response A
3. Response B

Now provide your evaluation and ranking:"""

    messages = [{"role": "user", "content": ranking_prompt}]
    responses = await query_titans_parallel(TITANS, messages)

    stage2_results = []
    for name, response in responses.items():
        if response is not None:
            full_text = response.get("content", "")
            stage2_results.append({
                "model": name,
                "ranking": full_text,
                "parsed_ranking": parse_ranking_from_text(full_text),
            })

    return stage2_results, label_to_model


async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Stage 3: Chairman synthesizes the final answer from all titan input."""
    stage1_text = "\n\n".join([
        f"{result['model']}:\n{result['response']}"
        for result in stage1_results
    ])

    stage2_text = "\n\n".join([
        f"{result['model']} (evaluator):\n{result['ranking']}"
        for result in stage2_results
    ])

    chairman_prompt = f"""You are synthesizing the collective wisdom of five world-class business titans: Elon Musk, Steve Jobs, Jeff Bezos, Alex Hormozi, and Jensen Huang.

Each titan has answered the following question in their own voice, and then ranked each other's responses.

Original Question: {user_query}

STAGE 1 — Individual Titan Responses:
{stage1_text}

STAGE 2 — Peer Rankings:
{stage2_text}

Your task is to synthesize all of this into a single, powerful final answer. Draw on the strongest insights from each titan, note where they agree, and where they meaningfully disagree. Deliver a clear, actionable conclusion that represents the council's collective wisdom.

Final Answer:"""

    messages = [{"role": "user", "content": chairman_prompt}]
    response = await query_model(CHAIRMAN_MODEL, messages)

    if response is None:
        return {"model": CHAIRMAN_NAME, "response": "Error: Unable to generate final synthesis."}

    return {"model": CHAIRMAN_NAME, "response": response.get("content", "")}


def parse_ranking_from_text(ranking_text: str) -> List[str]:
    """Extract the FINAL RANKING section from a model's response."""
    import re

    if "FINAL RANKING:" in ranking_text:
        parts = ranking_text.split("FINAL RANKING:")
        if len(parts) >= 2:
            ranking_section = parts[1]
            numbered_matches = re.findall(r"\d+\.\s*Response [A-Z]", ranking_section)
            if numbered_matches:
                return [re.search(r"Response [A-Z]", m).group() for m in numbered_matches]
            return re.findall(r"Response [A-Z]", ranking_section)

    return re.findall(r"Response [A-Z]", ranking_text)


def calculate_aggregate_rankings(
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Calculate aggregate rankings across all titans."""
    from collections import defaultdict

    model_positions = defaultdict(list)

    for ranking in stage2_results:
        parsed_ranking = parse_ranking_from_text(ranking["ranking"])
        for position, label in enumerate(parsed_ranking, start=1):
            if label in label_to_model:
                model_positions[label_to_model[label]].append(position)

    aggregate = [
        {
            "model": model,
            "average_rank": round(sum(positions) / len(positions), 2),
            "rankings_count": len(positions),
        }
        for model, positions in model_positions.items()
        if positions
    ]

    aggregate.sort(key=lambda x: x["average_rank"])
    return aggregate


async def generate_conversation_title(user_query: str) -> str:
    """Generate a short title for a conversation."""
    title_prompt = f"""Generate a very short title (3-5 words maximum) that summarizes the following question.
The title should be concise and descriptive. Do not use quotes or punctuation in the title.

Question: {user_query}

Title:"""

    messages = [{"role": "user", "content": title_prompt}]
    response = await query_model("google/gemini-2.5-flash", messages, timeout=30.0)

    if response is None:
        return "New Conversation"

    title = response.get("content", "New Conversation").strip().strip("\"'")
    return title[:47] + "..." if len(title) > 50 else title


async def run_full_council(user_query: str) -> Tuple[List, List, Dict, Dict]:
    """Run the complete 3-stage titans council process."""
    stage1_results = await stage1_collect_responses(user_query)

    if not stage1_results:
        return [], [], {
            "model": "error",
            "response": "All titans failed to respond. Please try again."
        }, {}

    stage2_results, label_to_model = await stage2_collect_rankings(user_query, stage1_results)
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)
    stage3_result = await stage3_synthesize_final(user_query, stage1_results, stage2_results)

    metadata = {
        "label_to_model": label_to_model,
        "aggregate_rankings": aggregate_rankings,
    }

    return stage1_results, stage2_results, stage3_result, metadata
