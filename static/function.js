$(document).ready(function() {
    // Function to get URL parameters
    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    // Function to validate a URL and add http:// if necessary
    function formatAndValidateUrl(urlString) {
        if (!/^https?:\/\//i.test(urlString)) {
            urlString = 'http://' + urlString;
        }
        try {
            new URL(urlString);  // This will throw if the URL is invalid
            return urlString;
        } catch (e) {
            return false;
        }
    }

    // Function to update the URL parameters without reloading the page
    function updateUrlParams(url) {
        const params = new URLSearchParams(window.location.search);
        params.set('url', url);
        const newUrl = `${window.location.pathname}?${params.toString()}`;
        history.replaceState({}, '', newUrl);
    }

    // Define the feature labels
    const featureLabels = [
        'Using IP', 'Long URL', 'Short URL', 'Symbol @', 'Redirecting //', 'Prefix/Suffix',
        'Sub Domains', 'HTTPS', 'Domain Registration Length', 'Favicon', 'Non-Standard Port',
        'HTTPS Domain URL', 'Request URL', 'Anchor URL', 'Links in &lt;script&gt; tags',
        'Server Form Handler', 'Info Email', 'Abnormal URL', 'Website Forwarding', 'Status Bar Customization',
        'Disable Right Click', 'Using Popup Window', 'Iframe Redirection', 'Age of Domain',
        'DNS Recording', 'Website Traffic', 'Page Rank', 'Google Index', 'Links Pointing to Page',
        'Stats Report'
    ];

    // Automatically submit form if URL is provided in the query params
    const urlParam = getQueryParam('url');
    if (urlParam) {
        const formattedUrl = formatAndValidateUrl(urlParam);
        if (formattedUrl) {
            $('#url').val(formattedUrl); // Set the URL input value
            setTimeout(function() {
                $('#urlForm').trigger('submit'); // Automatically submit the form
            }, 100);
        } else {
            alert('Invalid URL provided.');
        }
    }

    // Handle form submission
    $('#urlForm').on('submit', function(event) {
        event.preventDefault();  // Prevent default form submission

        let urls = $('#url').val().split('\n').filter(url => url.trim() !== ''); // Split input by new lines and remove empty strings
        if (urls.length === 0) {
            alert("Please enter at least one URL.");
            return;
        }

        $('#extractedFeatures').collapse('hide');  // Hide features section
        $('#featuresList').html(''); // Clear previous features list
        $('#results').html('');  // Clear previous results
        $('#loadingSpinner').show();  // Show the loading spinner

        urls.forEach(function(url, index) {
            url = formatAndValidateUrl(url);
            if (url) {
                updateUrlParams(url);  // Update the URL parameters for each valid URL
                checkUrl(url, index);  // Submit each URL via AJAX
            } else {
                alert('Please enter a valid URL.');
            }
        });
    });

    // Function to submit a URL and process the result
    function checkUrl(url, index) {
        $.ajax({
            url: '/check_url',  // Adjust the URL if your Flask endpoint is different
            method: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({ url: url }),
            success: function(response) {
                $('#loadingSpinner').hide();  // Hide the loading spinner when the first response is received

                // Create unique IDs for each result and its features for toggling
                const resultId = `result-${index}`;
                const featuresId = `features-${index}`;

                // Append the results for each URL
                let resultHtml = `
                    <div class="card mb-3">
                        <div class="card-header" id="${resultId}">
                            <strong>Result for: ${url}</strong>
                            <button class="btn btn-link" data-toggle="collapse" data-target="#${featuresId}" aria-expanded="false" aria-controls="${featuresId}">
                                Toggle Features
                            </button>
                        </div>
                        <div class="card-body">
                            <p class="${response.message.includes('phishing site') ? 'text-danger' : 'text-success'}">
                                ${response.message}
                            </p>
                        </div>
                        <div id="${featuresId}" class="collapse">
                            <div class="card-body">
                                <table class="table table-striped table-bordered">
                                    <thead>
                                        <tr>
                                            <th>Feature</th>
                                            <th>Value</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                `;

                // Populate the features list for the current URL
                if (response.features) {
                    response.features.forEach(function(feature, index) {
                        let label = featureLabels[index] || 'Unknown';
                        let valueClass = feature === -1 ? 'text-danger' :
                                         feature === 0 ? 'text-warning' : 'text-success';
                        let valueText = feature === -1 ? 'Potentially Malicious' :
                                        feature === 0 ? 'Suspicious' : 'Likely Safe';
                        
                        resultHtml += `
                            <tr>
                                <td>${label}</td>
                                <td class="${valueClass}">${valueText}</td>
                            </tr>
                        `;
                    });
                } else {
                    resultHtml += `
                        <tr>
                            <td colspan="2">No features available</td>
                        </tr>
                    `;
                }

                resultHtml += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;

                $('#results').append(resultHtml);  // Append result for each URL

                $('#results').collapse('show');  // Show the results section after each URL
            },
            error: function(resp) {
                $('#loadingSpinner').hide();  // Hide the loading spinner in case of error
                alert(`Error checking ${url}: ${resp.responseJSON.error}`);
            }
        });
    }
});
