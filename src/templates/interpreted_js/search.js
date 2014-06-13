(function($, document, location, window) {
    $(document).ready(function() {
        // Attach datetimepicker widgets to start and end time fields
        $('#start').datetimepicker();
        $('#end').datetimepicker();


        // Create empty object to attendees
        var attendees = {};

        // Create a list item with a clickable dismiss icon.  When clicked, the
        // item is removed both from the displayed list and from the 'obj'
        // object
        var liDismiss = function(obj, key) {
            var btn = $('<button/>', {
                type: 'button',
                class: 'close pull-right',
                html: '&times',
                click: function() {
                    $(this).parent().remove();
                    delete obj[key];
                }
            }).attr('aria-hidden', true);

            var li = $('<li/>', {
                class: 'list-group-item',
            }).text(key).append(btn);
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
            $.each(attendees, function(key, value) {
                console.log("index: " + key + "; value: " + value);
                $('#attendees').append(liDismissAttendees(key));
            });
        };

        var getUserNames = function(name) {
            var names = name.split(/\W+/),
                lname = names.pop(),
                fname = names.shift();

            console.log("from getUserNames: " + name);

            if(lname.length === 0 || fname.length === 0) {
                return null;
            } else {
                var ret = {};
                ret[name] = {'fname': fname, 'lname': lname};
                return ret;
            }
        };

        // From http://css-tricks.com/snippets/jquery/serialize-form-to-json/
        $.fn.serializeObject = function() {
            var obj = {};
            var arr = this.serializeArray();

            $.each(arr, function() {
                if (obj[this.name]) {
                    if (!obj[this.name].push) {
                        obj[this.name] = [obj[this.name]];
                    }
                    obj[this.name].push(this.value || '');
                } else {
                    obj[this.name] = this.value || '';
                }
            });
            return obj;
        };


        $("#findtimes").click(function(event) {
            console.log("Searching....")

            form_arr = $(this).parent().serializeObject();
            form_arr['users'] = attendees;
            console.log(JSON.stringify(form_arr));

            /*
            // Send the form data back to the app
            socket.emit('submit', {
                            "items": attendees_arr ,
                            "csrf_token": $("#csrf_token").val(),
                        });
            */
            $.ajax({
                type: 'POST',
                url: '{{ url_for("find_times") }}',
                contentType: 'application/json',
                data: JSON.stringify(form_arr),
                success: function(result) {
                    console.log('search result: ' + JSON.stringify(result));
                },
                error: function(e) {
                    console.log(e);
                }
            });

            // Prevent form submission
            event.preventDefault();
        });

        $('#adduser').click(function (event) {
            // Grab entered text
            attendee = $("#onid").val();
            console.log(attendee);

            name_query = getUserNames(attendee);
            console.log(JSON.stringify(name_query));

            if(name_query === null)
                // TODO add error class to parent
                ;

            console.log(JSON.stringify(name_query));
            $.ajax({
                type: 'POST',
                url: '{{ url_for("run_query") }}',
                contentType: 'application/json',
                data: JSON.stringify(name_query),
                success: function(result) {
                    //console.log('search result: ' + JSON.stringify(result));
                    result_data = result['onids'][0];
                    console.log('search result: ' + JSON.stringify(result_data));
                    onid = result_data['onid'];
                    if(onid != null) {
                        console.log("onid is not null");
                        fname = result_data['fname'];
                        lname = result_data['lname'];

                        console.log(JSON.stringify(name_query))

                        query_fname = name_query[attendee]['fname']
                        query_lname = name_query[attendee]['lname']

                        if(fname.toLowerCase() === query_fname.toLowerCase()
                           && lname.toLowerCase() === query_lname.toLowerCase()) {
                            console.log("Adding attendee...");
                            // Add to the dictionary, if it's not already there
                            if(! attendees[attendee] && attendee != "") {
                                attendees[attendee] = result_data;
                            }

                            buildList();

                            // Reset text field
                            $("#onid").val("");
                            console.log(JSON.stringify(attendees));
                        } else {
                            // TODO: handle errors
                            ;
                        }
                    } else {
                        // TODO: handle errors
                        ;
                    }

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
