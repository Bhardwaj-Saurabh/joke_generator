document.getElementById('jokeForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // UI Elements
    const topic = document.getElementById('topic').value;
    const tone = document.getElementById('tone').value;
    const btn = document.getElementById('generateBtn');
    const resultSection = document.getElementById('resultSection');

    // Set Loading State
    btn.classList.add('loading');
    resultSection.classList.add('hidden');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                tone: tone,
                language: 'english'
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate joke');
        }

        const data = await response.json();

        // Update UI with Result
        document.getElementById('jokeSetup').textContent = data.setup;
        document.getElementById('jokePunchline').textContent = data.punchline;

        const explanationEl = document.getElementById('jokeExplanation');
        if (data.explanation) {
            explanationEl.textContent = `Why it's funny: ${data.explanation}`;
            explanationEl.classList.remove('hidden');
        } else {
            explanationEl.classList.add('hidden');
        }

        resultSection.classList.remove('hidden');

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        // Reset Loading State
        btn.classList.remove('loading');
    }
});

function copyToClipboard() {
    const setup = document.getElementById('jokeSetup').textContent;
    const punchline = document.getElementById('jokePunchline').textContent;
    const text = `${setup}\n\n${punchline}`;

    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    });
}
