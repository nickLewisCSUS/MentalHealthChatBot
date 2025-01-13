// chatbot.js
async function sendMessage() {
    const userMessage = document.getElementById('userMessage').value;

    // Check if the input is not empty
    if (!userMessage) {
        alert("Please enter a message before sending.");
        return;
    }

    try {
        // Sending a POST request to the FastAPI backend
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_message: userMessage })
        });

        // Handling the server response
        if (!response.ok) {
            throw new Error("Failed to fetch the chatbot response.");
        }

        const result = await response.json();
        document.getElementById('botResponse').innerText = result.response;
    } catch (error) {
        console.error("Error:", error);
        document.getElementById('botResponse').innerText = "Error reaching the chatbot server.";
    }
}