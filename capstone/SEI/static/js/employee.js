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
        employee_list.append("<li class='list-group-item' id=\""+employee_id+"\">Name:"+employee_name+"\t\t\tTeam:"+team_name+"</li>");
      }
      $('#myModal').modal({show:true});
  });
}

function showContent(e){
  var employee_id=$(e.target).attr("id");
  var url="/SEI/get_employee_project/"+employee_id;
  $.get(url)
   .done(function(data){
      renderDonutChart(data);
      renderLineChart(data);
      renderAllocationChart(data);
   });
}

function renderDonutChart(data){
    var donut_chart=$("#donut_chart")
    donut_chart.hide()
    var d = new Date();
    var currentmonth = d.getYear()+1900+"-"+d.getMonth()+1+"-01";
    donut_data=[]
    if(currentmonth in data){
      month_data=data[currentmonth]
      for(var i=0;i<month_data.length;i++){
        donut_data.push({label:month_data[i].PWP_num,value:month_data[i].time_use})
      }
    }

    if(donut_data.length!=0){
      Morris.Donut({
          element: 'morris-donut-chart',
          data: donut_data,
          resize: true
      });
    }
    
    donut_chart.show()
}

function renderLineChart(data){
    var line_chart=$("#line_chart");
    line_chart.hide();
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var linechart_data=[]
    var PWP_nums=[]
    for(var month in data){
        var dict=[]
        dict['d']=month;
        var month_project=data[month];
        for(var i=0;i<month_project.length;i++){
          var PWP_num=month_project[i]["PWP_num"];
          var percentage=month_project[i]["percentage"];
          dict[PWP_num]=percentage;
          if(!(PWP_num in PWP_nums)){
             PWP_nums.push(PWP_num);
          }
        }
        linechart_data.push(dict);
    }
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
        xLabelFormat: function (x) { return x.getYear()+1900+"-"+months[x.getMonth()];}
    });
    line_chart.show();
}

  function renderAllocationChart(data){
        var resourcerow=$("#resource_chart");
        resourcerow.show();

  }


$(function(){
    $("#search_btn").click(getEmployeList);

    // $("#myModal").on("show.bs.modal", getEmployeList);
    $("#employee_list").on("click","li",showContent);
})