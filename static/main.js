function openModal(type) {
    document.getElementById(type + 'Modal').style.display = 'block';
}

function closeModal(type) {
    document.getElementById(type + 'Modal').style.display = 'none';
}

async function handleSignup() {
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    try {
        const response = await fetch('http://127.0.0.1:5555/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await response.json();
        alert(data.message || data.error); // Show message from server

        if (response.ok) {
            closeModal('signup');
        }
    } catch (error) {
        alert('Signup failed. Please try again.');
        console.error(error);
    }
}

async function handleLogin() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('http://127.0.0.1:5555/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        alert(data.message || data.error);

        if (response.ok) {
            // Redirect to the correct URL for myStockroom
            window.location.href = "http://127.0.0.1:5555/myStockroom";  // Adjusted URL for the page
        }
    } catch (error) {
        alert('Login failed. Please try again.');
        console.error(error);
    }
}

