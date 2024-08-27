chrome.webRequest.onBeforeRequest.addListener(
    async function(details) {
      const url = details.url;
  
      // Call the local server or cloud server hosting your phishing model
      const response = await fetch("http://localhost:5000/check_url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: url })
      });
  
      const result = await response.json();
  
      if (result.is_phishing) {
        return { cancel: true };  // Block the request if it's a phishing site
      }
    },
    { urls: ["<all_urls>"] },
    ["blocking"]
  );
  