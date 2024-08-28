$(document).ready(function() {
    // Function to get URL parameters
    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    // Function to validate a URL and add http:// if necessary
    function formatAndValidateUrl(urlString) {
        // Check if the URL starts with http://, https://, or another protocol
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
            // Delay the form submission slightly to ensure the DOM is ready
            setTimeout(function() {
                $('#urlForm').trigger('submit'); // Automatically submit the form
            }, 100); // Adjust the delay as necessary
        } else {
            alert('Invalid URL provided.');
        }
    }

    // Handle form submission
    $('#urlForm').on('submit', function(event) {
        event.preventDefault();  // Prevent default form submission

        let url = $('#url').val();

        url = formatAndValidateUrl(url);
        if (!url) {
            alert('Please enter a valid URL.');
            return;
        }

        // Update the URL parameters
        updateUrlParams(url);

        $('#results').collapse('hide');  // Hide previous results
        $('#loadingSpinner').show();  // Show the loading spinner

        $.ajax({
            url: '/check_url',  // Adjust the URL if your Flask endpoint is different
            method: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({ url: url }),
            success: function(response) {
                $('#loadingSpinner').hide();  // Hide the loading spinner
                
                // Display the results
                $('#resultText').html(`<strong>${url}</strong> ${response.message}`);
                $('#resultText').removeClass('text-danger text-success');
                if (response.is_phishing || response.message.includes('not reachable')) {
                    $('#resultText').addClass('text-danger');
                } else {
                    $('#resultText').addClass('text-success');
                }
                
                // Populate the features list
                if (response.features) {
                    let featuresHtml = '';
                    response.features.forEach(function(feature, index) {
                        let label = featureLabels[index] || 'Unknown';
                        let valueClass = feature === -1 ? 'text-danger' :
                                         feature === 0 ? 'text-warning' : 'text-success';
                        let valueText = feature === -1 ? 'Potentially Malicious' :
                                        feature === 0 ? 'Suspicious' : 'Likely Safe';
                        
                        featuresHtml += `
                            <tr>
                                <td>${label}</td>
                                <td class="${valueClass}">${valueText}</td>
                            </tr>
                        `;
                    });
                    $('#featuresList').html(featuresHtml);
                    $('#extractedFeatures').collapse('show');  // Show features
                } else {
                    $('#extractedFeatures').collapse('hide');
                }

                $('#results').collapse('show');  // Show the results section
            },
            
            error: function(xhr, status, error) {
                $('#loadingSpinner').hide();  // Hide the loading spinner
                alert('An error occurred: ' + error);
            }
        });
    });

    // Handle the toggle icon change on collapse show/hide
    $('#extractedFeatures').on('shown.bs.collapse', function () {
        $(this).find('.toggle-icon').removeClass('fa-chevron-right').addClass('fa-chevron-down');
    }).on('hidden.bs.collapse', function () {
        $(this).find('.toggle-icon').removeClass('fa-chevron-down').addClass('fa-chevron-right');
    });
});
