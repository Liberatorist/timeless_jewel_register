const time_formatter = new Intl.RelativeTimeFormat('en', { 
    numeric: 'auto',
    style: 'long',
    localeMatcher: 'best fit'
});
const currentDate = new Date(Date.now());

$(document).ready(function () {
    var input_effect = $('#min_effect');
    var input_effect_pp = $('#min_effect_pp');
    var input_max_points = $('#max_points');
    var input_max_price = $('#max_price');
    var input_position = $('#position');
    var input_jewel_type = $('#jewel');
    var input_requirements = $('#requirements');
    var input_seed = $('#seed');

    // Custom range filtering function
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        var filter_min_effect = parseInt(input_effect.val(), 0);
        var filter_min_effect_pp = parseFloat(input_effect_pp.val(), 0);
        var filter_max_points = parseInt(input_max_points.val(), 0);
        var filter_max_price = parseFloat(input_max_price.val(), 0);
        var filter_position = String(input_position.val());
        var filter_jewel_type = parseFloat(input_jewel_type.val(), 0);
        var filter_requirements = String(input_requirements.val());
        var filter_seed = String(input_seed.val());

        var data_type = parseFloat(data[1]) || 0;
        var data_position = String(data[2]) || 0;
        var data_seed = String(data[3]) || 0;
        var data_effect = parseFloat(data[4]) || 0;
        var data_points = parseFloat(data[5]) || 0;
        var data_effect_pp = parseFloat(data[6]) || 0;
        var data_requirements = String(data[7]) || 0;
        var data_price = parseFloat(data[8]) || 0;

        
        if (data_effect < filter_min_effect){ return false; }
        if (data_effect_pp < filter_min_effect_pp){ return false; }
        if (data_points > filter_max_points){ return false; }
        if (filter_position != "null" && filter_position != "Any" && data_position != filter_position){ return false; }
        if (!isNaN(filter_jewel_type) && data_type != filter_jewel_type ){ return false; }
        if ((filter_requirements == "no_ie" || filter_requirements == "basic") && data_requirements == "i"){ return false; }
        if ((filter_requirements == "no_anoint" || filter_requirements == "basic") && data_requirements == "a"){ return false; }
        if (!isNaN(filter_seed) && data_seed.toLowerCase().indexOf(filter_seed.toLowerCase()) === -1 ){ return false; }
        if (data_price > filter_max_price){ return false; }
        return true;
    })
    
    
    $('#divide').on('change', function () {
        table.rows().invalidate('data');
        table.draw(false);
    });


    var table = $('#data').DataTable({
        retrieve: true,
        columnDefs: [
            {   
                render: function (data, type, row) {
                    var div = parseFloat(row[4]) / parseFloat(row[5]);
                    return Math.round(div * 100) / 100;
                },
                targets:6
            },
            {   
                render: function (data, type, row) {
                    if (row[8] ==""){return ""}
                    return Math.round(parseFloat(row[8]) * 100) / 100;
                },
                targets:8
            },
            {   
                render: function (data, type, row) {
                    if (row[9] ==""){return "never"}
                    
                    const last_update = new Date(row[9] + "Z");
                    const minutes = (last_update - currentDate) / 60000
                    if (Math.abs(minutes) < 60){
                        return time_formatter.format(Math.round(minutes), 'minute');
                    }
                    const hours = minutes / 60
                    if (Math.abs(hours) < 24){
                        return time_formatter.format(Math.round(hours), 'hour')
                    }
                    const days = hours / 24
                    return  time_formatter.format(Math.round(days), 'day');
                },
                targets:9
            },
            {orderable: false, targets: 10},
            {orderable: false, targets: 0},
            
        ]
    
    });

    $('#data_filter').hide();
    // Changes to the inputs will trigger a redraw to update the table
    input_effect.on('input', function () {
        table.draw();
    });
    input_effect_pp.on('input', function () {
        table.draw();
    });
    input_max_points.on('input', function () {
        table.draw();
    });
    input_position.on('input', function () {
        table.draw();
    });
    input_jewel_type.on('input', function () {
        table.draw();
    });
    input_requirements.on('input', function () {
        table.draw();
    });
    input_max_price.on('input', function () {
        table.draw();
    });
    input_seed.on('input', function () {
        table.draw();
    });
});

$('#data tfoot tr').appendTo('#data thead');
