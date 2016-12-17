function getEmployeList(){      
  var input=$("#search_input").val().toLowerCase().split(/\s+/g);
  var first_name=input[0];
  var last_name=input[1];
  var url="/SEI/get_employee/"+first_name+"/"+last_name;
  $.get(url)
  .done(function(data) {
      for(var i=0;i<data.length;i++){
        var employee_list=$("#employee_list");
        employee=data[i];
        var employee_name=employee["first_name"]+" "+employee["last_name"];
        var team_name=employee.team_name;
        var employee_id=employee.id;
        employee_list.append("<li class='list-group-item' id=\""+employee_id+"\">Name:"+employee_name+"\tTeam:"+team_name+"</li>");
      }
      $('#myModal').modal({show:true});  
  });
}

function show_morris_content(e){
  var employee_id=$(e.target).attr("id");
  var employee_name=$(e.target).text();
  show_morris(employee_id,employee_name);
}

//show morris js content, including donut and line chart
function show_morris(id,employee_name){
  $("#header").show()
  $("#employee_name").text(employee_name)
  $("#morris-donut-chart").empty()
  $("#morris-line-chart").empty()
  var url="/SEI/get_employee_project/"+id;
  $.get(url)
   .done(function(data){
      renderDonutChart(data);
      renderLineChart(data);
   });
}

function removeModal(){
  var employees=$("#employee_list").children("li");
  for(var i=0;i<employees.length;i++){
    $(employees[i]).remove();
  }
}

//show current month allocation chart
function renderDonutChart(data){
  var json=JSON.parse(data)
  var donut_chart=$("#donut_chart")
  donut_chart.hide()
    var d = new Date();
    var currentmonth = d.getYear()+1900+"-"+(d.getMonth()+1)+"-01";
    donut_data=[]
    if(currentmonth in json){
      month_data=json[currentmonth]
      for(var i=0;i<month_data.length;i++){
        donut_data.push({label:month_data[i].PWP_num,value:month_data[i].time_use})
      }
    }
    donut_chart.show()
    if(donut_data.length!=0){
        Morris.Donut({
            element: 'morris-donut-chart',
            data: donut_data,
            resize:true
      });
    } 
}

//show trends graph
function renderLineChart(data){
    var json=JSON.parse(data)
    var line_chart=$("#line_chart");
    line_chart.hide();
    var linechart_data=[]
    var PWP_nums=[]
    for(var month in json){
        var dict=[]
        dict['d']=month;
        var month_project=json[month];
        for(var i=0;i<month_project.length;i++){
          var PWP_num=month_project[i]["PWP_num"];
          var percentage=month_project[i]["percentage"];
          dict[PWP_num]=percentage;
          if(PWP_nums.indexOf(PWP_num)==-1){
             PWP_nums.push(PWP_num);
          }
        }
        linechart_data.push(dict);
    }
    line_chart.show();
    if(linechart_data.length!=0){
      var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    // Line Chart
    Morris.Line({
        // ID of the element in which to draw the chart.
        element: 'morris-line-chart',
        // Chart data records -- each entry in this array corresponds to a point on
        // the chart.
        data: linechart_data,
        // The name of the data record attribute that contains x-visitss.
        xkey: 'd',
        // A list of names of data record attributes that contain y-visitss.
        ykeys: PWP_nums,
        // Labels for the ykeys -- will be displayed when you hover over the
        // chart.
        labels: PWP_nums,
        // Disables line smoothing
        smooth: false,
        resize: true,
        xLabelFormat: function (x) { return x.getYear()-100+"-"+months[x.getMonth()];}
    });
    }
}

function show_d3_content(e){
    var employee_id=$(e.target).attr("id");
    show_d3(employee_id);
}

//shwo d3 content--resource allocation graph
function show_d3(employee_id){
   project_allocation_chart=$("#visavailchart")
    var year=new Date().getFullYear();
    $.get("/SEI/get_employee_allocation/"+employee_id+"/"+year)
    .done(function(data){
        var json = JSON.parse(data);
        var chart = visavailChart().width(800);
        dataset=[];
        if (json['resource_chart_data'] != null && json['resource_chart_data'].length > 0){
          dataset = json['resource_chart_data']
        }
        else
          dataset = []
        
        project_allocation_chart.empty();
        d3.select("#visavailchart")
          .datum(dataset)
          .call(chart);
    });
    $("#project_allocation_chart").show();
    $("#reportform").attr("action", "/SEI/report_employee/"+employee_id);
    $("#reporting").show();
}


$(function(){
    employee_id = $("#employee_id").val()
    //if employee_id is not empty, then file is directly from backend, 
    //thus no need to get input from search bar.
    if (employee_id != "")
    {
     employee_name=$("#first_name").val()+" "+$("#last_name").val();
     show_morris(employee_id,employee_name);
     show_d3(employee_id);
    }
    
    $("body").on('hidden.bs.modal', '.modal', function () {
       removeModal();
      });
      $("#search_btn").click(getEmployeList);
      $("#employee_list").on("click","li",show_d3_content);
      $("#employee_list").on("click","li",show_morris_content);
            $("#last_year").click(function(){
      var last_year = parseInt($("#year").text()) - 1;
      $("#year").text(last_year);
        getResourceAllocationChart(last_year);
      });

      $("#next_year").click(function(){
      var next_year = parseInt($("#year").text()) + 1;
      $("#year").text(next_year);
        getResourceAllocationChart(next_year);
      });
})