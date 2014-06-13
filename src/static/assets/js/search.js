<script type="text/javascript">
(function($, document, location, window) {
    $(document).ready(function() {
        // Attach datetimepicker widgets to start and end time fields
        $('#start').datetimepicker();
        $('#end').datetimepicker();

        // Create a socket to communicate with our Flask app
        var socket = io.connect('http://' + document.domain + ':' +
                                location.port + '/search');

        // Create empty object to hold stock items
        var attendees = {};
        var form_items = [];

        // Split value of the 'items' field on commas
        if($("#users").attr('value') != "") {
            form_items = $("#users").attr('value').split(',');
        }

        // Save each item as the key and value in the 'attendees' object
        $.each(form_items, function(k, v) {
            attendees[v] = v;
        });

        // Create a list item with a clickable dismiss icon.  When clicked, the
        // item is removed both from the displayed list and from the 'obj'
        // object
        var liDismiss = function(obj, v) {
            var btn = $('<button/>', {
                type: 'button',
                class: 'close pull-right',
                html: '&times',
                click: function() {
                    $(this).parent().remove();
                    delete obj[v];
                }
            }).attr('aria-hidden', true);

            var li = $('<li/>', {
                class: 'list-group-item',
            }).text(v).append(btn);
            return li;
        };

        // Curried form of liDismiss(), with 'attendees' passed as the object
        var liDismissAttendees = function(v) {
            return liDismiss(attendees, v);
        }

        // For each item in 'attendees', construct a list item
        var buildList = function() {
            // Clear out list
            $('#attendees').empty();

            // Replace list with new list containing all items of interest
            $.each(attendees, function(i, e) {
                $('#attendees').append(liDismissAttendees(e));
            });
        };

        var getUserNames = function(name) {
            var names = value['value'].split(/\W+/),
                lname = names.pop(),
                fname = names.shift();

            if(lname.length === 0 || fname.length === 0) {
                return null;
            } else {
                return {name: {'fname': fname, 'lname': lname}};
            }
        };

        buildList();

        socket.on('items', function(msg) {
            // Creates a suggestion engine based on the 'item' field of the
            // list of objects passed in 'msg.data'
            var onids = new Bloodhound({
                name: 'onids',
                datumTokenizer: Bloodhound.tokenizers.obj.whitespace('onids'),
                queryTokenizer: Bloodhound.tokenizers.whitespace,
                local: msg.data,
            });

            // Begins processing of dataset
            onids();

            $('#finduser .typeahead').typeahead(
                {
                    hint: true,
                    highlight: true,
                    minLength: 1,
                },
                {
                    name: 'onids',
                    displayKey: 'onids',
                    source: items.ttAdapter(),
                    templates: {
                        empty: ['<div class="empty message">',
                                'unable to find any matching ONIDS or names',
                                '</div>'].join('\n'),
                        suggestion:
                        Handlebars.compile(['<div class="media">',
                                            '<span class="glyphicon glyphicon-user media-object pull-left"></span>',
                                            '<div class="media-body">',
                                            '<h4 class="media-heading">{{ name }}</div>',
                                            '<p>Quantity: {{ onid }}</p>',
                                            '</div>',
                                            '</div>',].join('\n')),
                    }
                }
            );
        });

        // Callback for 'validate' event from server.  We expect to receive a
        // Boolean value for 'msg.is_valid'
        socket.on('validate', function(msg) {
            if(msg.is_valid) {
                // Find the parent form of the submit button, and submit it
                var form = $("#buy").parents().find('form')[0];
                $(form).submit();
            } else {
                // Add error signaling and error message to form input
                $("#finduser").addClass("has-error");
                var label = $("label[for='item']");
                // Only add message if there's not already one there
                if(label.find("p").length < 1) {
                    label.append("<p>Must select at least one item</p>");
                }
            }
        });

        $("#findtimes").click(function(event) {
            console.log("Searching....")
            // Add user-chosen items to array
            var attendees_arr = [];
            $.each(attendees, function(k,v) {
                attendees_arr.push(v);
            });

            // Set the 'value' attribute of the hidden list field to a
            // comma-separated list of the user's selections
            $("#users").attr('value', attendees_arr.join(','));

            // Send the form data back to the app
            socket.emit('submit', {
                            "items": attendees_arr ,
                            "csrf_token": $("#csrf_token").val(),
                        });

            // Prevent form submission
            event.preventDefault();
        });

        $('#adduser').click(function (event) {
            // Grab entered text
            attendee = $("#onid").val();

            name_query = getUserNames(attendee);

            if(name_query === null)
                // TODO add error class to parent

            console.log(JSON.stringify(name_query));
            $.ajax({
                type: 'POST',
                url: '{{ url_for("run_query") }}',
                contentType: 'application/json',
                data: JSON.stringify(name_query),
                success: function(result) {
                    console.log('search result: ' + JSON.stringify(result));
                },
                error: function(e) {
                    console.log(e);
                }
            });

            /*
            // Add to the dictionary, if it's not already there
            if(! attendees[attendee] && attendee != "") { attendees[attendee] = attendee; }

            buildList();

            // Reset text field
            $("#onid").val("");
            */

            // Stop whatever would have happened otherwise
            event.preventDefault();
        });
    });
})(jQuery, document, location, window);
</script>
