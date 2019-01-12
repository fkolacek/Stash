    function show_repositories() {
        $.get("/repos", function (data) {
            var counter = 0;

            $("table#stash tbody").empty();

            $.each(data, function (i, item) {
                $("<tr>").append(
                    $("<td>").text(item.id),
                    $("<td>").append($("<a>", {href: '/detail/' + item.name, text: item.name})),
                    $("<td>").text(item.type),
                    $("<td>").text(item.description),
                    $("<td>").text(item.created),
                    $("<td>").text(item.score)
                ).appendTo('table#stash tbody');

                counter++;
                console.log(item);
            });

            if (counter == 0) {
                $("<tr>").append(
                    $("<td>")
                        .attr('colspan', 5)
                        .addClass('text-center')
                        .text('There are no stashed projects yet!')
                ).appendTo('table#stash tbody');
            }
        });
    }