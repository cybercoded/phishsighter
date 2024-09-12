chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
  const currentUrl = tabs[0].url;
  const statusElement = document.getElementById('status');
  let statusMessage = "Unknown status";  // Default status message in case of error

  try {
    // Perform phishing check via API
    const response = await fetch("http://localhost:5000/check_url", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: currentUrl })
    });

    const data = await response.json();

    // Update status based on phishing result
    if (data.message.includes('phishing site')) {
      statusMessage = "Warning: Phishing site detected!";
    } else if (data.message.includes('safe')) {
      statusMessage = "This site is safe.";
    } else {
      statusMessage = `Error: this site ${data.message}`;
    }

    // Update the statusElement on the UI
    statusElement.textContent = statusMessage;

    // Add a link to view full analysis
    const fullPageLink = document.createElement('a');
    fullPageLink.href = `http://localhost:5000/?url=${encodeURIComponent(currentUrl)}`;
    fullPageLink.target = "_blank"; // Open in a new tab
    fullPageLink.textContent = "View Full Page Analysis";
    fullPageLink.style.display = "block";
    fullPageLink.style.marginTop = "10px";
    
    statusElement.appendChild(fullPageLink);

  } catch (error) {
    console.error('Error during phishing check:', error);
    statusMessage = `An error occurred: ${error.message}`;
    statusElement.textContent = statusMessage;
  }

  // Send message to content script to show notification
  // Store the statusMessage in chrome.storage.local
  chrome.storage.local.set({statusMessage: statusMessage}, function() {
    console.log('Message stored in chrome.storage.local');
  });

  chrome.tabs.sendMessage(tabs[0].id, {
    action: "showNotification",
    message: statusMessage  // Send the statusMessage as the notification content
  }, function(response) {
    console.log("Message sent from popup to content script");
    if (chrome.runtime.lastError) {
      console.error("Error sending message:", chrome.runtime.lastError.message);
    }
  });
});
