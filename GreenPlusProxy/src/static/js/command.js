

$(function () {
    $('#btn_send').click(function () {
        // var device_id = $('#device_id').val();
        var command = $('#device_command').val();
        var device_id = $("#device_list").val();
        sendCommand(device_id,command);
        // alert(JSON.stringify(orderIds));
    });

     $.ajax({
        url: '/api/device/actives',
        type: 'get',
        // dataType: 'json',
        async: true
    }).done(function (data) {
        $.each(data.result,function (index, value) {
            var item = `<option value='${value.device_id}'>${value.name} - ${value.device_id}</option>`;
            $('#device_list').append(item);
        });

    });

});

function  sendCommand(device_id,command) {
    // 一键平仓（市场限价平掉所有仓位)
    $.ajax({
        url: '/api/command',
        data: {
            device_id:device_id,
            command:command
        },
        type: 'post',
        // dataType: 'json',
        async: true
    }).done(function (data) {
        // alert("send:" + JSON.stringify(data));
    });

}