//initialisation of global variables to be used throughout script
var StationMarkers = {};
var infoWindow = {};
var journey = {};
//chart initialisation
var daily_chart_template = MakeDailyChartTemplate();
var hourly_chart_template = MakeHourlyChartTemplate();
//map settings
var stationZoom = 16;
var routeZoom = 15;
var mapZoom = 14;
var altMarkerIcon;
var markerIcon;
var dublin_bounds = {
  north: 53.4,
  south: 53.3,
  west: -6.38,
  east: -6.15,
};
//default location if user location not enabled
var userLat = 53.34229;
var userLong = -6.25975;
var userLocation = "Grafton Street, Dublin";
var locationMarker;
//the user selection for date/time of journey
var current_date = "Today";
var current_time = "Now";
var forecast_weather = {};
var predictionInfo = document.getElementById("weatherPrediction");
//the user selection for start/end station (station number) - all changes in UI reflected in these variables
var selected_start_station = {};
var selected_end_station = {};
var placeOrigin = {};
var placeDestination = {};
var routes = {};
// Points to functions in initMap
var f = {};
var initial_page_load = true;
var origin_stations;
var destination_stations;
var station_names_index = {};

//populate route planner date/time option dropdown with values
PopulateDateOptions();
PopulateTimeOptions();
//makes station_finder default tab
document.getElementById("station_finder_tab").click();

// function to post data to flask app
async function postData(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    cache: "no-cache",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return response.json();
}

//create the daily availability chart object
function MakeDailyChartTemplate() {
  var daily_canvas = document.getElementById("daily_availability");

  var daily_chart = new Chart(daily_canvas, {
    type: "bar",
    //initialise with no data
    options: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "Availability by Day",
      },
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
            },
          },
        ],
      },
    },
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          borderWidth: 1,
        },
      ],
    },
  });
  return daily_chart;
}

//create the hourly availability chart object
function MakeHourlyChartTemplate() {
  var hourly_canvas = document.getElementById("hourly_availability");

  var hourly_chart = new Chart(hourly_canvas, {
    type: "bar",
    options: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "Availability by Hour",
      },
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
            },
          },
        ],
      },
    },
    data: {
      labels: [],
      options: {
        title: {
          display: true,
          text: "Availability by Hour",
        },
      },
      datasets: [
        {
          data: [],
          borderWidth: 1,
        },
      ],
    },
  });
  return hourly_chart;
}

//get a custom gradient for the chart to match app theme
function getCustomGradient(chartid) {
  var ctx = document.getElementById(chartid).getContext("2d");

  var chart_template;
  if (chartid == "hourly_availability") {
    chart_template = hourly_chart_template;
  } else {
    chart_template = daily_chart_template;
  }

  var pixel_max = chart_template.scales["y-axis-0"].getPixelForValue(10);

  if (pixel_max < 0) {
    pixel_max = 120;
  }

  var pixel_zero = chart_template.height;
  var gradient = ctx.createLinearGradient(0, pixel_max, 0, pixel_zero);

  gradient.addColorStop(1, "rgba(40, 70, 70, 0.3)");
  gradient.addColorStop(0, "cadetblue");

  return gradient;
}

//update the availability charts with the hourly and daily availability statistics
function updateAvailabilityCharts(hourly_availability, daily_availability) {
  var hourly_gradient = getCustomGradient("hourly_availability");
  var daily_gradient = getCustomGradient("daily_availability");

  daily_chart_template.data.labels = daily_availability.labels;
  daily_chart_template.data.datasets[0] = {
    data: daily_availability.data,
    borderWidth: 1,
    backgroundColor: hourly_gradient,
  };

  daily_chart_template.update();

  hourly_chart_template.data.labels = hourly_availability.labels;
  hourly_chart_template.data.datasets[0] = {
    data: hourly_availability.data,
    borderWidth: 1,
    backgroundColor: daily_gradient,
  };

  hourly_chart_template.update();
}

//function to return 2 divs given a station object-info box for the map and a div for the sidebar with station details
function stationStats(station) {
  let banking;
  if (station.banking == 0) {
    banking = "No";
  } else {
    banking = "Yes";
  }

  let stationInfoMap =
    "<h4>" +
    station.address +
    "</h4>" +
    "<p>Available bikes: " +
    station.availablebikes +
    "</br>Free stands: " +
    station.availablestands +
    "<br>Cards accepted: " +
    banking;

  let stationInfoSidebar =
    "<div class=sidebarheader>STATION INFORMATION</div>" +
    //constructing the table for the sidebar
    "<div id=stationinfo><table id=infotable>" +
    "<tr><th colspan='2'>" +
    station.address +
    "</th></tr>" +
    "<tr><td>Available Bikes" +
    "</td><td>" +
    station.availablebikes +
    "</td></tr><tr><td>Available Stands</td><td>" +
    station.availablestands +
    "</td></tr><td>Cards Accepted</td><td>" +
    banking +
    "</td></tr></table></div>";

  return { stationInfoMap, stationInfoSidebar };
}

//function to control displaying a station
//populates sidebar with live station information and historical stats
//centers map on station and opens information box on marker
function displayStation(
  stationNumber,
  mapClick = false,
  suppress_recenter = false
) {
  var bikes = document.getElementById("bikes");
  var stands = document.getElementById("stands");

  //if div is available (it might not be on initial load due to async initMap then click the bike div to display available bikes)
  if (bikes) {
    if (bikes.classList.contains("active")) {
      bikes.click();
    } else {
      stands.click();
    }
  }

  const marker = StationMarkers[stationNumber];
  fetch("/station/" + stationNumber)
    .then((response) => {
      return response.json();
    })
    .then((station) => {
      //format the station information and return string
      stationInfo = stationStats(station);

      //update the charts with the data for this station
      updateAvailabilityCharts(
        station.hourly_availability,
        station.daily_availability
      );

      //set content of infoWindow
      infoWindow.setContent(stationInfo.stationInfoMap);

      //open infoWindow unless initial page load
      if (initial_page_load == true) {
        initial_page_load = false;
      } else {
        infoWindow.open(map, marker);
      }

      //in the case where the function is triggered by a show stations nearby call then maintain center on user's location
      if (suppress_recenter == false) {
        //set the center of the map to the markers position
        map.setCenter(marker.getPosition());
      }

      //set the sidebar information to the station information
      document.getElementById("sidebar").innerHTML =
        stationInfo.stationInfoSidebar;

      UpdateSelectedStationDropdown(station.address);

      //if it was a map click zoom in on that station
      if (mapClick) {
        map.setZoom(stationZoom);
      }
    })
    .catch();
}

function populateDropdown(stationNumber, stationAddress) {
  //build entries for dropdown list, called by initMap
  dropDown =
    '<option id="' +
    stationNumber +
    '" value="' +
    stationNumber +
    '">' +
    stationAddress +
    " </option>";
  document.getElementById("station_select").innerHTML += dropDown;
}

function DropdownClicked(ev) {
  ev.stopPropagation();
  //id the dropdown is currently not showing (i.e. arrow pointing down) then display it
  if (document.getElementById("dropdownarrow").className == "arrow down") {
    let stationlist = document.getElementById("dropdown-station-list");
    stationlist.style.display = "block";
    document.getElementById("dropdownarrow").setAttribute("class", "arrow up");
  } else {
    document.getElementById("dropdown-station-list").style.display = "none";
    document
      .getElementById("dropdownarrow")
      .setAttribute("class", "arrow down");
  }
}

function closeDropdown(object_clicked) {
  if (
    (object_clicked.target != document.getElementById("selected-element")) &
    (object_clicked.target != document.getElementById("arrow-icon")) &
    (object_clicked.target != document.getElementById("dropdownarrow"))
  ) {
    document.getElementById("dropdown-station-list").style.display = "none";
    document
      .getElementById("dropdownarrow")
      .setAttribute("class", "arrow down");
  }
}

//add listeners to close dropdowns whenever document is clicked
//each function checks that the dropdown itself has not been clicked and if not it closes itself
document.addEventListener("click", closeDropdown);
document.addEventListener("click", closeDateDropdown);
document.addEventListener("click", closeTimeDropdown);
document.addEventListener("click", closeStartStationDropdown);
document.addEventListener("click", closeEndStationDropdown);


function UpdateSelectedStationDropdown(station_name) {
  var customselect = document.getElementById("station_select");
  for (i = 0; i < customselect.length; i++) {
    if (customselect.options[i].innerText.trim() == station_name.trim()) {
      customselect.selectedIndex = i;
      break;
    }
  }

  UpdateCustomDropdown();
}

function UpdateCustomDropdown() {
  //get the custom dropdown object
  var dropdown_container = document.getElementById("custom-dropdown");

  //get the dropown select object
  var customselect = document.getElementById("station_select");

  //get the name of the station selected
  var selected_station_name =
    customselect.options[customselect.selectedIndex].innerHTML;

  //get the div which contains the selected station
  var selected_station = document.getElementById("selected-element");

  //set the inner html to the name of the station
  selected_station.innerHTML = selected_station_name;

  //get the div which contains the list of all non-selected stations
  var other_items_dropdown = document.getElementById("dropdown-station-list");

  //clear the list
  other_items_dropdown.innerHTML = "";

  //create the list of all stations
  for (let index = 0; index < customselect.length; index++) {
    let station_name = customselect.options[index].innerHTML;

    station_names_index[station_name.trim()] = index;

    let non_selected_div = document.createElement("DIV");

    non_selected_div.setAttribute("class", "non-selected-element");

    non_selected_div.innerHTML = station_name;

    non_selected_div.addEventListener("click", () => {
      UpdateSelectedStationDropdown(station_name);
      displayStation(customselect.options[index].id);
    });

    other_items_dropdown.appendChild(non_selected_div);
  }
}



//functions for handling populating the suggested start and end stations
function setSelectedStartStation(station_name, station_number) {
  document.getElementById("start_selected_value").innerHTML = station_name;
  selected_start_station = { name: station_name, number: station_number };

  // Calculate Route from Origin to Selected Start Station
  f.calcRoute(
    placeOrigin.LatLng,
    StationMarkers[station_number].position,
    "leg0",
    "WALKING"
  );

  // If later route variables already set recalc route legs where possible
  if (selected_end_station.number) {
    f.calcRoute(
      StationMarkers[selected_start_station.number].position,
      StationMarkers[selected_end_station.number].position,
      "leg1",
      "BICYCLING"
    );
    if (placeDestination.LatLng) {
      f.calcRoute(
        StationMarkers[selected_end_station.number].position,
        placeDestination.LatLng,
        "leg2",
        "WALKING"
      );
    }
  }
}

function setSelectedEndStation(station_name, station_number) {
  document.getElementById("end_selected_value").innerHTML = station_name;
  selected_end_station = { name: station_name, number: station_number };

  // If later route variables already set recalc route legs where possible
  if (selected_start_station.number) {
    f.calcRoute(
      StationMarkers[selected_start_station.number].position,
      StationMarkers[station_number].position,
      "leg1",
      "BICYCLING"
    );
  }
  f.calcRoute(
    StationMarkers[station_number].position,
    placeDestination.LatLng,
    "leg2",
    "WALKING"
  );
}

function formatSuggestedDropdownDiv(station, type_) {
  var class_option;
  var icon_option;
  var onclickfunction;

  if (type_ == "origin") {
    class_option = "start_station_option";
    icon_option = "fas fa-bicycle";
    onclickfunction = setSelectedStartStation;
  } else {
    class_option = "end_station_option";
    icon_option = "fas fa-parking";
    onclickfunction = setSelectedEndStation;
  }

  const option_div = document.createElement("div");
  option_div.setAttribute("class", class_option);

  const option_name = document.createElement("div");
  option_name.setAttribute("class", "option_name");
  option_name.innerHTML = `${station.address} - ${station.distance}`;

  const option_details = document.createElement("div");
  option_details.setAttribute("class", "option_details");

  if (type_ == "origin") {
    option_details.innerHTML = `${station.availablebikes} <i class="${icon_option}"></i>`;
    document.getElementById("loader1").style.visibility = "hidden";
    document.getElementById("loader1").style.position = "absolute";
    document.getElementById("select_origin_wrapper").style.display = "block";
  } else {
    option_details.innerHTML = `${station.availablestands} <i class="${icon_option}"></i>`;
    document.getElementById("loader2").style.visibility = "hidden";
    document.getElementById("loader2").style.position = "absolute";
    document.getElementById("select_destination_wrapper").style.display =
      "block";
  }

  option_div.appendChild(option_name);
  option_div.appendChild(option_details);

  option_div.onclick = () => onclickfunction(station.address, station.number);

  return option_div;
}

function StartSuggestionDropdownClick(ev) {
  ev.stopPropagation();

  const start_station_dd_arrow = document.getElementById(
    "dropdownarrow-start-suggestions"
  );

  if (start_station_dd_arrow.getAttribute("class") == "arrow down") {
    start_station_dd_arrow.setAttribute("class", "arrow up");
    document.getElementById("start_station_options").style.display = "block";
  } else {
    start_station_dd_arrow.setAttribute("class", "arrow down");
    document.getElementById("start_station_options").style.display = "none";
  }

  document.getElementById("date_options").style.display = "none";
  document
    .getElementById("dropdownarrowdt")
    .setAttribute("class", "arrow down");
  document.getElementById("time_options").style.display = "none";
  document
    .getElementById("dropdownarrowtime")
    .setAttribute("class", "arrow down");
  document.getElementById("end_station_options").style.display = "none";
  document
    .getElementById("dropdownarrow-end-suggestions")
    .setAttribute("class", "arrow down");
}

function EndSuggestionDropdownClick(ev) {
  ev.stopPropagation();

  const end_station_dd_arrow = document.getElementById(
    "dropdownarrow-end-suggestions"
  );

  if (end_station_dd_arrow.getAttribute("class") == "arrow down") {
    //change the dropdown arrow to arrow up
    end_station_dd_arrow.setAttribute("class", "arrow up");
    //display the end stations dropdown
    document.getElementById("end_station_options").style.display = "block";
    //scroll to bottom of div to get dropdown in view
    document.getElementById("sidetab").scrollTop = document.getElementById(
      "sidetab"
    ).scrollHeight;
  } else {
    //close dropdown and set arrow up to arrow down
    end_station_dd_arrow.setAttribute("class", "arrow down");
    document.getElementById("end_station_options").style.display = "none";
  }

  document.getElementById("date_options").style.display = "none";
  document
    .getElementById("dropdownarrowdt")
    .setAttribute("class", "arrow down");
  document.getElementById("time_options").style.display = "none";
  document
    .getElementById("dropdownarrowtime")
    .setAttribute("class", "arrow down");
  document.getElementById("start_station_options").style.display = "none";
  document
    .getElementById("dropdownarrow-start-suggestions")
    .setAttribute("class", "arrow down");
}

function PopulateStartStationSuggestions(stations_array) {
  document.getElementById("start_station_options").innerHTML = "";
  setSelectedStartStation(
    origin_stations[0].address,
    origin_stations[0].number
  );
  for (var i = 0; i < origin_stations.length; i++) {
    let station = origin_stations[i];
    let station_option = formatSuggestedDropdownDiv(station, "origin");
    document
      .getElementById("start_station_options")
      .appendChild(station_option);
  }
}

function PopulateEndStationSuggestions(stations_array) {
  document.getElementById("end_station_options").innerHTML = "";
  setSelectedEndStation(
    destination_stations[0].address,
    destination_stations[0].number
  );
  for (var i = 0; i < destination_stations.length; i++) {
    let station = destination_stations[i];
    let station_option = formatSuggestedDropdownDiv(station, "destination");
    document.getElementById("end_station_options").appendChild(station_option);
  }
}

//funciton to create string representation of a date for dropdown
function makeDateString(date) {
  const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "June",
    "July",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  var weekday = weekdays[date.getDay()];

  var monthday = date.getDate();

  var month = months[date.getMonth()];

  const dtstr = `${weekday}, ${monthday} ${month}`;

  return dtstr;
}

function closeDateDropdown(object_clicked) {
  //if anything other than the date dropdown is clicked close it
  if (
    (object_clicked.target.getAttribute("id") != "date_selection") &
    (object_clicked.target.getAttribute("id") != "dt-arrow-icon") &
    (object_clicked.target.getAttribute("id") != "dropdownarrowdt")
  ) {
    document.getElementById("date_options").style.display = "none";
    document
      .getElementById("dropdownarrowdt")
      .setAttribute("class", "arrow down");
  }
}

function closeTimeDropdown(object_clicked) {
//if anything other than the time dropdown is clicked close it
  if (
    (object_clicked.target.getAttribute("id") != "time_selection") &
    (object_clicked.target.getAttribute("id") != "time-arrow-icon") &
    (object_clicked.target.getAttribute("id") != "dropdownarrowtime")
  ) {
    document.getElementById("time_options").style.display = "none";
    document
      .getElementById("dropdownarrowtime")
      .setAttribute("class", "arrow down");
  }
}

function closeStartStationDropdown(object_clicked) {
  //if anything other than the start station dropdown is clicked close it
  if (
    (object_clicked.target.getAttribute("id") !=
      "select_suggested_start_wrapper") &
    (object_clicked.target.getAttribute("id") !=
      "dropdownarrow-start-suggestions") &
    (object_clicked.target.getAttribute("id") != "arrow-icon-start-suggestions")
  ) {
    document.getElementById("start_station_options").style.display = "none";
    document
      .getElementById("dropdownarrow-start-suggestions")
      .setAttribute("class", "arrow down");
  }
}

function closeEndStationDropdown(object_clicked) {
  //if anything other than the end station dropdown is clicked close it
  if (
    (object_clicked.target.getAttribute("id") !=
      "select_suggested_end_wrapper") &
    (object_clicked.target.getAttribute("id") !=
      "dropdownarrow-end-suggestions") &
    (object_clicked.target.getAttribute("id") != "arrow-icon-end-suggestions")
  ) {
    document.getElementById("end_station_options").style.display = "none";
    document
      .getElementById("dropdownarrow-end-suggestions")
      .setAttribute("class", "arrow down");
  }
}

function setDateValue(dtstr) { 
  //sets the users chosen date value and updates the time value if required
  document.getElementById("date_value").innerHTML = dtstr;
  const old_date = current_date;
  current_date = dtstr;

  //if the user changes from today to a different date then if the current time selected is
  //now it must be changed to something else (09:00) and the dropdown options for time must be updated
  if ((old_date == "Today") & (current_date != "Today")) {
    if (current_time == "Now") {
      setTimeValue("09:00");
    } else setTimeValue(current_time);

    PopulateTimeOptions();
    return;
  }

  if ((old_date != "Today") & (current_date == "Today")) {
    PopulateTimeOptions();
    setTimeValue("Now");
  }

  if ((old_date != "Today") & (current_date != "Today")) {
    PopulateTimeOptions();
    setTimeValue(current_time);
  }
}

function PopulateDateOptions() { 
  //populate date options based off the current time
  var day = new Date();

  makeDateString(day);

  var days_to_show = 5;

  var options_div = document.getElementById("date_options");

  for (var i = 0; i < days_to_show; i++) {
    let dtstr;

    if (i == 0) {
      dtstr = "Today";
    } else {
      day.setDate(day.getDate() + 1);
      dtstr = makeDateString(day);
    }

    const dt_option_div = document.createElement("div");
    dt_option_div.setAttribute("class", "date_option");
    dt_option_div.innerHTML = `${dtstr}`;
    dt_option_div.onclick = () => setDateValue(dtstr);
    options_div.appendChild(dt_option_div);
  }
}


function setTimeValue(tm) { 
  //sets the user's chosen time value and automatically refreshes predictions
  document.getElementById("time_value").innerHTML = tm;
  current_time = tm;

  if (tm != "Now") {
    document.getElementById("suggested-end-label").innerHTML =
      "Suggested End Stations (Predicted Availability)";
    document.getElementById("suggested-start-label").innerHTML =
      "Suggested Start Stations (Predicted Availability)";
  } else {
    document.getElementById("suggested-end-label").innerHTML =
      "Suggested End Stations";
    document.getElementById("suggested-start-label").innerHTML =
      "Suggested Start Stations";
  }


  // Trigger Route Calc on Time Change if place variables are set
  if (placeOrigin.LatLng) {
    const request_params = {
      lat: placeOrigin.LatLng.lat,
      lng: placeOrigin.LatLng.lng,
      dt: current_date,
      tm: current_time,
    };

    // hides station dropdown and sets loader visible
    document.getElementById("loader1").style.visibility = "visible";
    document.getElementById("loader1").style.position = "relative";
    document.getElementById("select_origin_wrapper").style.display = "none";

    //post origin to flask, return array of 5 nearest stations and call function to populate dropdown
    postData("API/origin", request_params).then((data) => {
      origin_stations = data.stations;
      forecast_weather = data.weather;

      PopulateStartStationSuggestions(origin_stations);
    });
  }

  if (placeDestination.LatLng) {
    const request_params = {
      lat: placeDestination.LatLng.lat,
      lng: placeDestination.LatLng.lng,
      dt: current_date,
      tm: current_time,
    };

    // hides station dropdown and sets loader visible
    document.getElementById("loader2").style.visibility = "visible";
    document.getElementById("loader2").style.position = "relative";
    document.getElementById("select_destination_wrapper").style.display =
      "none";

    //post destination to flask, return array of 5 nearest stations and call function to populate dropdown
    postData("API/destin", request_params).then((data) => {
      destination_stations = data.stations;
      forecast_weather = data.weather;
      PopulateEndStationSuggestions(destination_stations);
    });
  }
}

function PopulateTimeOptions() {
  //display these times as options if future date is chosen
  var future_options = [
    "05:00",
    "06:00",
    "07:00",
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00",
    "22:00",
    "23:00",
  ];

  var today_options = ["Now"];

  var day = new Date();

  while (day.getHours() < 23) {
    day.setHours(day.getHours() + 1);

    let current_hour = day.getHours();

    if (current_hour < 10) {
      current_hour = `0${current_hour}`;
    }

    current_hour = `${current_hour}:00`;

    today_options.push(current_hour);
  }

  let displayable_options;

  if (current_date == "Today") {
    displayable_options = today_options;
  } else {
    displayable_options = future_options;
  }

  var options_div = document.getElementById("time_options");

  options_div.innerHTML = "";

  for (var i = 0; i < displayable_options.length; i++) {
    let tm = displayable_options[i];
    const time_option = document.createElement("div");
    time_option.setAttribute("class", "time_option");
    time_option.innerHTML = `${tm}`;
    time_option.onclick = () => setTimeValue(tm);
    options_div.appendChild(time_option);
  }
}

function TimeDropdownClicked(ev) {
  ev.stopPropagation();

  const time_dd_arrow = document.getElementById("dropdownarrowtime");

  if (time_dd_arrow.getAttribute("class") == "arrow down") {
    time_dd_arrow.setAttribute("class", "arrow up");
    document.getElementById("time_options").style.display = "block";
  } else {
    time_dd_arrow.setAttribute("class", "arrow down");
    document.getElementById("time_options").style.display = "none";
  }

  document.getElementById("date_options").style.display = "none";
  document
    .getElementById("dropdownarrowdt")
    .setAttribute("class", "arrow down");
  document.getElementById("start_station_options").style.display = "none";
  document
    .getElementById("dropdownarrow-start-suggestions")
    .setAttribute("class", "arrow down");
  document.getElementById("end_station_options").style.display = "none";
  document
    .getElementById("dropdownarrow-end-suggestions")
    .setAttribute("class", "arrow down");
}

function DateDropdownClicked(ev) {
  ev.stopPropagation();

  const dt_dd_arrow = document.getElementById("dropdownarrowdt");

  if (dt_dd_arrow.getAttribute("class") == "arrow down") {
    dt_dd_arrow.setAttribute("class", "arrow up");
    document.getElementById("date_options").style.display = "block";
  } else {
    dt_dd_arrow.setAttribute("class", "arrow down");
    document.getElementById("date_options").style.display = "none";
  }

  document.getElementById("time_options").style.display = "none";
  document
    .getElementById("dropdownarrowtime")
    .setAttribute("class", "arrow down");
  document.getElementById("start_station_options").style.display = "none";
  document
    .getElementById("dropdownarrow-start-suggestions")
    .setAttribute("class", "arrow down");
  document.getElementById("end_station_options").style.display = "none";
  document
    .getElementById("dropdownarrow-end-suggestions")
    .setAttribute("class", "arrow down");
}

//
// Initialise Google Map thru JS API
//

function setUserCoordinates(lat, long, suppress_info_box) {
  userLat = lat;
  userLong = long;
  const position = new google.maps.LatLng(lat, long);

  if (!locationMarker) {
    setTimeout(() => setUserCoordinates(lat, long, suppress_info_box), 500);
  } else {
    locationMarker.setPosition(position);
    displayStationsNearby(true);
  }
}

function calculateNewBounds(closest_marker) {
  var bounds = new google.maps.LatLngBounds();
  bounds.extend(closest_marker.getPosition());
  bounds.extend(locationMarker.getPosition());
  map.fitBounds(bounds);
}

function displayStationsNearby(place_change_trigger) {
  //on the first page load when the location is set do not zoom in
  if (initial_page_load == true) {
    fetch(`/closeststation/${userLat}/${userLong}`).then((response) => {
      response.json().then((data) => {
        var customselect = document.getElementById("station_select");
        UpdateSelectedStationDropdown(data[0].address);
        displayStation(
          customselect.options[station_names_index[data[0].address]].id,
          false,
          true
        );
      });
    });
    return;
  }
  //if the user changes place then always display nearby stations to that location - if they click the button then
  //either reset the map if the button says reset or else show stations nearby
  if (
    (document.getElementById("stations-near-me-button").getAttribute("class") ==
      "show-stations") |
    place_change_trigger
  ) {
    locationMarker.setVisible(true);
    fetch(`/closeststation/${userLat}/${userLong}`).then((response) => {
      response.json().then((data) => {
        var customselect = document.getElementById("station_select");
        UpdateSelectedStationDropdown(data[0].address);

        calculateNewBounds(StationMarkers[data[0].number]);
        map.setZoom(map.getZoom() - 1);
        displayStation(
          customselect.options[station_names_index[data[0].address]].id,
          false,
          true
        );
      });
    });
    document
      .getElementById("stations-near-me-button")
      .setAttribute("class", "reset-view");
    document.getElementById("stations-near-me-button").innerHTML = "Reset View";
    document.getElementById("stations-near-me-button").style.lineHeight =
      "30px";
  } else {
    map.setZoom(mapZoom);
    locationMarker.setVisible(false);
    map.setCenter({ lat: 53.3457, lng: -6.2678 });
    document.getElementById("stations-near-me-button").innerHTML =
      "Display Stations Near Me";
    document
      .getElementById("stations-near-me-button")
      .setAttribute("class", "show-stations");
    document.getElementById("stations-near-me-button").style.lineHeight = "";
    infoWindow.close();
  }
}

function revertToDefaultLocation() {
  document
    .getElementById("your-location-autocomplete")
    .setAttribute("placeholder", userLocation);
  document.getElementById("your-location-error").style.display = "block";
  document.getElementById("your-location-wrapper").style.marginTop = "2px";
  setUserCoordinates(userLat, userLong, true);
}

function getUserLocation(autoCompleteYourLocation) {
  //gets the user location and displays in the auto complete (defaults to grafton street if failed)

  const geocoder = new google.maps.Geocoder();

  try {
    //try to get the user's current location
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userLat = position.coords.latitude;
        userLong = position.coords.longitude;

        const latlng = {
          lat: userLat,
          lng: userLong,
        };

        geocoder.geocode({ location: latlng }, (results, status) => {
          if (status === "OK") {
            if (results[0]) {
              const location_description =
                results[0].address_components[1].long_name +
                ", " +
                results[0].address_components[2].long_name;
              document
                .getElementById("your-location-autocomplete")
                .setAttribute("placeholder", location_description);
            }
            setUserCoordinates(userLat, userLong, true);
          }
        });
      },
      () => {
        revertToDefaultLocation();
      },
      { timeout: 1000 }
    );
  } catch (err) {
    //if it fails then the current location will default to grafton street
    revertToDefaultLocation();
  }
}

function initMap() {
  // First set some variables & initialise google map objects

  // Setup googlemaps Places Autocomplete Service
  // Set options for service
  const autocompleteOptions = {
    bounds: dublin_bounds,
    strictBounds: true,
    fields: ["name", "geometry", "place_id"], // Google charges per field
  };
  // Set Ids of text-boxes attached to autocomplete
  const inputOrigin = document.getElementById("inputOrigin");
  const inputDestination = document.getElementById("inputDestin");
  // Ids of info-boxes beneath search boxes
  const infoOrigin = document.getElementById("infoOrigin");
  const infoDestin = document.getElementById("infoDestin");
  const infoRoute = document.getElementById("infoRoute");
  const yourLocation = document.getElementById("your-location-autocomplete");

  // Make autocomplete objects associated with input-box
  autocompleteOrigin = new google.maps.places.Autocomplete(
    inputOrigin,
    autocompleteOptions
  );
  autocompleteDestin = new google.maps.places.Autocomplete(
    inputDestination,
    autocompleteOptions
  );
  autocompleteYourLocation = new google.maps.places.Autocomplete(
    yourLocation,
    autocompleteOptions
  );

  getUserLocation(autocompleteYourLocation);
  // Setup Googlemaps Directions Service
  const directionsService = new google.maps.DirectionsService();
  // Renderer Options
  routeIcon = {
    path: google.maps.SymbolPath.CIRCLE,
    scale: 5,
    fillColor: "cadetblue",
    strokeColor: "black",
    fillOpacity: 0.8,
    strokeWeight: 1,
  };
  renderOptions = {
    suppressBicyclingLayer: true,
    preserveViewport: true,
    PolylineOptions: { strokeColor: "#5F9EA0" }, // Only recognises basic css colors?
    markerOptions: { icon: routeIcon, zIndex: -1 },
  };
  // Need a distinct renderer for each leg
  const directionsRenderer0 = new google.maps.DirectionsRenderer(renderOptions); // 0: origin to station; walking
  const directionsRenderer1 = new google.maps.DirectionsRenderer(renderOptions); // 1: station to station; cycling
  const directionsRenderer2 = new google.maps.DirectionsRenderer(renderOptions); // 2: station to destin; walking
  directionsRenderer0.set("directions", null); // Initially set directions to null to assist changing
  directionsRenderer1.set("directions", null); // routes as planner points are changed
  directionsRenderer2.set("directions", null);
  directionsRenderer0.set("map", null); // Initially set map to null to assist changing
  directionsRenderer1.set("map", null); // routes as planner points are changed
  directionsRenderer2.set("map", null);

  //fetch data to populate map with station markers
  fetch("/stations")
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 53.3457, lng: -6.2678 },
        zoom: mapZoom,
        gestureHandling: "greedy",
        maxZoom: 20,
        minZoom: 12,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        restriction: {
          latLngBounds: dublin_bounds,
        },
        styles: [
          { stylers: [{ saturation: -90 }] },
          {
            featureType: "administrative.land_parcel",
            elementType: "labels",
            stylers: [{ visibility: "off" }],
          },
          {
            featureType: "landscape.man_made",
            stylers: [{ visibility: "off" }],
          },
          {
            featureType: "poi",
            elementType: "labels.text",
            stylers: [{ visibility: "off" }],
          },
          {
            featureType: "poi",
            elementType: "geometry",
            stylers: [{ visibility: "off" }],
          },
          { featureType: "poi.attraction", stylers: [{ visibility: "off" }] },
          { featureType: "poi.business", stylers: [{ visibility: "off" }] },
          { featureType: "poi.government", stylers: [{ visibility: "off" }] },
          {
            featureType: "road",
            elementType: "labels.icon",
            stylers: [{ visibility: "on" }],
          },
          {
            featureType: "road.local",
            elementType: "labels",
            stylers: [{ visibility: "on" }],
          },
          { featureType: "transit", stylers: [{ visibility: "off" }] },
        ],
      });

      var stationNearMe = document.createElement("div");
      stationNearMe.setAttribute("id", "stations-near-me-button");
      stationNearMe.setAttribute("class", "show-stations");
      stationNearMe.style.backgroundColor = "white";
      stationNearMe.style.border = "2px solid gray";
      stationNearMe.style.borderRadius = "3px";
      stationNearMe.style.height = "30px";
      stationNearMe.style.width = "100px";
      stationNearMe.style.fontSize = "12px";
      stationNearMe.style.boxShadow = "0 2px 6px rgba(0,0,0,.3)";
      stationNearMe.style.cursor = "pointer";
      stationNearMe.style.textAlign = "center";
      stationNearMe.innerHTML = "Find Stations Near Me";
      stationNearMe.onclick = () => displayStationsNearby(false);

      map.controls[google.maps.ControlPosition.TOP_RIGHT].push(stationNearMe);

      //add control buttons to map
      const buttonBikesDiv = document.createElement("div");
      buttonBikesDiv.setAttribute("id", "bikes");
      buttonBikesDiv.setAttribute("class", "active");
      setMapControls(buttonBikesDiv, map);

      const buttonStandsDiv = document.createElement("div");
      buttonStandsDiv.setAttribute("id", "stands");
      setMapControls(buttonStandsDiv, map);

      const buttonClearRoute = document.createElement("div");
      buttonClearRoute.setAttribute("id", "route");
      setMapControls(buttonClearRoute, map);

      //create and open single infoWindow (now accessible to the rest of the script)
      infoWindow = new google.maps.InfoWindow();

      //create marker icon
      markerIcon = {
        path:
          "M0-48c-9.8 0-17.7 7.8-17.7 17.4 0 15.5 17.7 30.6 17.7 30.6s17.7-15.4 17.7-30.6c0-9.6-7.9-17.4-17.7-17.4z",
        fillColor: "cadetblue",
        fillOpacity: 0.9,
        scale: 0.65,
        labelOrigin: new google.maps.Point(0, -23),
      };

      altMarkerIcon = {
        path:
          "M0-48c-9.8 0-17.7 7.8-17.7 17.4 0 15.5 17.7 30.6 17.7 30.6s17.7-15.4 17.7-30.6c0-9.6-7.9-17.4-17.7-17.4z",
        fillColor: "gray",
        fillOpacity: 0.8,
        scale: 0.65,
        labelOrigin: new google.maps.Point(0, -23),
      };

      var user_loc_icon = {
        path:
          "M50.688-9.143q0 2.268-2.214 4.086t-5.904 2.916-8.1 1.656-9.126.558-9.126-.558-8.1-1.656-5.904-2.916-2.214-4.086q0-1.764 1.188-3.186t3.276-2.394 4.248-1.602 4.716-1.062q.936-.18 1.728.378t.936 1.494q.18.936-.378 1.728t-1.494.936q-2.088.36-3.816.846t-2.754.918-1.746.846-.99.702-.306.432q.108.396.972.954t2.628 1.188 4.104 1.17 5.778.9 7.254.36 7.254-.36 5.778-.9 4.104-1.188 2.628-1.206.972-.99q-.036-.144-.306-.396t-.99-.684-1.746-.846-2.754-.9-3.816-.846q-.936-.144-1.494-.936t-.378-1.728q.144-.936.936-1.494t1.728-.378q2.556.432 4.716 1.062t4.248 1.602 3.276 2.394 1.188 3.186zm-13.824-32.256v13.824q0 .936-.684 1.62t-1.62.684h-2.304v13.824q0 .936-.684 1.62t-1.62.684h-9.216q-.936 0-1.62-.684t-.684-1.62v-13.824h-2.304q-.936 0-1.62-.684t-.684-1.62v-13.824q0-1.908 1.35-3.258t3.258-1.35h13.824q1.908 0 3.258 1.35t1.35 3.258zm-3.456-13.824q0 3.348-2.358 5.706t-5.706 2.358-5.706-2.358-2.358-5.706 2.358-5.706 5.706-2.358 5.706 2.358 2.358 5.706z",
        fillColor: "darkslategrey",
        fillOpacity: 1,
        strokeWeight: 0,
        scale: 0.7,
        opacity: 0.8,
      };

      locationMarker = new google.maps.Marker({
        map: map,
        icon: user_loc_icon,
        position: { lat: userLat, lng: userLong },
      });

      locationMarker.setVisible(false);

      //loop through station data
      data.forEach((station) => {
        const marker = new google.maps.Marker({
          icon: markerIcon,
          position: { lat: station.latitude, lng: station.longitude },
          map: map,
          label: {
            text: station.availablebikes.toString(),
            color: "white",
            fontSize: "12px",
            fontWeight: "bold",
          },
        });

        var availability = station.availablebikes;
        if (availability == 0) {
          marker.setIcon(altMarkerIcon);
        }

        //add reference to each marker in StationMarkers
        StationMarkers[station.number] = marker;

        //build entries for dropdown menu by calling populate Dropdown
        populateDropdown(station.number, station.address);

        //when the station is clicked we call displayStation with that station number and mapclicked=True
        marker.addListener("click", () =>
          displayStation(station.number, true, false)
        );
      });

      UpdateCustomDropdown();
    });

  autocompleteYourLocation.addListener("place_changed", () => {
    const loc = autocompleteYourLocation.getPlace();
    const lat = loc.geometry.location.lat();
    const long = loc.geometry.location.lng();

    setUserCoordinates(lat, long, false);
  });

  // Event Listeners for autocomplete input boxes
  autocompleteOrigin.addListener("place_changed", () => {
    const origin = autocompleteOrigin.getPlace();

    if (!origin.geometry || !origin.geometry.location) {
      // User entered the name of a Place that was not suggested and
      // pressed the Enter key, or the Place Details request failed.
      window.alert("No details available for input: '" + origin.name + "'"); // Style this if kept
      return;
    }

    const originLatLng = {
      lat: origin.geometry.location.lat(),
      lng: origin.geometry.location.lng(),
    };

    const request_params = {
      lat: origin.geometry.location.lat(),
      lng: origin.geometry.location.lng(),
      dt: current_date,
      tm: current_time,
    };

    placeOrigin.LatLng = originLatLng;
    placeOrigin.name = origin.name;
    // Print Selected place name beneath search box

    //hides dropdown (if not already hidden) and sets loader visible
    document.getElementById("loader1").style.visibility = "visible";
    document.getElementById("loader1").style.position = "relative";
    document.getElementById("select_origin_wrapper").style.display = "none";

    //post origin to flask, return array of 5 nearest stations and call function to populate dropdown
    postData("API/origin", request_params).then((data) => {
      origin_stations = data.stations;
      forecast_weather = data.weather;
      PopulateStartStationSuggestions(origin_stations);
    });

    // Focus on destination search box (later station suggestion drop-down / list)
    inputDestination.focus();
  });

  autocompleteDestin.addListener("place_changed", () => {
    const destin = autocompleteDestin.getPlace();

    //hides dropdown (if not already hidden) and sets loader visible
    document.getElementById("loader2").style.visibility = "visible";
    document.getElementById("loader2").style.position = "relative";
    document.getElementById("select_destination_wrapper").style.display =
      "none";

    if (!destin.geometry || !destin.geometry.location) {
      // User entered the name of a Place that was not suggested and
      // pressed the Enter key, or the Place Details request failed.
      window.alert("No details available for input: '" + destin.name + "'");
      return;
    }

    const destinLatLng = {
      lat: destin.geometry.location.lat(),
      lng: destin.geometry.location.lng(),
    };
    const request_params = {
      lat: destin.geometry.location.lat(),
      lng: destin.geometry.location.lng(),
      dt: current_date,
      tm: current_time,
    };
    placeDestination.LatLng = destinLatLng;
    placeDestination.name = destin.name;
    // Print Selected place name beneath search box

    //post destination to flask, return array of 5 nearest stations and call function to populate dropdown
    postData("API/destin", request_params).then((data) => {
      destination_stations = data.stations;
      forecast_weather = data.weather;
      PopulateEndStationSuggestions(destination_stations);
    });

    // Display route (later focus on station suggestion drop-down / list)
  });

  // calculate a route, journeyLeg one of {leg0, leg1, leg2}
  function calcRoute(place1, place2, journeyLeg, mode) {
    var start = place1;
    var end = place2;

    var request = {
      origin: start,
      destination: end,
      travelMode: mode,
    };
    directionsService.route(request, function (response, status) {
      if (status == "OK") {
        let infoA;
        let infoB;
        let returnPos;
        if (journeyLeg == "leg0") {
          infoA = placeOrigin.name;
          infoB = selected_start_station.name;
          returnPos = 0;
        } else if (journeyLeg == "leg1") {
          infoA = selected_start_station.name;
          infoB = selected_end_station.name;
          returnPos = 1;
        } else if (journeyLeg == "leg2") {
          infoA = selected_end_station.name;
          infoB = placeDestination.name;
          returnPos = 2;
        }
        let info = document.getElementById(journeyLeg);
        let text = infoA + " to " + infoB;
        let duration = response.routes[0].legs[0].duration.text;
        info.children[1].innerHTML = text;
        info.children[2].innerHTML = duration;
        // If forecast weather exists parse & display
        if (forecast_weather.detail) {
          let forecastTemp = Math.round(forecast_weather.temp * 10) / 10;
          let weatherText =
            "<strong> Predicted Weather:</strong> " +
            forecast_weather.detail +
            ", " +
            forecastTemp +
            "&#176C";
          let weatherIcon =
            "<img src='static/images/icons/" +
            forecast_weather.icon +
            "@2x.png' width='25px' height='25px'>";
          predictionInfo.children[1].innerHTML = weatherText;
          predictionInfo.children[0].innerHTML = weatherIcon;
          predictionInfo.style.visibility = "visible";
        } else {
          predictionInfo.style.visibility = "collapse";
        }
        // Toggle Explanation & Route Plan
        if (
          document.getElementById("routeExplainTable").style.display == "table"
        ) {
          document.getElementById("routeExplainTable").style.display = "none";
          document.getElementById("routePlanTable").style.display = "table";
          document.getElementById("leg0").style.visibility = "hidden";
          document.getElementById("leg1").style.visibility = "hidden";
          document.getElementById("leg2").style.visibility = "hidden";
        }
        if (info.style.visibility != "visible") {
          info.style.visibility = "visible";
        }
        if (
          document.getElementById("routeButtons").style.visibility != "visible"
        ) {
          document.getElementById("routeButtons").style.visibility = "visible";
        }
        routes[returnPos] = response;

        if (
          !(
            directionsRenderer0.directions === null &&
            directionsRenderer1.directions === null &&
            directionsRenderer2.directions === null
          )
        ) {
          renderRoute();
        }
      }
    });
  }

  // display a route on the map
  function renderRoute() {
    //
    directionsRenderer0.setMap(map);
    directionsRenderer1.setMap(map);
    directionsRenderer2.setMap(map);
    // Render routes which have been set
    if (routes[0]) directionsRenderer0.setDirections(routes[0]);
    if (routes[1]) directionsRenderer1.setDirections(routes[1]);
    if (routes[2]) directionsRenderer2.setDirections(routes[2]);
    // Calc Bounds of entire composite route & set view to show whole route
    let routeBounds;
    if (routes[0]) {
      routeBounds = routes[0].routes[0].bounds;
      if (routes[1]) {
        routeBounds = routeBounds.union(routes[1].routes[0].bounds);
        if (routes[2])
          routeBounds = routeBounds.union(routes[2].routes[0].bounds);
      }
    }
    if (routeBounds) map.fitBounds(routeBounds, 30); // 30px padding around routeBounds

    // set hide route map button to visible
    document.getElementById("route").style.display = "block";

    //close open infoWindow
    infoWindow.close();
  }

  // reset all route related objects
  function resetRoute() {
    // Clear journey plan text
    document.getElementById("leg0").style.visibility = "collapse";
    document.getElementById("leg1").style.visibility = "collapse";
    document.getElementById("leg2").style.visibility = "collapse";
    document.getElementById("routeButtons").style.visibility = "collapse";
    document.getElementById("weatherPrediction").style.visibility = "collapse";
    // Show Route Planner Explanation Text
    document.getElementById("routeExplainTable").style.display = "table";
    document.getElementById("routePlanTable").style.display = "none";

    // Reset Autocomplete
    inputOrigin.value = "";
    inputDestination.value = "";

    // Remove route rendering
    hideRoute();

    // Hides dropdowns if reset
    document.getElementById("select_origin_wrapper").style.display = "none";
    document.getElementById("select_destination_wrapper").style.display =
      "none";

    // Reset Variables (Before resetting Time Selector to avoid route recalc)
    selected_start_station = {};
    selected_end_station = {};
    placeOrigin = {};
    placeDestination = {};
    routes = {};
    forecast_weather = {};

    // Reset Time Selector
    PopulateDateOptions();
    setDateValue("Today");
    PopulateTimeOptions();
    setTimeValue("Now");
  }

  // remove rendered route from map
  function hideRoute() {
    directionsRenderer0.set("directions", null);
    directionsRenderer1.set("directions", null);
    directionsRenderer2.set("directions", null);
    directionsRenderer0.setMap(null);
    directionsRenderer1.setMap(null);
    directionsRenderer2.setMap(null);

    //remove hide route button from map
    document.getElementById("route").style.display = "none";
  }

  // point to above functions for access
  f.calcRoute = calcRoute;
  f.drawRoute = renderRoute;
  f.resetRoute = resetRoute;
  f.hideRoute = hideRoute;
} 

function openTab(event, tabName) {
  // Hide elements with class="tabcontent"
  var tabcontent = document.getElementsByClassName("tabcontent");
  for (var i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="sidebar_tabs" and remove the class "active"
  var sidebar_tabs = document.getElementsByClassName("sidebar_tabs");
  for (i = 0; i < sidebar_tabs.length; i++) {
    sidebar_tabs[i].className = sidebar_tabs[i].className.replace(
      " active",
      ""
    );
  }

  // Show current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  event.currentTarget.className += " active";
}

//set map controls to change number on markers from available bikes<->stands

function setMapControls(buttonDiv, map) {
  //style map controls
  var buttonText = document.createElement("div");
  buttonDiv.style.backgroundColor = "white";
  buttonDiv.style.border = "2px solid gray";
  buttonDiv.style.borderRadius = "3px";
  buttonDiv.style.height = "30px";
  buttonDiv.style.width = "100px";
  buttonDiv.style.fontSize = "12px";
  buttonDiv.style.boxShadow = "0 2px 6px rgba(0,0,0,.3)";
  buttonDiv.style.cursor = "pointer";
  buttonDiv.style.textAlign = "center";

  //add icons & text
  if (buttonDiv.id == "bikes") {
    buttonDiv.style.backgroundColor = "#f1f1f1";
    buttonDiv.innerHTML = "<i class='fas fa-bicycle'></i><br>Available Bikes";
    buttonDiv.style.cursor = "default";
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(buttonDiv);
  } else if (buttonDiv.id == "stands") {
    buttonDiv.innerHTML = "<i class='fas fa-parking'></i><br>Available Stands";
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(buttonDiv);
  } else {
    buttonDiv.innerHTML = "<i class='fa fa-window-close'></i><br>Hide Route";
    buttonDiv.style.display = "none";
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(buttonDiv);
  }

  buttonDiv.appendChild(buttonText);

  //add listeners for controls, change background color and cursor when clicked
  buttonDiv.addEventListener("click", () => {
    if (buttonDiv.id == "route") {
      f.hideRoute();
    } else {
      buttonDiv.setAttribute("class", "active");
      if (buttonDiv.id == "bikes") {
        document.getElementById("stands").setAttribute("class", "inactive");
        document.getElementById("stands").style.cursor = "pointer";
        document.getElementById("stands").style.backgroundColor = "white";
      } else {
        document.getElementById("bikes").setAttribute("class", "inactive");
        document.getElementById("bikes").style.cursor = "pointer";
        document.getElementById("bikes").style.backgroundColor = "white";
      }

      fetch("/stations")
        .then((response) => {
          return response.json();
        })
        .then((data) => {
          data.forEach((station) => {
            if (buttonDiv.id == "bikes") {
              var availability = station.availablebikes.toString();
            } else {
              var availability = station.availablestands.toString();
            }
            changeMarkers(buttonDiv, map, availability, station);
          });
        });
    }
  });
}

function changeMarkers(buttonDiv, map, availability, station) {
  //set new label for markers and change to grey icon if availability = 0
  buttonDiv.style.backgroundColor = "#f1f1f1";
  buttonDiv.style.cursor = "default";
  var label = StationMarkers[station.number].getLabel();
  if (availability == 0) {
    StationMarkers[station.number].setIcon(altMarkerIcon);
  } else {
    StationMarkers[station.number].setIcon(markerIcon);
  }

  label.text = availability;
  StationMarkers[station.number].setLabel(label);
}
