document.addEventListener('DOMContentLoaded', () => {
  window.setTimeout(() => document.querySelector('.page-loader')?.classList.add('done'), 180);
  document.querySelector('.menu-button')?.addEventListener('click', () => document.querySelector('.sidebar')?.classList.toggle('open'));
  document.querySelectorAll('.flash button').forEach((button) => button.addEventListener('click', () => button.parentElement.remove()));
  const card = document.querySelector('input[name="card_number"]');
  card?.addEventListener('input', () => { const digits = card.value.replace(/\D/g, '').slice(0, 16); card.value = digits.replace(/(.{4})/g, '$1 ').trim(); });
  document.querySelectorAll('form').forEach((form) => form.addEventListener('submit', () => { const submit = form.querySelector('button[type="submit"]'); if (submit && form.checkValidity()) { submit.classList.add('is-loading'); submit.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing securely'; } }));
});
