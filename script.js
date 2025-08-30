async function analyzeNews() {
    const url = document.getElementById("url").value;
    const text = document.getElementById("text").value;
    const tone = document.getElementById("tone").value;

    const loader = document.getElementById("loader");
    const result = document.getElementById("result");

    loader.style.display = "block";
    result.innerHTML = "";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, text, tone })
        });

        let data;
        try {
            data = await response.json();
        } catch {
            data = { error: "Invalid response from server", summary: "", bias: "" };
        }

        if (data.error) {
            result.innerHTML = `<p style="color:red">${data.error}</p>`;
        } else {
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
        result.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
    } finally {
        loader.style.display = "none";
    }
}
