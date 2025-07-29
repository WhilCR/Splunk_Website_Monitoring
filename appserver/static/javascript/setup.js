require([
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/simplexml/ready!'
], function($) {

    const collectionUrl = "/servicesNS/nobody/Splunk_Website_Monitoring/storage/collections/data/url_monitoring_targets";

    function loadURLs() {
        $.ajax({
            url: collectionUrl,
            type: "GET",
            success: function(data) {
                const urls = data.map(entry => `<li>${entry.url} <button class="remove-url" data-id="${entry._key}">Remove</button></li>`);
                $('#url-list').html(urls.join(""));
            }
        });
    }

    function addURL(url) {
        $.ajax({
            url: collectionUrl,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ url: url }),
            success: function() {
                $('#new-url').val('');
                $('#save-status').text("URL added.");
                loadURLs();
            }
        });
    }

    function removeURL(id) {
        $.ajax({
            url: `${collectionUrl}/${id}`,
            type: "DELETE",
            success: function() {
                $('#save-status').text("URL removed.");
                loadURLs();
            }
        });
    }

    $('#add-url').on('click', function() {
        const url = $('#new-url').val().trim();
        if (url.startsWith("http")) {
            addURL(url);
        } else {
            $('#save-status').text("Invalid URL format.");
        }
    });

    $('#url-list').on('click', '.remove-url', function() {
        const id = $(this).data('id');
        removeURL(id);
    });

    loadURLs();
});
