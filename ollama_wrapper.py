import subprocess

def generate_review(text, model_name="mistral"):
    prompt = f"""You are simulating a Scopus Q1 peer review process.

Act as three independent reviewers. Provide constructive feedback focusing on:
- Novelty
- Methodology
- Clarity
- Structure
- Reference Quality

Use the following format:
Reviewer A:
...
Reviewer B:
...
Reviewer C:
...

Here is the paper content:
{text[:4000]}  # Limited for performance
"""

    try:
        result = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120  # max wait time
        )

        output = result.stdout.decode("utf-8")
        return output

    except Exception as e:
        return f"⚠️ Error generating review: {str(e)}"
