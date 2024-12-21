document.getElementById('ticketForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Останавливаем перезагрузку страницы

    const data = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        subject: document.getElementById('subject').value,
        description: document.getElementById('description').value
    };

    try {
        const response = await fetch('https://app-service-qwog.onrender.com/tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            document.getElementById('responseMessage').textContent = "Ticket submitted successfully!";

            // Очистка формы
            document.getElementById('ticketForm').reset(); // Очистка формы
        } else {
            document.getElementById('responseMessage').textContent = "Failed to submit ticket.";
        }

        // Очистить сообщение через 3 секунды
        setTimeout(() => {
            document.getElementById('responseMessage').textContent = "";
        }, 3000);
    } catch (error) {
        document.getElementById('responseMessage').textContent = "Error submitting ticket: " + error.message;
    }
});
