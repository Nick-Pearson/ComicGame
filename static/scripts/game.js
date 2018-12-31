// code for the game screen


var app = undefined;
var GameID = undefined;

window.onload = OnPageLoad;

app = new Vue({
  el: "#game",
  data: {
    gameInfo: undefined,
    GameState: GameState
  }
});

// Define a new component called todo-item
Vue.component('player-entry', {
  props: {
    'player':Object,
    'show_score': {type: Boolean, default: true}
  },
  template: `<div><h3>{{player.name}}<span v-if="show_score"> - {{player.score}}</span></h3></div>`
});


Vue.component('countdown-clock', {
  props: ['end_time'],
  created: function() {
    window.setInterval(() => {
        this.now = Math.round((new Date()).getTime() / 1000);
    },1000);
  },
  data: function() {
    return {
      now: Math.round((new Date()).getTime() / 1000)
    }
  },
  computed: {
    rem_time: function() {
      return Math.max(0, this.end_time - this.now);
    },
    minutes: function() {
      return Math.floor(this.rem_time / 60);
    },
    seconds: function() {
      return this.rem_time % 60;
    }
  },
  template: `<div class="countdown">{{ minutes }}:{{ seconds | two_digits}}</div>`
});

Vue.component("colour-picker", {
  props: {
    "colour": String,
    "selected": {type:Boolean, default:false}
  },
  data: function() {
    return {
      isSelected: this.selected
    };
  },
  methods: {
    onclick: function(e) {
      if(this.isSelected)
      {
        return;
      }

      this.$emit("clicked", this.colour);
      this.isSelected = true;
    }
  },
  template: `<div class="colour-picker" v-on:mousedown="onclick" v-bind:class="{ selected: isSelected }" v-bind:style="{ 'background-color': colour }"></div>`
});

Vue.component("panel-creator", {
  props: [],
  mounted: function() {
    this.context = this.$refs.canvas.getContext("2d");
    this.context.lineWidth = 20;
    this.context.lineCap = "round";
  },
  data: function() {
    return {
      context: undefined,
      penDown: false,
      touchdata: {}
    }
  },
  methods: {
    mousedown: function(event) {
      if(event.button == 0)
      {
        this.penDown = true;
      }
    },
    mouseup: function(event) {
      if(event.button == 0)
      {
        this.penDown = false;
      }
    },
    mousemove: function(event) {
      if(this.penDown)
      {
        let canvas = this.$refs.canvas;
        let scale = canvas.width / canvas.offsetWidth;
        this.context.moveTo(scale * (event.offsetX - event.movementX), scale * (event.offsetY - event.movementY));
        this.context.lineTo(scale * event.offsetX, scale * event.offsetY);
        this.context.stroke();
      }
    },
    touchstart: function(event) {
      for(let i = 0; i < event.changedTouches.length; i++)
      {
        console.log("Touch " + event.changedTouches[i].identifier + " start!");
        this.touchdata[event.changedTouches[i].identifier] = {x: event.changedTouches[i].pageX, y: event.changedTouches[i].pageY};
      }
    },
    touchend: function(event) {
      for(let i = 0; i < event.changedTouches.length; i++)
      {
        console.log("Touch " + event.changedTouches[i].identifier + " end");
        delete this.touchdata[event.changedTouches[i].identifier];
      }
    },
    touchmove: function(event) {
      event.preventDefault();

      let canvas = this.$refs.canvas;
      let scale = canvas.width / canvas.offsetWidth;
      let rect = canvas.getBoundingClientRect();

      for(let i = 0; i < event.touches.length; i++)
      {
        let offsetX = event.touches[i].pageX - rect.left;
        let offsetY = event.touches[i].pageY - rect.top;
        let lastX = this.touchdata[event.touches[i].identifier].x - rect.left;
        let lastY = this.touchdata[event.touches[i].identifier].y - rect.top;

        this.context.moveTo(scale * lastX, scale * lastY);
        this.context.lineTo(scale * offsetX, scale * offsetY);
        this.context.stroke();

        this.touchdata[event.touches[i].identifier] = {x: event.touches[i].pageX, y: event.touches[i].pageY};
      }
    },
    changecolour: function(colour) {
      this.context.strokeStyle = colour;
      this.context.beginPath();
    }
  },
  template: `<div class="row">
              <div class="left-toolbar col-sm-1">
                <colour-picker selected colour="#000" v-on:clicked="changecolour"></colour-picker>
                <colour-picker colour="#f00" v-on:clicked="changecolour"></colour-picker>
                <colour-picker colour="#0f0" v-on:clicked="changecolour"></colour-picker>
                <colour-picker colour="#00f" v-on:clicked="changecolour"></colour-picker>
              </div>
              <div class="col-sm-11">
                <canvas v-on:mousedown="mousedown" v-on:mouseup="mouseup" v-on:mousemove="mousemove" v-on:touchstart="touchstart" v-on:touchend="touchend" v-on:touchmove="touchmove" ref="canvas" width="1120" height="1600" style="max-height:90%; max-width: 100%"></canvas>
              </div>
            </div>`
});

Vue.filter('two_digits', function (value) {
  let str = value.toString();
  if(str.length <= 1)
  {
      return "0"+str;
  }
  return str;
});

function OnPageLoad()
{
  // Parse the Game ID from the URL
  GameID = GetQueryParam("id");

  if(!IsValidGameID(GameID))
  {
    // if game is not valid go home
    document.location = "/";
    return;
  }

  // Get game details from server
  GetGameInfo(GameID, function(info, found) {
    if(!found)
    {
      document.location = "/";
      return;
    }

    app.gameInfo = info;
  });
}

function StartGameClicked()
{
  let req = new XMLHttpRequest();
  req.onreadystatechange = function() {
    if(this.readyState == 4)
    {
      let res = JSON.parse(this.responseText);

      if(res.success === true)
      {
        app.gameInfo.state = res.state;
        app.gameInfo.round_end = res.end_time;
      }
    }
  };

  req.open("POST", GetAPIRoot() + "/game/start/" + encodeURIComponent(GameID), true);
  req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  req.send("gameID=" + encodeURIComponent(GameID));
}
