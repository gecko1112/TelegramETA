const statusEl = document.getElementById("status");

function showLoading() {
  statusEl.innerHTML = `
    Trying to send your location
    <div class="loading-dots">
      <span>.</span><span>.</span><span>.</span>
    </div>
  `;
}

function showSuccess() {
  statusEl.innerHTML = `<span class="icon success">✓</span> Location sent!`;
  setTimeout(() => {
    showLoading();
  }, 2000);
}

function showError() {
  statusEl.innerHTML = `<span class="icon error">✗</span> Error sending location.`;
}

function sendLocation() {
  if ("geolocation" in navigator) {
    showLoading();

    navigator.geolocation.getCurrentPosition(
      function(position) {
        fetch("/location", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        })
        .then(res => {
          if (!res.ok) throw new Error("Network response not ok");
          return res.json();
        })
        .then(data => {
          console.log("Location sent successfully", data);
          showSuccess();
        })
        .catch(err => {
          console.error("Fetch error:", err);
          showError();
        });
      },
      function(error) {
        console.error("Geolocation error:", error);
        showError();
      }
    );
  } else {
    console.log("Geolocation not supported");
    showError();
  }
}

window.onload = function() {
  sendLocation();
  setInterval(sendLocation, 5000);
};
