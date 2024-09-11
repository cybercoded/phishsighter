chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
 
  if (message.action === "showNotification") {
    chrome.notifications.create({
      type: "basic",
      iconUrl: chrome.runtime.getURL("icon.png"),
      title: "Phishing Alert!",
      message: `${message.url} ${message.message}`
    }, function(notificationId) {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError.message);
      } else {
        console.log(`Notification created with ID: ${notificationId}`);
      }
    });
  }
});
