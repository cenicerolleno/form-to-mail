const API_URL = 'http://localhost:5001/contact';

export async function sendContactForm(formData) {
    // devuelve { ok, status, errors }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },

            body: JSON.stringify(formData),
        });
       const data = await response.json();
       return { ok: response.ok, status: response.status, errors: data.errors };

    } catch (error) {
        console.error('Error: ', error);
        return { ok: false, status: null, errors: null };
    }
}