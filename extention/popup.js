chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const currentUrl = tabs[0].url;
  
    fetch("http://localhost:5000/check_url", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: currentUrl })
    })
    .then(response => response.json())
    .then(data => {
      const statusElement = document.getElementById('status');
      if (data.is_phishing) {
        statusElement.textContent = "Warning: Phishing site detected!";
      } else {
        statusElement.textContent = "This site is safe.";
      }
    });
  });
  