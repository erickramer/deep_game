function create_update_board(data){

  function update_board(data){
    var dots_data = data.dots,
        circle_data = data.circles,
        triangle_data = data.triangles

    var t = d3.transition()
      .duration(100)

    // DOTS

    var dots = svg.selectAll(".dot")
      .data(dots_data, function(d){return d.id})

    // enter any new dots
    dots.enter()
      .append("circle")
      .attr("class", "dot")
      .attr("r", dot_radius)
      .attr("cx", function(d){return x(d.x)})
      .attr("cy", function(d){return y(d.y)})
      .attr("fill", "lightgray")

    // update dot position
    dots.transition(t)
      .attr("cx", function(d){return x(d.x)})
      .attr("cy", function(d){return y(d.y)})

    dots.exit()
      .remove()

    // CIRCLES
    var circles = svg.selectAll(".animal")
      .data(circle_data, function(d){return d.id})

    circles.enter()
      .append("circle")
      .attr("class", "animal")
      .attr("r", circle_radius)
      .attr("cx", function(d){return x(d.x)})
      .attr("cy", function(d){return y(d.y)})
      .attr("fill", "black")

    circles.transition(t)
      .attr("cx", function(d){return x(d.x)})
      .attr("cy", function(d){return y(d.y)})

    circles.exit()
      .remove()

    // triangles

    var triangles = svg.selectAll(".triangle")
      .data(triangle_data, function(d){return d.id})

    triangles.enter()
      .append("circle")
      .attr("class", "triangle")
      .attr("r", triangle_radius)
      .attr("cx", function(d){return x(d.x)})
      .attr("cy", function(d){return y(d.y)})
      .attr("fill", "red")

    triangles.transition(t)
      .attr("cx", function(d){return x(d.x)})
      .attr("cy", function(d){return y(d.y)})

    triangles.exit()
      .remove()

  }

  var dot_radius = 3,
      circle_radius = 10,
      triangle_radius = 3

  var margin = {top: 20, right: 10, bottom: 20, left: 10};

  var width = 620 - margin.left - margin.right,
      height = 440 - margin.top - margin.bottom

  var svg = d3.select("#game")
    .append("svg")
    .attr("height", height + margin.top + margin.bottom)
    .attr("width", width + margin.left + margin.right)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var x = d3.scaleLinear()
    .range([0, width])
    .domain([0, 600])

  var y = d3.scaleLinear()
    .range([height, 0])
    .domain([0, 400])

  update_board(data)

  return update_board
}

function generate_data(){

  var dots = d3.range(10).map(function(i){
    return {id: i, x: Math.random()*600, y: Math.random()*400}
  })
  var data = {'dots': dots}
  return(data);
}


$('document').ready(function(){

  var direction = '';
  var ai = false;


  $.get('/board/state', function(data){
    var update_board = create_update_board(data)

    setInterval(function(){

      data = {'name': 0, 'direction': direction}

      $.post('/board/update', data, function(board){
        $("#score").text("Score: " + board.score)
        update_board(board);
      })
    }, 100)

  })

  $(document).keydown(function(e){
    if(e.keyCode == 37){
      direction = 'left';
      //console.log(direction)
    } else if(e.keyCode == 39){
      direction = 'right';
      //console.log(direction)
    } else if(e.keyCode == 38){
      direction = 'up';
    } else if(e.keyCode == 40){
      direction = 'down';
    }
  }).keyup(function(e){
    if(e.keyCode == 37 || e.keyCode == 39){
      direction = '';
      //console.log('up')
    } else if(e.keyCode == 38 || e.keyCode == 40){
      direction = '';
    }
  })

  $("#reset").click(function(){
    $.get('/board/reset', function(board){
      $("#score").text("Score: " + board.score)
    })
  })

  $("#ai").click(function(){
    if($(this).attr('class') == "button-primary"){
      $(this).removeClass('button-primary')
      ai = false
    } else{
      $(this).addClass('button-primary')
      ai = true
    }
  })

})
