function visavailChart() {
  // define chart layout
  var margin = {
    // top margin includes title and legend
    top: 70,

    // right margin should provide space for last horz. axis title
    right: 40,

    bottom: 20,

    // left margin should provide space for y axis titles
    left: 100,
  };

  // height of horizontal data bars
  var dataHeight = 18;

  // spacing between horizontal data bars
  var lineSpacing = 14;

  // vertical space for heading
  var paddingTopHeading = -50;

  // vertical overhang of vertical grid lines on bottom
  var paddingBottom = 10;

  // space for y axis titles
  var paddingLeft = -100;

  var width = 940 - margin.left - margin.right;

  // title of chart is drawn or not (default: yes)
  var drawTitle = 1;

  // year ticks to be emphasized or not (default: yes)
  var emphasizeYearTicks = 1;

  // define chart pagination
  // max. no. of datasets that is displayed, 0: all (default: all)
  var maxDisplayDatasets = 0;

  // dataset that is displayed first in the current
  // display, chart will show datasets "curDisplayFirstDataset" to
  // "curDisplayFirstDataset+maxDisplayDatasets"
  var curDisplayFirstDataset = 0;

  var xaxis_link = null;

  var chart_year = new Date().getFullYear();
  
  var pwp_num = "";
  
  //assumes key same name as category 
  var ycolors = {};

  var ygroups = [];

  // global div for tooltip
  var div = d3.select('#visavailchart').append('div')
  .attr('class', 'tooltip')
  .style('opacity', 0);

  var definedBlocks = null;
  var isDateOnlyFormat = null;

  function chart(selection) {
    selection.each(function drawGraph(dataset) {
      // check which subset of datasets have to be displayed
      var maxPages = 0;
      var startSet;
      var endSet;
      if (maxDisplayDatasets !== 0) {
        startSet = curDisplayFirstDataset;
        if (curDisplayFirstDataset + maxDisplayDatasets > dataset.length) {
          endSet = dataset.length;
        } else {
          endSet = curDisplayFirstDataset + maxDisplayDatasets;
        }
        maxPages = Math.ceil(dataset.length / maxDisplayDatasets);
      } else {
        startSet = 0;
        endSet = dataset.length;
      }

      // append data attribute in HTML for pagination interface
      selection.attr('data-max-pages', maxPages);

      var noOfDatasets = endSet - startSet;
      var height = dataHeight * noOfDatasets + lineSpacing * noOfDatasets - 1;

      // check how data is arranged
      if (definedBlocks === null) {
        definedBlocks = 0;
        for (var i = 0; i < dataset.length; i++) {
          if (dataset[i].data[0].length === 3) {
            definedBlocks = 1;
            break;
          } else {
            if (definedBlocks) {
              throw new Error('Detected different data formats in input data. Format can either be ' +
                'continuous data format or time gap data format but not both.');
            }
          }
        }
      }

      // parse data text strings to JavaScript date stamps
      var parseDate = d3.time.format('%Y-%m-%d');
      var parseDateTime = d3.time.format('%Y-%m-%d %H:%M:%S');
      var parseDateRegEx = new RegExp(/^\d{4}-\d{2}-\d{2}$/);
      var parseDateTimeRegEx = new RegExp(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/);
      if (isDateOnlyFormat === null) {
        isDateOnlyFormat = true;
      }
      dataset.forEach(function (d) {
        d.data.forEach(function (d1) {
          if (!(d1[0] instanceof Date)) {
            if (parseDateRegEx.test(d1[0])) {
              // d1[0] is date without time data
              d1[0] = parseDate.parse(d1[0]);
            } else if (parseDateTimeRegEx.test(d1[0])) {
              // d1[0] is date with time data
              d1[0] = parseDateTime.parse(d1[0]);
              isDateOnlyFormat = false;
            } else {
              throw new Error('Date/time format not recognized. Pick between \'YYYY-MM-DD\' or ' +
                '\'YYYY-MM-DD HH:MM:SS\'.');
            }
          }
        });
      });

      // cluster data by dates to form time blocks
      dataset.forEach(function (series, seriesI) {
        var tmpData = [];
        var dataLength = series.data.length;
        series.data.forEach(function (d, i) {
          if (i !== 0 && i < dataLength) {
              // the value has changed since the last date
              d[3] = 0;
              if (!definedBlocks) {
                // extend last block until new block starts
                tmpData[tmpData.length - 1][2] = d[0];
              }
              tmpData.push(d);
          } else if (i === 0) {
            d[3] = 0;
            tmpData.push(d);
          }
        });
        dataset[seriesI].disp_data = tmpData;
      });

      // determine start and end dates among all nested datasets
      var startDate = 0;
      var endDate = 0;


      //force data range to current year January - December
      //can change range here specifiying project start and end dates instead
      //recommend making as attributes passed into grid or as part of the json data in that case
      //var parseDate = d3.time.format('%Y-%m-%d');
      startDate = parseDate.parse(chart_year + "-01-01");
      endDate = d3.time.year.offset(startDate, 1);

      // define scales
      var xScale = d3.time.scale()
      .domain([startDate, endDate])
      .range([0, width])
      .clamp(1);

      // define axes
      var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient('top');

      // create SVG element
      var svg = d3.select(this).append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      // create basic element groups
      svg.append('g').attr('id', 'g_title');
      svg.append('g').attr('id', 'g_axis');
      svg.append('g').attr('id', 'g_data');

      // create y axis labels
      svg.select('#g_axis').selectAll('text')
      .data(dataset.slice(startSet, endSet))
      .enter()
      .append('text')
      .attr('x', paddingLeft)
      .attr('y', lineSpacing + dataHeight / 2)
      .text(function (d) {
        return d.measure;
      })
      .attr('transform', function (d, i) {
        return 'translate(0,' + ((lineSpacing + dataHeight) * i) + ')';
      })
      .attr('class', 'ytitle');

      // create vertical grid
      svg.select('#g_axis').selectAll('line.vert_grid').data(xScale.ticks())
      .enter()
      .append('line')
      .attr({
        'class': 'vert_grid',
        'x1': function (d) {
          return xScale(d);
        },
        'x2': function (d) {
          return xScale(d);
        },
        'y1': 0,
        'y2': dataHeight * noOfDatasets + lineSpacing * noOfDatasets - 1 + paddingBottom
      });

      // create horizontal grid
      svg.select('#g_axis').selectAll('line.horz_grid').data(dataset)
      .enter()
      .append('line')
      .attr({
        'class': 'horz_grid',
        'x1': 0,
        'x2': width,
        'y1': function (d, i) {
          return ((lineSpacing + dataHeight) * i) + lineSpacing + dataHeight / 2;
        },
        'y2': function (d, i) {
          return ((lineSpacing + dataHeight) * i) + lineSpacing + dataHeight / 2;
        }
      });


      // create x axis
      svg.select('#g_axis').append('g')
      .attr('class', 'axis')
      .call(xAxis)
      .selectAll("text")
      .on('click', function (d){
        if(xaxis_link != null){
          xaxis_link(moment(parseDate(d)).format('l'), pwp_num);              
        }
      })
      .on("mouseover", function(d) {
        d3.select(this).style("font-weight", "bold");
        div.transition()    
        .duration(200)    
        .style("opacity", .9);    
        div .html("Click here to add" + moment(parseDate(d)).format('l') + "resources")  
        .style("left", (d3.event.pageX) + "px")   
        .style("top", (d3.event.pageY - 28) + "px");  
      })          
      .on("mouseout", function(d) {   
        d3.select(this).style("font-weight", "normal");
        div.transition()    
        .duration(500)    
        .style("opacity", 0); 
      });

      // make y groups for different data series
      var g = svg.select('#g_data').selectAll('.g_data')
      .data(dataset.slice(startSet, endSet))
      .enter()
      .append('g')
      .attr('transform', function (d, i) {
        return 'translate(0,' + ((lineSpacing + dataHeight) * i) + ')';
      })
      .attr('class', 'dataset');

      // add data series
      g.selectAll('rect')
      .data(function (d) {
        return d.disp_data;
      })
      .enter()
      .append('rect')
      .attr('x', function (d) {
        return xScale(d[0]);
      })
      .attr('y', lineSpacing)
      .attr('width', function (d) {
        var d2 = d3.time.month.offset(d[0], 1);
        return (xScale(d2) - xScale(d[0]));
      })
      .attr('height', dataHeight)
      .attr('class', function (d) {
        if (d[1] > 0) {
          return 'rect_has_data';
        }
        return 'rect_has_no_data';
      })
      .on('mouseover', function (d, i) {
        var matrix = this.getScreenCTM().translate(+this.getAttribute('x'), +this.getAttribute('y'));
        div.transition()
        .duration(200)
        .style('opacity', 0.9);
        div.html(function () {
          var output = '';
          if (d[1] > 0) {
            output = '<i class="fa fa-fw fa-check tooltip_has_data"></i>';
          } else {
            output = '<i class="fa fa-fw fa-times tooltip_has_no_data"></i>';
          }
          if (isDateOnlyFormat) {
                return output + moment(parseDate(d[0])).format('l');
              } else {
                return output + moment(parseDateTime(d[0])).format('LTS'); 
              }
            })
        .style('left', function () {
          return window.pageXOffset + matrix.e + 'px';
        })
        .style('top', function () {
          return window.pageYOffset + matrix.f - 11 + 'px';
        })
        .style('height', dataHeight + 11 + 'px');
      })
      .on('mouseout', function () {
        div.transition()
        .duration(500)
        .style('opacity', 0);
      });

      // rework ticks and grid for better visual structure
      function isYear(t) {
        return +t === +(new Date(t.getFullYear(), 0, 1, 0, 0, 0));
      }

      function isMonth(t) {
        return +t === +(new Date(t.getFullYear(), t.getMonth(), 1, 0, 0, 0));
      }

      var xTicks = xScale.ticks();
      var isYearTick = xTicks.map(isYear);
      var isMonthTick = xTicks.map(isMonth);
      // year emphasis
      // ensure year emphasis is only active if years are the biggest clustering unit
      if (emphasizeYearTicks
        && !(isYearTick.every(function (d) { return d === true; }))
        && isMonthTick.every(function (d) { return d === true; })) {
        d3.selectAll('g.tick').each(function (d, i) {
          if (isYearTick[i]) {
            d3.select(this)
            .attr({
              'class': 'x_tick_emph',
            });
          }
        });
      d3.selectAll('.vert_grid').each(function (d, i) {
        if (isYearTick[i]) {
          d3.select(this)
          .attr({
            'class': 'vert_grid_emph',
          });
        }
      });
    }

      // create title
      if (drawTitle) {
        svg.select('#g_title')
        .append('text')
        .text('Allocations')
        .attr('x', paddingLeft)
        .attr('y', paddingTopHeading)
        .attr('class', 'heading');
      }

      // create subtitle
      var subtitleText = '';
      if (isDateOnlyFormat) {
        subtitleText = 'from ' + moment(parseDate(startDate)).format('MMMM Y') + ' to '
        + moment(parseDate(endDate)).format('MMMM Y');
      } else {
        subtitleText = 'from ' + moment(parseDateTime(startDate)).format('l') + ' '
        + moment(parseDateTime(startDate)).format('LTS') + ' to '
        + moment(parseDateTime(endDate)).format('l') + ' '
        + moment(parseDateTime(endDate)).format('LTS');
      }

      svg.select('#g_title')
      .append('text')
      .attr('x', paddingLeft)
      .attr('y', paddingTopHeading + 17)
      .text(subtitleText)
      .attr('class', 'subheading');

      // create legend
      var legend = svg.select('#g_title')
      .append('g')
      .attr('id', 'g_legend')
      .attr('transform', 'translate(0,-12)');

      legend.append('rect')
      .attr('x', width + margin.right - 150)
      .attr('y', paddingTopHeading)
      .attr('height', 15)
      .attr('width', 15)
      .attr('class', 'rect_has_data');

      legend.append('text')
      .attr('x', width + margin.right - 150 + 20)
      .attr('y', paddingTopHeading + 8.5)
      .text('Resource Allocated')
      .attr('class', 'legend');

    });
}

chart.width = function (_) {
  if (!arguments.length) return width;
  width = _;
  return chart;
};

chart.drawTitle = function (_) {
  if (!arguments.length) return drawTitle;
  drawTitle = _;
  return chart;
};

chart.maxDisplayDatasets = function (_) {
  if (!arguments.length) return maxDisplayDatasets;
  maxDisplayDatasets = _;
  


  svg.select('#g_axis').append('g')
  .attr('class', 'axis')
  .call(xAxis)
  .selectAll("text")
  .on('click', function (d){
    if(xaxis_link != null){
      xaxis_link(moment(parseDate(d)).format('l'));              
    }
  })


  return chart;
};

chart.curDisplayFirstDataset = function (_) {
  if (!arguments.length) return curDisplayFirstDataset;
  curDisplayFirstDataset = _;
  return chart;
};

chart.emphasizeYearTicks = function (_) {
  if (!arguments.length) return emphasizeYearTicks;
  emphasizeYearTicks = _;
  return chart;
};

chart.xaxis_link = function (_) {
  if (!arguments.length) return xaxis_link;
  xaxis_link = _;
  return chart;
};

chart.chart_year = function (_) {
  if (!arguments.length) return chart_year;
  chart_year = _;
  return chart;
};

chart.pwp_num = function (_) {
  if (!arguments.length) return pwp_num;
  pwp_num = _;
  return chart;
};


return chart;
}
