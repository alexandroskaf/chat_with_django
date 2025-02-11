hide_fields();

function hide_fields(){
  $('#select_epsad_choice').hide(1);
  $('#select_related_dig_connection').hide(1);
  $('#select_related_pyrseia_server').hide(1);
  $('#select_related_broadband_transceiver').hide(1);
  $('#select_related_satellite_node').hide(1);
  $('#select_related_harp_correspondent').hide(1);
  $('#select_related_hermes_node').hide(1);
  $('#select_related_hermes_connection').hide(1);
  $('#select_hermes_choice').hide(1);
  $('#show_dispatcher_form_select').hide(1);
}


// Function that handles the select inputs based on mean
$('#id_means_new_failure').change(function () {
  var means_name = $(this).find(':selected')[0].label;
  var unit_name = $("#id_unit_new_failure").find(':selected')[0].label;

  related_data_fetch('/ajax/get_failure_types/', means_name, unit_name, '#id_failure_type', 'failure_types')

  if (means_name == "ΔΙΔΕΣ") {
    $('input:radio[name="epsad_choice"]').filter('[value=epsad_internal]').prop('checked', false);
    console.log("espad_internal unchecked");
    $('input:radio[name="epsad_choice"]').filter('[value=epsad_external]').prop('checked', false);
    console.log("espad_external_unchecked");

    $("#id_related_epsad_external_new_failure").find('option').remove().end()
    $("#id_related_epsad_internal_new_failure").find('option').remove().end()

    related_data_fetch('/ajax/get_related_data_dig/', means_name, unit_name, '#id_related_dig_connection_new_failure', 'related_dig_connections');
    hide_fields();
    $('#select_related_dig_connection').show("slow");
  }
  else if (means_name == "ΕΨΑΔ-ΑΤΚ") {
    console.log($('input:radio[name="epsad_choice"]'));
    hide_fields();
    $('input:radio[name="epsad_choice"]').filter('[value=epsad_internal]').prop('checked', true);
    $('#select_epsad_choice').show("slow");
    epsad_internal_checked(means_name, unit_name);
  }
  else if (means_name == "ΣΕΖΜ-ΕΡΜΗΣ") {
    hide_fields();
    $('input:radio[name="hermes_choice"]').filter('[value=hermes_node]').prop('checked', true);
    $('#select_hermes_choice').show("slow");
    hermes_node_checked(means_name, unit_name);
  } 
  else if (means_name == "ΠΥΡΣΕΙΑ") {
    hide_fields();
    related_data_fetch('/ajax/get_related_data_pyrseia/', means_name, unit_name, '#id_related_pyrseia_server_new_failure', 'related_pyrseia_server');
    $('#select_related_pyrseia_server').show("slow");
  }
  else if (means_name == "ΕΥΡΥΖΩΝΙΚΟ") {
    hide_fields();
    related_data_fetch('/ajax/get_related_data_broadband/', means_name, unit_name, '#id_related_broadband_transceiver_new_failure', 'related_broadband_transceiver');
    $('#select_related_broadband_transceiver').show("slow");
  }
  else if (means_name == "ΔΟΡΥΦΟΡΙΚΑ") {
    related_data_fetch('/ajax/get_related_data_satellite/', means_name, unit_name, '#id_related_satellite_node_new_failure', 'related_satellite_node');
    hide_fields();
    $('#select_related_satellite_node').show("slow");
  }
  else if (means_name == "HARP") {
    related_data_fetch('/ajax/get_related_data_harp/', means_name, unit_name, '#id_related_harp_correspondent_new_failure', 'related_harp_correspondent');
    hide_fields();
    $('#select_related_harp_correspondent').show("slow");
  }
  else {
    hide_fields();
  }
});

// Function that handles the select inputs based on unit
$('#id_unit_new_failure').change(function () {
  var means_name = $("#id_means_new_failure").find(':selected')[0].label;
  var unit_name = $(this).find(':selected')[0].label;

  if (means_name == "ΔΙΔΕΣ") {
    $('input:radio[name="epsad_choice"]').filter('[value=epsad_internal]').prop('checked', false);
    console.log("espad_internal unchecked");
    $('input:radio[name="epsad_choice"]').filter('[value=epsad_external]').prop('checked', false);
    console.log("espad_external_unchecked");
    console.log($('input:radio[name="epsad_choice"]'));

    related_data_fetch('/ajax/get_related_data_dig/', means_name, unit_name, '#id_related_dig_connection_new_failure', 'related_dig_connections');
  }
  if (means_name == "ΕΨΑΔ-ΑΤΚ") {
    console.log($('input:radio[name="epsad_choice"]'));
    var epsad_internal_choice = $("#id_epsad_internal_choice")
    var epsad_external_choice = $("#id_epsad_external_choice")
    if (epsad_internal_choice.is(":checked")) {
      epsad_internal_checked(means_name, unit_name)
    }
    else if (epsad_external_choice.is(":checked")) {
      epsad_external_checked(means_name, unit_name)
    }
  }
  else if (means_name == "ΣΕΖΜ-ΕΡΜΗΣ") {  
    var hermes_node_choice = $("#id_hermes_node_choice")
    var hermes_connection_choice = $("#id_hermes_connection_choice")
    if (hermes_node_choice.is(":checked")) {
      hermes_node_checked(means_name, unit_name)
    }
    else if (hermes_connection_choice.is(":checked")) {
      hermes_connection_checked(means_name, unit_name)
    }
  } 
  else if (means_name == "ΠΥΡΣΕΙΑ") {
    related_data_fetch('/ajax/get_related_data_pyrseia/', means_name, unit_name, '#id_related_pyrseia_server_new_failure', 'related_pyrseia_server');
  }
  else if (means_name == "ΕΥΡΥΖΩΝΙΚΟ") {
    related_data_fetch('/ajax/get_related_data_broadband/', means_name, unit_name, '#id_related_broadband_transceiver_new_failure', 'related_broadband_transceiver');
  }
  else if (means_name == "ΔΟΡΥΦΟΡΙΚΑ") {
    related_data_fetch('/ajax/get_related_data_satellite/', means_name, unit_name, '#id_related_satellite_node_new_failure', 'related_satellite_node');
  }
  else if (means_name == "HARP") {
    related_data_fetch('/ajax/get_related_data_harp/', means_name, unit_name, '#id_related_harp_correspondent_new_failure', 'related_harp_correspondent');
  }
});

function related_data_fetch(ajax_url, means_name, unit_name, ajax_id, related_data_tag){
  // $.ajax -> performs an asynchronous HTTP (Ajax) request
  $.ajax({
    // the url which the request is sent to
    url: ajax_url,

    // data to be sent to the server - if the http method is one that cannot have an entity body,
    // such as GET, the data is appended to the URL
    data: {
      'means_name': means_name,
      'unit_name': unit_name
    },

    // the type of data expected back from the server
    dataType: 'json',

    // function to be called if the request succeeds
    success: function (data) {
      // set the disabled property for the matched element as false
      $(ajax_id).prop('disabled', false);
      $(ajax_id).find('option').remove().end()
      $(ajax_id).append('<option value="">' + '---------' + '</option>');
      $.each(data[related_data_tag], function (index, value) {
        $(ajax_id).append('<option value="' + value.id + '">' + value.name + '</option>');
      });
      $(ajax_id).selectpicker('refresh');
    }
  });
}

$('input:radio[name="hermes_choice"]').change(
  function(){
    var means_name = $("#id_means_new_failure").find(':selected')[0].label;
    var unit_name = $("#id_unit_new_failure").find(':selected')[0].label;

    if ($(this).is(':checked') && $(this).val() == 'hermes_node') {
      hermes_node_checked(means_name, unit_name)
    }
    else if ($(this).is(':checked') && $(this).val() == 'hermes_connection') {
      hermes_connection_checked(means_name, unit_name)
    }
  });


$('input:radio[name="epsad_choice"]').change(
  function(){
    var means_name = $("#id_means_new_failure").find(':selected')[0].label;
    var unit_name = $("#id_unit_new_failure").find(':selected')[0].label;

    if ($(this).is(':checked') && $(this).val() == 'epsad_internal') {
      epsad_internal_checked(means_name, unit_name)
    }
    else if ($(this).is(':checked') && $(this).val() == 'epsad_external') {
      epsad_external_checked(means_name, unit_name)
    }
  });


function epsad_internal_checked(means_name, unit_name) {
  $('#select_epsad_external').hide(1);
  $("#id_related_epsad_external_new_failure").find('option').remove().end()
  $("#id_related_dig_connection_new_failure").find('option').remove().end()
  related_data_fetch('/ajax/get_related_data_dig/', means_name, unit_name, '#id_related_epsad_internal_new_failure', 'related_dig_connections');
  $('#select_epsad_internal').show('slow');
}

function epsad_external_checked(means_name, unit_name) {
  $('#select_epsad_internal').hide(1);
  $("#id_related_epsad_internal_new_failure").find('option').remove().end()
  $("#id_related_dig_connection_new_failure").find('option').remove().end()
  related_data_fetch('/ajax/get_related_data_dig/', means_name + "|external", unit_name, '#id_related_epsad_external_new_failure', 'related_dig_connections');
  $('#select_epsad_external').show('slow');
}

function hermes_node_checked(means_name, unit_name) {
  $('#select_related_hermes_connection').hide(1);
  related_data_fetch('/ajax/get_related_data_hermes_node/', means_name, unit_name, '#id_related_hermes_node_new_failure', 'related_hermes_node');
  $('#select_related_hermes_node').show('slow');
}

function hermes_connection_checked(means_name, unit_name) {
  $('#select_related_hermes_node').hide(1);
  related_data_fetch('/ajax/get_related_data_hermes_connection/', means_name, unit_name, '#id_related_hermes_connection_new_failure', 'related_hermes_connection');
  $('#select_related_hermes_connection').show('slow');
}


$('#select_dispatcher').click(function() {
  var means_name = $('#means').text();
  $.ajax({
    url: '/ajax/get_dispatchers',
    data: {
      'means_name': means_name,
    },
    dataType: 'json',
    success: function (data) {
      $('#id_dispatcher_form_select').find('option').not(':first').remove().end()
      $.each(data['dispatcher_form_select'], function (index, value) {
        $('#id_dispatcher_form_select').append('<option value="' + value.id + '">' + value.name + '</option>');
      });
      $('#id_dispatcher_form_select').selectpicker('refresh');
    }
  });

  $('#searching_message').delay(500).hide('slow');
  $('#show_dispatcher_form_select').delay(500).show('slow');
});

$(document).ready(function() {
  if (window.location.href.indexOf("#assign") != -1) {
    $("#select_dispatcher").trigger("click");
  }
  else if (window.location.href.indexOf("#delete") != -1) {
    $("#delete_failure").trigger("click");
    $("#delete_report").trigger("click");
  }
  else if (window.location.href.indexOf("#complete") != -1) {
    focus_on_solution();
  }
})

function focus_on_solution() {
  console.log("inside focus");
  $("#failure_solution").focus();
  $("#report_solution").focus();
}

$("#complete_failure_button").on("click", function(e) {
  if (!$("#failure_solution").val() || $("#failure_solution").val() == "---") {
    e.preventDefault();
    $("#completeModal").modal("show");
  }
});

$("#complete_report_button").on("click", function(e) {
  if (!$("#report_solution").val() || $("#report_solution").val() == "---") {
    e.preventDefault();
    $("#completeModal").modal("show");
  }
});


/*
Chat Display new unreade messages
*/

if (!window.chatDashboard) {
  window.chatData = {
    activeRoomMessageCount: {}
  };

  function fetchChatData() {
    $.get("/chat/chats", ( data ) => {
      window.chatData.data = data.data;
      console.log(data.data);
      displayUnreadMessages();
    });
  }

  function displayUnreadMessages() {
    let chatRoomReadMessages = JSON.parse(localStorage.getItem('chatRoomReadMessages'));
    const chatData = window.chatData;
    let unreadMessagesObject = {};
    let unreadMessagesCount = 0;

    chatRoomReadMessages = chatRoomReadMessages || [];
    chatData.data.forEach((chatRoom) => {
      const readChatRoom = chatRoomReadMessages.find(element => element && element.id == chatRoom.id);
      const lastReadMessageId = (readChatRoom && readChatRoom.lastReadMessage) ? readChatRoom.lastReadMessage.id : 0;
      chatRoom.messages.forEach((message) => {
        if (message.id > lastReadMessageId && message.sender_id != window.user.id) {
          unreadMessagesCount++;
        }
      });
    });
    // span class="badge badge-info float-right">2</span>
    if (unreadMessagesCount > 0) {
      $('.new-chat-msgs-badge').remove();
      const el = document.createElement('span');
      el.setAttribute('class', 'badge badge-primary float-right new-chat-msgs-badge');
      el.style = " position: absolute;right: 33%;top: 12%;";
      el.innerText = unreadMessagesCount;
      $('.chat-nav').append(el);
    } else {
      $('.new-chat-msgs-badge').remove();
    }
    console.log('unread messages', unreadMessagesCount);
  }

  $(function() {
    setInterval(fetchChatData, 10000);
    fetchChatData();
  });

  
}