// Auto-dismiss alerts after 4s
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 300);
  }, 4000);
});

// Char counter for textareas with maxlength
document.querySelectorAll('textarea[maxlength]').forEach(el => {
  const max = el.getAttribute('maxlength');
  const hint = el.parentElement.querySelector('.form-text');
  if (hint) {
    el.addEventListener('input', () => {
      hint.textContent = `${el.value.length} / ${max} characters`;
    });
  }
});