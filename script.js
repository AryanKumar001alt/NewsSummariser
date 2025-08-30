async function analyzeNews() {
    const url = document.getElementById("url").value;
    const text = document.getElementById("text").value;
    const tone = document.getElementById("tone").value;

    const loader = document.getElementById("loader");
    const result = document.getElementById("result");

    // Show loader
    loader.style.display = "block";
    result.innerHTML = "";

    try {
        // Call backend API (relative path works on Render)
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, text, tone })
        });

        const data = await response.json();

        if (data.error) {
            // Show error
            result.innerHTML = `<p style="color:red">${data.error}</p>`;
        } else {
            // Show summary and bias
            result.innerHTML = `
                <div class="summary-card">
                    <h3>Summary:</h3>
                    <p>${data.summary}</p>
                </div>
                <div class="bias-card">
                    <h3>Bias:</h3>
                    <p>${data.bias}</p>
                </div>
            `;
        }
    } catch (err) {
        // Catch network or other errors
        result.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
    } finally {
        // Hide loader
        loader.style.display = "none";
    }
}
