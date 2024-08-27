chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "checkPhishing") {
    const currentUrl = window.location.href;

    fetch("http://localhost:5000/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: currentUrl })
    })
    .then(response => response.json())
    .then(data => {
      if (data.is_phishing) {
        alert("Warning: This site may be a phishing site!");
        // Optionally redirect to a warning page
        window.location.href = "https://your-safe-page.com";
      }
    })
    .catch(error => console.error('Error:', error));
  }
});

// Send message to background script to check phishing on load
chrome.runtime.sendMessage({ action: "checkPhishing" });
