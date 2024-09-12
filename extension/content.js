async function sendDataToServer(data) {
  try {
    const response = await fetch('http://localhost:5000/check_url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: window.location.href }),
    });

    const data = await response.json();
    if (data.message.includes('phishing site')) {
      chrome.runtime.sendMessage({
        action: "showNotification",
        message: data.message,
        url: window.location.href // or wherever you want the URL to come from
      }, function(response) {
        console.log('Message sent:');
      });
    }
    
    // You won't be able to parse the response as JSON in no-cors mode
    console.log('Request sent, but response handling is limited due to no-cors mode');
  } catch (error) {
    console.error('Error sending data to server:', error);
  }
}


// Call the function to fetch data
sendDataToServer();





