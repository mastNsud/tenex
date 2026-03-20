document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    const appendMessage = (text, sender) => {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.innerHTML = `<p>${text}</p>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const handleChat = async () => {
        const text = userInput.value.trim();
        if (!text) return;

        appendMessage(text, 'user');
        userInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(text) // main.py expects a plain string or we might need to adjust based on endpoint
            });
            
            // Note: main.py expects a POST with a string. 
            // FastAPI's `message: str` as a single argument might need a query param or a body object.
            // Let's refine the backend to handle this better if needed.

            const data = await response.json();
            if (data.response) {
                appendMessage(data.response, 'bot');
            } else if (data.detail) {
                appendMessage(`Error: ${data.detail}`, 'bot');
            }
        } catch (error) {
            appendMessage("Sorry, I'm having trouble connecting to the brain. 🧠", 'bot');
            console.error(error);
        }
    };

    sendBtn.addEventListener('click', handleChat);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleChat();
    });
});
