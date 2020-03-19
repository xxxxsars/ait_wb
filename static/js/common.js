/**
 * Created by Andy on 2020/1/10.
 */


//auto close alert  after 4 seconds.
$(".alert").delay(4000).slideUp(200, function () {
    $(this).alert('close');

});


$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

function ajax_download(url) {

                $.ajax({
                    "consumes": [],
                    "produces": [
                        "application/octet-stream"
                    ],
                    url: url,
                    xhrFields: {
                        // keep binary file
                        responseType: "blob"
                    }
                }).done((response, status, xhr) => {
                    // 這邊一定要用原生的 document.createElement
                    // jQuery 沒辦法真的模擬原生的 click event

                    const a = document.createElement("a");
                    // 給下載回來的資料產生一個網址
                    const url = URL.createObjectURL(response);
                    a.style = "display: none";

                    //get original filename
                    var f = (xhr.getResponseHeader('Content-Disposition').split("=")[1]);

                    var dt = new Date();
                    a.download = dt.toISOString() +".zip";
                    a.href = url;

                    a.click();
                    setTimeout(() => URL.revokeObjectURL(url), 5000)
                });

}

function ajax_loading(content) {
    $(document).ajaxStart(function () {
        $("body").hide();

        $(".load_panel").each(function () {
            $(this).remove()
        });

        $("html").append(
            '<div class="load_panel" style="width: 100%; height: 100%;">' +
            '  <div class="ui active inverted dimmer">' +
            '    <div class="ui text loader">'+ content +'</div>' +
            '  </div>' +
            '</div>');


    });

    $(document).ajaxComplete(function () {
        $(".load_panel").each(function () {
            $(this).remove()
        });

        // remove load.css
        $("#load_css").remove();
        $("body").show()
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function station_table_clone(part_number, index) {
            return '<tr>\n' +
                '                        <td colspan="3">\n' +
                '                            <div class="form-group">\n' +
                '                                <div class="input-group mb-3">\n' +
                '                                    <div style="margin-left: 10%">\n' +
                '                                        <select name="' + part_number + '" id="station_' + index + '"\n' +
                '                                                class="add_dropdwon stations selectpicker show-tick"\n' +
                '                                                data-live-search="true" title="Nothing selected">\n' +
                '                                            <option value="PCBA_FT1">PCBA_FT1</option>\n' +
                '                                            <option value="PCBA_FT2">PCBA_FT2</option>\n' +
                '                                            <option value="PCBA_FT3">PCBA_FT3</option>\n' +
                '                                            <option value="PCBA_FT4">PCBA_FT4</option>\n' +
                '                                            <option value="PCBA_FT5">PCBA_FT5</option>\n' +
                '                                            <option value="PCBA_FT6">PCBA_FT6</option>\n' +
                '                                            <option data-divider="true"></option>\n' +
                '                                            <option value="ASSY_PCBA_FT1">ASSY_PCBA_FT1</option>\n' +
                '                                            <option value="ASSY_PCBA_FT2">ASSY_PCBA_FT2</option>\n' +
                '                                            <option value="ASSY_PCBA_FT3">ASSY_PCBA_FT3</option>\n' +
                '                                            <option value="ASSY_PCBA_FT4">ASSY_PCBA_FT4</option>\n' +
                '                                            <option value="ASSY_PCBA_FT5">ASSY_PCBA_FT5</option>\n' +
                '                                            <option value="ASSY_PCBA_FT6">ASSY_PCBA_FT6</option>\n' +
                '                                            <option data-divider="true"></option>\n' +
                '                                            <option value="ASSY_FT1">ASSY_FT1</option>\n' +
                '                                            <option value="ASSY_FT2">ASSY_FT2</option>\n' +
                '                                            <option value="ASSY_FT3">ASSY_FT3</option>\n' +
                '                                            <option value="ASSY_FT4">ASSY_FT4</option>\n' +
                '                                            <option value="ASSY_FT5">ASSY_FT5</option>\n' +
                '                                            <option value="ASSY_FT6">ASSY_FT6</option>\n' +
                '                                            <option data-divider="true"></option>\n' +
                '                                            <option value="ASSY_DBA_FT1">ASSY_DBA_FT1</option>\n' +
                '                                            <option value="ASSY_DBA_FT2">ASSY_DBA_FT2</option>\n' +
                '                                            <option value="ASSY_DBA_FT3">ASSY_DBA_FT3</option>\n' +
                '                                            <option value="ASSY_DBA_FT4">ASSY_DBA_FT4</option>\n' +
                '                                            <option value="ASSY_DBA_FT5">ASSY_DBA_FT5</option>\n' +
                '                                            <option value="ASSY_DBA_FT6">ASSY_DBA_FT6</option>\n' +
                '                                            <option data-divider="true"></option>\n' +
                '                                        </select>\n' +
                '                                    </div>\n' +
                '                                    <div class="input-group-append">\n' +
                '                                        <button class="btn btn-outline-danger specific-st-remove" type="button"><i\n' +
                '                                                class="fas fa-trash"></i>\n' +
                '                                        </button>\n' +
                '                                    </div>\n' +
                '                                </div>\n' +
                '                            </div>\n' +
                '                        </td>\n' +
                '                    </tr>'
        }
        function ajax_del_station(project_name, part_number, station_name, remove_tr) {
            if (station_name != "") {
                if (confirm("Are you sure to delete this row?")) {
                    $.ajax({
                        url: "/project/station_delete/", // the endpoint,commonly same url
                        type: 'POST',
                        data: {
                            csrfmiddlewaretoken: getCookie("csrftoken"),
                            "project_name": project_name,
                            "part_number": part_number,
                            "station_name": station_name
                        },

                        success: function (json) {
                            var remove_select = remove_tr.find('select');
                            $('#set_station_form').bootstrapValidator('removeField', remove_select);
                            remove_tr.remove();
                            $("#save_btn").removeAttr('disabled');
                        },

                        //處理失敗時會做的動作
                        error: function (xhr, errmsg, err) {
                            console.log("part number not in database");
                            var remove_input = ($('select[name="' + part_number + '"]').last());
                            $('#set_station_form').bootstrapValidator('removeField', remove_input);
                            remove_tr.remove();
                            $("#save_btn").removeAttr('disabled');
                        }
                    });
                }
            } else {
                var remove_input = ($('select[name="' + part_number + '"]').last());
                $('#set_station_form').bootstrapValidator('removeField', remove_input);
                remove_tr.remove();
                $("#save_btn").removeAttr('disabled');
            }
        }