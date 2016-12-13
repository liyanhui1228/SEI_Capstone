function stackedBarChart(){


// space for y axis titles
var paddingLeft = 0;

var margin = {top: 50, right: 160, bottom: 50, left: 160};

var width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

//pass in groups for y
var ygroups = []

function chart(selection){
      selection.each(function drawGraph(data) {
var svg = d3.select(this)
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// Transpose the data into layers
var dataset = d3.layout.stack()(ygroups.map(function(expense) {
  return data.map(function(d) {
    return {x: d.month, y: +d[expense]};
  });
}));

console.log(data);

// Set x, y and colors
var x = d3.scale.ordinal()
  .domain(dataset[0].map(function(d) { return d.x }))
  .rangeRoundBands([10, width-10], 0.02);

var y = d3.scale.linear()
  .domain([0, d3.max(dataset, function(d) {  return d3.max(d, function(d) { return d.y0 + d.y; });  })])
  .range([height, 0]);


var colors = ["#d9534f", "#f0ad4e", "#3d8b3d", "#337ab7"];
  

// Define and draw axes
var yAxis = d3.svg.axis()
  .scale(y)
  .orient("left")
  .ticks(5)
  .tickSize(-width, 0, 0)
  .tickFormat(d3.format("$,"))


var xAxis = d3.svg.axis()
  .scale(x)
  .orient("bottom")
  .tickFormat(function(d) { return moment.monthsShort(d - 1) });

svg.append("g").attr("id", "g_title");

svg.append("g")
  .attr("class", "y axis")
  .attr("transform", "translate("+paddingLeft+",0)")
  .call(yAxis);

svg.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .call(xAxis);

// Create groups for each series, rects for each segment 
var groups = svg.selectAll("g.cost")
  .data(dataset)
  .enter().append("g")
  .attr("class", "cost")
  .style("fill", function(d, i) { return colors[i]; });

//draw bars
var rect = groups.selectAll("rect")
  .data(function(d) { return d; })
  .enter()
  .append("rect")
  .attr("x", function(d) { return x(d.x); })
  .attr("y", function(d) { return y(d.y0 + d.y); })
  .attr("height", function(d) { return y(d.y0) - y(d.y0 + d.y); })
  .attr("width", x.rangeBand())
  .on("mouseover", function() { tooltip.style("visibility", "visible"); })
  .on("mouseout", function() { tooltip.style("display", "none"); })
  .on("mousemove", function(d) {
    var xPosition = d3.mouse(this)[0] - 15;
    var yPosition = d3.mouse(this)[1] - 25;
    tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");
    tooltip.select("text").text(d.y);
  });

//draw line
var budgetline = d3.svg.line()
    .x(function(d) { return x(d.month); })
    .y(function(d) { return y(d.monthly_budget); })
    .interpolate("linear");

  svg.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("d", budgetline);

// Draw legend
var legend = svg.selectAll(".legend")
  .data(colors)
  .enter().append("g")
  .attr("class", "legend")
  .attr("transform", function(d, i) { return "translate(30," + i * 19 + ")"; });
 
legend.append("rect")
  .attr("x", width - 18)
  .attr("width", 18)
  .attr("height", 18)
  .style("fill", function(d, i) {return colors.slice().reverse()[i];});
 
legend.append("text")
  .attr("x", width + 5)
  .attr("y", 9)
  .attr("dy", ".35em")
  .style("text-anchor", "start")
  .text(function(d, i) { 
      return ygroups[ygroups.length - 1 - i]
  });


// Prep the tooltip bits, initial display is hidden
var tooltip = svg.append("g")
  .attr("class", "tooltip")
  .style("display", "none");
    
tooltip.append("rect")
  .attr("width", 30)
  .attr("height", 20)
  .attr("fill", "white")
  .style("opacity", 0.5);

tooltip.append("text")
  .attr("x", 15)
  .attr("dy", "1.2em")
  .style("text-anchor", "middle")
  .attr("font-size", "12px")
  .attr("font-weight", "bold");


//add titles to axes
padding = -90
svg.append("text")
    .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
    .attr("transform", "translate("+ ((padding-margin.left)/2) +","+(height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
    .text("Cost ($)");

svg.append("text")
    .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
    .attr("transform", "translate("+ (width/2) +","+(height-((padding-margin.bottom)/3))+")")  // centre below axis
    .text("Month");

svg.select('#g_title')
.append('text')
.text('Current Year Monthly Aggregated Project Expense by Category')
.attr('x', 125)
.attr('y', -margin.top/2)
.attr('class', 'heading');

});
}

chart.ygroups = function (_) {
  if (!arguments.length) return ygroups;
  ygroups = _;
  return chart;
};

return chart;
}
