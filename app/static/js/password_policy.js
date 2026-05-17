/**
 * Client-side password policy (mirrors app/security/password_policy.py).
 */
(function (global) {
  const MIN_LENGTH = 8;
  const MAX_LENGTH = 128;
  const SPECIAL = /[!@#$%^&*()_+\-=[\]{}|;:'",.<>?/\\`~]/;

  const COMMON = new Set([
    "password", "password1", "password12", "password123",
    "12345678", "123456789", "1234567890", "qwerty", "qwerty123",
    "admin", "admin123", "letmein", "welcome", "welcome1",
    "iloveyou", "monkey", "dragon", "master", "abc123", "11111111",
    "aura", "aura123", "customer", "test1234", "changeme",
  ]);

  const MIN_SEQUENCE_RUN = 6;

  const SEQUENCES = [
    "0123456789", "9876543210",
    "abcdefghijklmnopqrstuvwxyz", "zyxwvutsrqponmlkjihgfedcba",
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
  ];

  function hasSequence(lower) {
    const n = MIN_SEQUENCE_RUN;
    for (const seq of SEQUENCES) {
      for (let i = 0; i <= seq.length - n; i++) {
        if (lower.includes(seq.slice(i, i + n))) return true;
      }
    }
    return false;
  }

  function checkRule(password, username, email) {
    return {
      length: password.length >= MIN_LENGTH && password.length <= MAX_LENGTH,
      upper: /[A-Z]/.test(password),
      lower: /[a-z]/.test(password),
      digit: /\d/.test(password),
      special: SPECIAL.test(password),
      noSpace: !/\s/.test(password),
      notCommon: !COMMON.has(password.toLowerCase()),
      notRepeat: !/(.)\1{3,}/.test(password),
      notSeq: !hasSequence(password.toLowerCase()),
      notPersonal: (() => {
        const lower = password.toLowerCase();
        const u = (username || "").trim().toLowerCase();
        if (u.length >= 3 && lower.includes(u)) return false;
        const local = ((email || "").split("@")[0] || "").trim().toLowerCase();
        if (local.length >= 3 && lower.includes(local)) return false;
        return true;
      })(),
    };
  }

  function validatePassword(password, username, email) {
    if (!password) {
      return { ok: false, message: "Password is required." };
    }
    const r = checkRule(password, username, email);
    if (!r.length) {
      return { ok: false, message: `Password must be ${MIN_LENGTH}–${MAX_LENGTH} characters.` };
    }
    if (!r.noSpace) return { ok: false, message: "Password cannot contain spaces." };
    if (!r.upper) return { ok: false, message: "Add at least one uppercase letter (A–Z)." };
    if (!r.lower) return { ok: false, message: "Add at least one lowercase letter (a–z)." };
    if (!r.digit) return { ok: false, message: "Add at least one number." };
    if (!r.special) {
      return { ok: false, message: "Add at least one special character (e.g. ! @ # $)." };
    }
    if (!r.notCommon) {
      return { ok: false, message: "This password is too common. Choose a stronger one." };
    }
    if (!r.notRepeat) {
      return { ok: false, message: "Avoid four or more identical characters in a row." };
    }
    if (!r.notSeq) {
      return {
        ok: false,
        message: `Avoid ${MIN_SEQUENCE_RUN}+ characters in a row from a simple sequence (e.g. 123456 or qwerty).`,
      };
    }
    if (!r.notPersonal) {
      return { ok: false, message: "Password cannot include your username or email." };
    }
    return { ok: true, message: "", rules: r };
  }

  function bindPasswordChecker(opts) {
    const pwd = document.querySelector(opts.passwordSelector);
    const confirm = opts.confirmSelector
      ? document.querySelector(opts.confirmSelector)
      : null;
    const list = opts.checklistSelector
      ? document.querySelector(opts.checklistSelector)
      : null;
    const usernameEl = opts.usernameSelector
      ? document.querySelector(opts.usernameSelector)
      : null;
    const emailEl = opts.emailSelector
      ? document.querySelector(opts.emailSelector)
      : null;

    if (!pwd || !list) return;

    const items = {
      length: list.querySelector('[data-rule="length"]'),
      upper: list.querySelector('[data-rule="upper"]'),
      lower: list.querySelector('[data-rule="lower"]'),
      digit: list.querySelector('[data-rule="digit"]'),
      special: list.querySelector('[data-rule="special"]'),
      match: list.querySelector('[data-rule="match"]'),
    };

    function paint() {
      const username = usernameEl ? usernameEl.value.trim() : "";
      const email = emailEl ? emailEl.value.trim() : "";
      const r = checkRule(pwd.value, username, email);
      const set = (el, ok) => {
        if (!el) return;
        el.classList.toggle("pwd-ok", ok);
        el.classList.toggle("pwd-bad", !ok);
      };
      set(items.length, r.length && r.noSpace);
      set(items.upper, r.upper);
      set(items.lower, r.lower);
      set(items.digit, r.digit);
      set(items.special, r.special);
      if (items.match && confirm) {
        const match =
          confirm.value.length > 0 && pwd.value === confirm.value;
        set(items.match, match);
      }
    }

    ["input", "change"].forEach((ev) => {
      pwd.addEventListener(ev, paint);
      if (confirm) confirm.addEventListener(ev, paint);
      if (usernameEl) usernameEl.addEventListener(ev, paint);
      if (emailEl) emailEl.addEventListener(ev, paint);
    });
    paint();
  }

  global.AuraPasswordPolicy = {
    MIN_LENGTH,
    validatePassword,
    bindPasswordChecker,
  };
})(window);
