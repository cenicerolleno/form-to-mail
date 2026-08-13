import { sendContactForm } from "./api.js";
import { validateContactData } from "./validation.js";
import { showErrors, clearErrors, showMessage, clearMessage, updateCounter } from "./ui.js";

const MAX_MESSAGE_LENGTH = 500
const form = document.getElementById("contactForm");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearErrors();
  clearMessage();

  // 1. recoger los datos del formulario
  const formData = {
    name: form.elements.name.value,
    email: form.elements.email.value,
    phone: form.elements.phone.value,
    message: form.elements.message.value,
    consent: form.elements.consent.checked,
    website: form.elements.website.value, // Honeypot field
  };
  // 2. validar en cliente → si hay errores, pintarlos y salir
  const errors = validateContactData(formData);
  if (Object.keys(errors).length > 0) {
    showErrors(errors);
    return;
  }
  // 3. llamar a la API
  const result = await sendContactForm(formData);
  // 4. actuar según el resultado
  if (result.ok) {
    // éxito
    form.reset()
    showMessage("Formulario enviado con éxito.", 'success');    
  } else if (result.status === 400) {
    // errores del servidor
    showErrors(result.errors);
  } else if (result.status === 429) {
    // demasiadas peticiones
    showMessage("Demasiadas peticiones. Inténtalo más tarde.", 'danger')
  } else {
    // fallo general
    showMessage("Error al enviar el formulario.", 'danger')
  }
});

const message = form.elements.message;
updateCounter(message.value.length, MAX_MESSAGE_LENGTH);
message.addEventListener('input', () => {
    updateCounter(message.value.length, MAX_MESSAGE_LENGTH);
});

form.addEventListener('reset', () => {
    clearErrors();
    clearMessage();
    updateCounter(0, MAX_MESSAGE_LENGTH);
});