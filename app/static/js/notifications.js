// Lightweight "real-time" layer: poll the server every 10s for unread
// notification count and update the bell badge without a full page reload.
function updateNotificationBadge() {
  fetch("/notifications/unread-count")
    .then((res) => res.json())
    .then((data) => {
      const badge = document.getElementById("notif-badge");
      if (!badge) return;
      if (data.count > 0) {
        badge.textContent = data.count;
        badge.classList.remove("is-hidden");
      } else {
        badge.classList.add("is-hidden");
      }
    })
    .catch(() => {});
}

setInterval(updateNotificationBadge, 10000);
