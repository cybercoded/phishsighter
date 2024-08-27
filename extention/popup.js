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
    
    // Add a "View Full Page" link
    const fullPageLink = document.createElement('a');
    fullPageLink.href = `http://localhost:5000/?url=${encodeURIComponent(currentUrl)}`;
    fullPageLink.target = "_blank"; // Open in a new tab
    fullPageLink.textContent = "View Full Page Analysis";
    fullPageLink.style.display = "block";
    fullPageLink.style.marginTop = "10px";
    
    statusElement.appendChild(fullPageLink);
  })
  .catch(error => {
    console.error('Error:', error);
    const statusElement = document.getElementById('status');
    statusElement.textContent = "An error occurred while checking the site.";
  });
});