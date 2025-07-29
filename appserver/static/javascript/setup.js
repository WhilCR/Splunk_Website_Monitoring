require([
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/simplexml/ready!'
], function($, mvc) {

    function fetchIndexes() {
        $.ajax({
            url: "/en-US/splunkd/__raw/services/data/indexes?output_mode=json",
            type: "GET",
            success: function(data) {
                var entries = data.entry || [];
                var dropdown = $('#index-dropdown');
                dropdown.empty();
                entries.forEach(function(item) {
                    var name = item.name;
                    dropdown.append(`<option value="${name}">${name}</option>`);
                });
            },
            error: function(err) {
                $('#status-msg').text("Error loading indexes.").css("color", "red");
            }
        });
    }

    function saveIndexSelection(index) {
        $.ajax({
            url: "/servicesNS/nobody/Splunk_Website_Monitoring/storage/collections/data/url_monitoring_config",
            type: "POST",
            data: JSON.stringify({ index: index }),
            contentType: "application/json",
            success: function() {
                $('#status-msg').text("Configuration saved successfully.");
            },
            error: function() {
                $('#status-msg').text("Failed to save config.").css("color", "red");
            }
        });
    }

    fetchIndexes();

    $('#save-config').on('click', function() {
        const selectedIndex = $('#index-dropdown').val();
        saveIndexSelection(selectedIndex);
    });
});
