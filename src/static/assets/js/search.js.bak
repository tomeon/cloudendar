(function($, document, window) {
    $(document).ready(function() {
        // Attach datetimepicker widgets to start and end time fields
        $('#start').datetimepicker();
        $('#end').datetimepicker();

        // Create empty object to hold ONID usernames
        var attendees = {};

        var form_onids = $("#users").attr('value').split(',');
        $.each(form_onids, function(k, v) {
            attendees[v] = v;
        });

        // Create a socket to communicate with our Flask app
        var socket = io.connect('http://' + document.domain + ':' + location.port + '/search');

        var buildList = function() {
            // Clear out list
            $('#attendees').empty();

            // Replace list with new list containing all members of interest
            $.each(attendees, function(i, e) {
                $('#attendees').append(liDismissAttendees(e));
            });
        };

        // This returns a function that parses user-entered text and matches
        // it against a list of valid values
        //var substrMatcher = function(strs) {
        //    return function findMatches(q, cb) {
        //        var matches, substrRegex;
        //        matches = [];
        //        substrRegex = new RegExp(q, 'i');
        //        $.each(strs, function(i, str) {
        //            if(substrRegex.test(str)) {
        //                matches.push({value: str});
        //            }
        //        });

        //        cb(matches);
        //    };
        //};

        var liDismiss = function(list, v) {
            var btn = $('<button/>', {
                type: 'button',
                class: 'close pull-right',
                html: '&times',
                click: function() {
                    $(this).parent().remove();
                    delete list[v];
                }
            }).attr('aria-hidden', true);

            var li = $('<li/>', {
                class: 'list-group-item',
            }).text(v).append(btn);
            return li;
        };

        var liDismissAttendees = function(v) {
            return liDismiss(attendees, v);
        }

        buildList();

        var data = [{ "a" : "b" },
                    { "a" : "b"},];
        console.log(data);
        for(var p in data) {
            console.log(p);
            for(var k in data[p]) {
                console.log(k + ": " + data[p][k]);
            }
        }

        socket.on('onids', function(msg) {
            var onids = new Bloodhound({
                name: 'onids',
                datumTokenizer: Bloodhound.tokenizers.obj.whitespace('onid'),
                queryTokenizer: Bloodhound.tokenizers.whitespace,
                local: msg.data,
            });

            // Begins processing of dataset
            onids.initialize();

            $('#search .typeahead').typeahead(
                {
                    hint: true,
                    highlight: true,
                    minLength: 1,
                },
                {
                    name: 'onids',
                    displayKey: 'onid',
                    source: onids.ttAdapter(),
                    templates: {
                        empty: ['<div class="empty message">',
                                'unable to find any matching ONIDs or names',
                                '</div>'].join('\n'),
                        suggestion:
                        Handlebars.compile(['<div class="media">',
                                            '<span class="glyphicon glyphicon-user media-object pull-left"></span>',
                                            '<div class="media-body">',
                                            '<h4 class="media-heading">{{ name }}</div>',
                                            '<p>ONID: {{ onid }}, dept: Basketweaving</p>',
                                            '</div>',
                                            '</div>',].join('\n')),
                    }
                }
            );
        });

        socket.on('result', function(msg) {
            alert(msg.data);
            //$('#users').append(msg.data + ', ');
        });

        $("#submit").click(function(event) {
            var attendees_arr = [];
            $.each(attendees, function(k,v) {
                attendees_arr.push(v);
            });

            $("#users").attr('value', attendees_arr.join(','));
            console.log($('#users').attr('value'));
        });

        $('#adduser').click(function (event) {
            // Grab entered text
            attendee = $("#onid").val();

            // Add to the dictionary, if it's not already there
            if(! attendees[attendee] && attendee != "") { attendees[attendee] = attendee; }

            buildList();

            // Reset text field
            $("#onid").val("");

            // Stop whatever would have happened otherwise
            event.preventDefault();
        });
    });
})(jQuery, document, window);
