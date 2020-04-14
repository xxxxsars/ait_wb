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
                '                                            <option value="ASSY_OBA_FT1">ASSY_OBA_FT1</option>\n' +
                '                                            <option value="ASSY_OBA_FT2">ASSY_OBA_FT2</option>\n' +
                '                                            <option value="ASSY_OBA_FT3">ASSY_OBA_FT3</option>\n' +
                '                                            <option value="ASSY_OBA_FT4">ASSY_OBA_FT4</option>\n' +
                '                                            <option value="ASSY_OBA_FT5">ASSY_OBA_FT5</option>\n' +
                '                                            <option value="ASSY_OBA_FT6">ASSY_OBA_FT6</option>\n' +
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