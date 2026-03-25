// ── Elements ──────────────────────────────────────────────
const form        = document.getElementById('loginForm');
const emailInput  = document.getElementById('email');
const pwInput     = document.getElementById('password');
const emailField  = document.getElementById('emailField');
const passwordField = document.getElementById('passwordField');
const togglePwBtn = document.getElementById('togglePw');
const eyeIcon     = document.getElementById('eyeIcon');
const loginBtn    = document.getElementById('loginBtn');
const toast       = document.getElementById('toast');
const toastMsg    = document.getElementById('toastMsg');

// ── Password Toggle ────────────────────────────────────────
const eyeOpen = `
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
  <circle cx="12" cy="12" r="3"/>`;

const eyeClosed = `
  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
  <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
  <line x1="1" y1="1" x2="23" y2="23"/>`;

let pwVisible = false;

togglePwBtn.addEventListener('click', () => {
  pwVisible = !pwVisible;
  pwInput.type = pwVisible ? 'text' : 'password';
  eyeIcon.innerHTML = pwVisible ? eyeClosed : eyeOpen;
  togglePwBtn.setAttribute('aria-label',
    pwVisible ? 'Hide password' : 'Show password');
});

// ── Inline Validation ──────────────────────────────────────
function validateEmail(val) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim());
}

function setError(fieldEl, show) {
  if (show) fieldEl.classList.add('has-error');
  else      fieldEl.classList.remove('has-error');
}

emailInput.addEventListener('blur', () => {
  setError(emailField, emailInput.value && !validateEmail(emailInput.value));
});

emailInput.addEventListener('input', () => {
  if (emailField.classList.contains('has-error') && validateEmail(emailInput.value))
    setError(emailField, false);
});

pwInput.addEventListener('blur', () => {
  setError(passwordField, pwInput.value && pwInput.value.length < 6);
});

pwInput.addEventListener('input', () => {
  if (passwordField.classList.contains('has-error') && pwInput.value.length >= 6)
    setError(passwordField, false);
});

// ── Toast Helper ───────────────────────────────────────────
function showToast(message, duration = 3000) {
  toastMsg.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

// ── Form Submit ────────────────────────────────────────────
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const emailVal = emailInput.value.trim();
  const pwVal    = pwInput.value;
  let valid = true;

  if (!validateEmail(emailVal)) {
    setError(emailField, true);
    valid = false;
  }
  if (pwVal.length < 6) {
    setError(passwordField, true);
    valid = false;
  }

  if (!valid) return;

  // ── Simulate async login ──
  loginBtn.classList.add('loading');
  loginBtn.disabled = true;

  await new Promise(r => setTimeout(r, 1800));

  loginBtn.classList.remove('loading');
  loginBtn.disabled = false;

  showToast('✓  Login successful! Redirecting…');
});

// ── Social button stubs ────────────────────────────────────
document.getElementById('googleBtn').addEventListener('click', () => {
  showToast('Google sign-in coming soon!', 2200);
});

document.getElementById('githubBtn').addEventListener('click', () => {
  showToast('GitHub sign-in coming soon!', 2200);
});

// ── Forgot password stub ───────────────────────────────────
document.getElementById('forgotLink').addEventListener('click', (e) => {
  e.preventDefault();
  showToast('Password reset link sent to your email!', 2500);
});

// ── Sign up stub ───────────────────────────────────────────
document.getElementById('signupLink').addEventListener('click', (e) => {
  e.preventDefault();
  showToast('Redirecting to sign-up page…', 2000);
});
