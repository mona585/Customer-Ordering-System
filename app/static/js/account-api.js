/**
 * Shared fetch helpers for account/profile forms (mobile-safe).
 */
(function (global) {
  function isJsonResponse(response) {
    const ct = response.headers.get('content-type') || '';
    return ct.includes('application/json');
  }

  async function parseJsonResponse(response) {
    if (!isJsonResponse(response)) {
      if (response.status === 401 || response.redirected) {
        const err = new Error('Your session expired. Please sign in again.');
        err.code = 'AUTH';
        throw err;
      }
      const err = new Error('Unexpected server response. Please try again.');
      err.code = 'PARSE';
      throw err;
    }
    return response.json();
  }

  function networkMessage(error) {
    if (error && error.code === 'AUTH') return error.message;
    if (!global.navigator.onLine) {
      return 'You appear to be offline. Check your connection and try again.';
    }
    if (error && error.name === 'AbortError') {
      return 'Request timed out. Check your connection and try again.';
    }
    return (error && error.message) || 'Could not reach the server. Please try again.';
  }

  async function postForm(url, formData, options) {
    const opts = options || {};
    const controller = new AbortController();
    const timeoutMs = opts.timeoutMs || 30000;
    const timer = global.setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        signal: controller.signal,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'application/json',
          ...(opts.headers || {}),
        },
      });
      const data = await parseJsonResponse(response);
      return { response, data };
    } finally {
      global.clearTimeout(timer);
    }
  }

  async function postJson(url, payload, options) {
    const opts = options || {};
    const controller = new AbortController();
    const timer = global.setTimeout(() => controller.abort(), opts.timeoutMs || 30000);
    const csrf =
      global.document.querySelector('meta[name="csrf-token"]')?.content || '';

    try {
      const response = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'application/json',
          'X-CSRFToken': csrf,
          ...(opts.headers || {}),
        },
        body: JSON.stringify(payload),
      });
      const data = await parseJsonResponse(response);
      return { response, data };
    } finally {
      global.clearTimeout(timer);
    }
  }

  global.AuraAccount = {
    postForm,
    postJson,
    networkMessage,
    parseJsonResponse,
  };
})(window);
