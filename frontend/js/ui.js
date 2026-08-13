const WARNING_THRESHOLD = 0.9;


export function showErrors(errors) {
    for (const campo in errors) {
    document.getElementById("error-" + campo).textContent = errors[campo];
    document.getElementById(campo).classList.add("is-invalid");
}
 }
export function clearErrors() {
    // 1. vaciar los textos de error
    document.querySelectorAll('.invalid-feedback').forEach(el => {
        el.textContent = '';
    });

    // 2. quitar el marcado rojo de los inputs
    document.querySelectorAll('.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
}
export function showMessage(text, type) {
    const messageDiv = document.getElementById('form-message');
    messageDiv.textContent = text;
    messageDiv.className = type === 'success' ? 'alert alert-success' : 'alert alert-danger';

}

export function clearMessage() {
    const el = document.getElementById('form-message');
    el.textContent = '';
    el.className = '';
}
export function updateCounter(current, max) {
    const counter = document.getElementById('counter');
    const warning = current > max * WARNING_THRESHOLD && current < max;
    const danger = current >= max;
    const normal = current <= max * WARNING_THRESHOLD;
    counter.textContent = `${current}/${max}`;
    counter.classList.toggle('text-warning', warning);
    counter.classList.toggle('text-danger', danger);
    counter.classList.toggle('text-secondary', normal);
}
