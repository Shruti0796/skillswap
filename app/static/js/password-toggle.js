// Adds a show/hide eye button to any input marked with data-password-toggle,
// so people can check what they typed before submitting.
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-password-toggle]").forEach(function (input) {
    const wrapper = document.createElement("div");
    wrapper.className = "password-field";
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "password-toggle";
    btn.setAttribute("aria-label", "Show password");
    btn.innerHTML = eyeIcon(false);
    wrapper.appendChild(btn);

    btn.addEventListener("click", function () {
      const showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.innerHTML = eyeIcon(!showing);
      btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
    });
  });

  function eyeIcon(open) {
    if (open) {
      return '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>';
    }
    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18"/><path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"/><path d="M9.5 5.2A9.8 9.8 0 0 1 12 5c6.5 0 10 7 10 7a13.2 13.2 0 0 1-3.1 3.9M6.1 6.1C3.7 7.7 2 10 2 10s3.5 7 10 7c1.2 0 2.3-.2 3.3-.6"/></svg>';
  }
});
