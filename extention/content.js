chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.is_phishing) {
      alert("Warning: This site may be a phishing site!");
    }
  });
  