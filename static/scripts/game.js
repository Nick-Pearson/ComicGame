// code for the game screen


var app = undefined;
var GameID = undefined;

window.onload = OnPageLoad;

app = new Vue({
  el: "#game",
  data: {
    gameInfo: undefined,
    GameState: GameState,
    waitingForPlayers: false
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
    "selected": {type:Boolean, default:false},
    "id": String
  },
  methods: {
    onclick: function(e) {
      if(this.selected)
      {
        return;
      }

      this.$emit("clicked", this.colour, this.id);
    }
  },
  template: `<div class="colour-picker" v-on:mousedown="onclick" v-bind:class="{ selected: selected }" v-bind:style="{ 'background-color': colour }"></div>`
});

Vue.component("panel-creator", {
  props: [],
  mounted: function() {
    let canvas = this.$refs.canvas;
    this.context = canvas.getContext("2d");
    this.context.lineWidth = 20;
    this.context.lineCap = "round";

    this.context.beginPath();
    this.context.rect(0, 0, canvas.width, canvas.height);
    this.context.fillStyle = "#fff";
    this.context.fill();
    this.context.beginPath();
  },
  data: function() {
    return {
      context: undefined,
      penDown: false,
      touchdata: {},
      curTool: "0"
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
        this.touchdata[event.changedTouches[i].identifier] = {x: event.changedTouches[i].pageX, y: event.changedTouches[i].pageY};
      }
    },
    touchend: function(event) {
      for(let i = 0; i < event.changedTouches.length; i++)
      {
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
    changecolour: function(colour, id) {
      this.context.strokeStyle = colour;
      this.context.beginPath();

      this.curTool = id;
    },
    submitimage: function(colour) {
      let canvas = this.$refs.canvas;
      let data = canvas.toDataURL();

      let req = new XMLHttpRequest();
      let that = this;
      req.onreadystatechange = function() {
        if(this.readyState == 4)
        {
          // clear the screen
          that.context.beginPath();
          that.context.rect(0, 0, canvas.width, canvas.height);
          that.context.fillStyle = "#fff";
          that.context.fill();
          that.context.beginPath();
          that.$refs.prompt.scrollIntoView();
        }
      };

      req.open("POST", GetAPIRoot() + "/game/" + encodeURIComponent(GameID) + "/panels", true);
      req.setRequestHeader("Content-type", "data:image/png;base64");
      req.send(data);
    }
  },
  template: `<div class="row">
              <div class="left-toolbar col-sm-1" ref="toolbar">
                <colour-picker v-bind:selected="curTool==0" id=0 colour="#000" v-on:clicked="changecolour"></colour-picker>
                <colour-picker v-bind:selected="curTool==1" id=1 colour="#f00" v-on:clicked="changecolour"></colour-picker>
                <colour-picker v-bind:selected="curTool==2" id=2 colour="#0f0" v-on:clicked="changecolour"></colour-picker>
                <colour-picker v-bind:selected="curTool==3" id=3 colour="#00f" v-on:clicked="changecolour"></colour-picker>
              </div>
              <div class="alert alert-primary" role="alert"ref="prompt">
                Great work! Create some more panels
              </div>
              <div class="col-sm-11">
                <canvas v-on:mousedown="mousedown" v-on:mouseup="mouseup" v-on:mousemove="mousemove" v-on:touchstart="touchstart" v-on:touchend="touchend" v-on:touchmove="touchmove" ref="canvas" width="1120" height="1600" style="max-height:90%; max-width: 100%"></canvas>
                <a  href="javascript:void(0);" v-on:mousedown="submitimage"><button type="button" class="btn btn-primary">Done</button></a>
              </div>
            </div>`
});



Vue.component("strip-creator", {
  props: {
  },
  mounted: function() {
    let req = new XMLHttpRequest();
    let that = this;
    req.onreadystatechange = function() {
      if(this.readyState == 4)
      {
        data = JSON.parse(this.responseText);

        that.unusedImages = data.assignments;

        that.comic = [];

        that.curImageIdx = 0;
        that.updateCurrentImage();
      }
    };

    req.open("GET", GetAPIRoot() + "/game/" + encodeURIComponent(GameID) + "/assignments", true);
    req.send();
  },
  data: function() {
    return {
      curImage: "http://localhost:5000/static/images/loading.gif",
      unusedImages: [],
      comic: [],
      curImageIdx: 0,
      panel1: "http://localhost:5000/static/images/panel1.png",
      panel2: "http://localhost:5000/static/images/panel2.png",
      panel3: "http://localhost:5000/static/images/panel3.png"
    }
  },
  methods: {
    addCurPanel: function() {
      this.comic.push(this.unusedImages[this.curImageIdx]);
      this.unusedImages.splice(this.curImageIdx, 1);

      this.updateCurrentImage();
      this.updateComic();
    },
    prevPanel: function() {
      this.curImageIdx--;
      this.updateCurrentImage();
    },
    nextPanel: function() {
      this.curImageIdx++;
      this.updateCurrentImage();
    },
    submit: function() {
      let req = new XMLHttpRequest();
      let that = this;

      req.open("POST", GetAPIRoot() + "/game/" + encodeURIComponent(GameID) + "/comics", true);
      req.setRequestHeader("Content-type", "application/json");
      req.send(JSON.stringify({"comic": this.comic}));

      app.waitingForPlayers = true;
    },
    updateComic: function() {
      this.panel1 = "http://localhost:5000/static/images/panel1.png";
      this.panel2 = "http://localhost:5000/static/images/panel2.png";
      this.panel3 = "http://localhost:5000/static/images/panel3.png";

      let len = this.comic.length;
      if (len > 0)
      {
        this.panel1 = this.getImageURLFor(this.comic[0]);

        if(len > 1)
        {
          this.panel2 = this.getImageURLFor(this.comic[1]);

          if(len > 2)
            this.panel3 = this.getImageURLFor(this.comic[2]);
        }
      }
    },
    updateCurrentImage: function() {
      if(this.curImageIdx >= this.unusedImages.length)
      {
        this.curImageIdx = this.unusedImages.length - 1;
      }
      else if(this.curImageIdx < 0)
      {
        this.curImageIdx = 0;
      }

      this.curImage = this.getImageURLFor(this.unusedImages[this.curImageIdx]);
    },
    getImageURLFor: function(id) {
      return document.location.origin + "/image/" + id;
    },
    removeComicAt: function(idx)
    {
      if(this.comic.length > idx)
      {
        this.comic.splice(idx, 1);
      }
    }
  },
  template: `<div>
              <div class="panel-gallery">
                <div><a href="javascript:void(0);" v-on:click="prevPanel" v-bind:class="{invisible: curImageIdx<=0}">
                  <img src="static/images/prev.png" width=36px/>
                </a></div>
                <div><a href="javascript:void(0);" v-on:click="addCurPanel">
                  <img v-bind:src="curImage" style="width:100%;"/>
                </a></div>
                <div><a href="javascript:void(0);" v-on:click="nextPanel" v-bind:class="{invisible: curImageIdx>=unusedImages.length-1}">
                  <img src="static/images/next.png" width=36px />
                </a></div>
              </div>
              <div class="row">
                <div class="col-md-4 col-sm-4 col-xs-4 col-4">
                  <a href="javascript:void(0);" v-on:click="removeComicAt(0)">
                    <img v-bind:src="panel1" width="98%"/>
                  </a>
                </div>
                <div class="col-md-4 col-sm-4 col-xs-4 col-4">
                  <a href="javascript:void(0);" v-on:click="removeComicAt(1)">
                    <img v-bind:src="panel2" width="98%"/>
                  </a>
                </div>
                <div class="col-md-4 col-sm-4 col-xs-4 col-4">
                  <a href="javascript:void(0);" v-on:click="removeComicAt(2)">
                    <img v-bind:src="panel3" width="98%"/>
                  </a>
                </div>
                <a  href="javascript:void(0);" v-on:click="submit" v-if="comic.length == 3"><button type="button" class="btn btn-primary">Done</button></a>
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

    SubscribeToWebsocket();
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

  req.open("POST", GetAPIRoot() + "/game/" + encodeURIComponent(GameID) + "/start", true);
  req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  req.send("gameID=" + encodeURIComponent(GameID));
}

function SubscribeToWebsocket()
{
  let ws = io.connect('http://' + document.domain + ':' + location.port);
  ws.on('connect', function() {
      console.log('Websocket connected!');

      ws.emit('subscribe', {"game_id": GameID});
  });


  ws.on('disconnect', function() {
    GetGameInfo(GameID, function(info, found) {
      if(found)
      {
          app.gameInfo = info;
      }
    });
  });

  // message handler for the 'join_room' channel
  ws.on('update', function(data) {
    let keys = Object.keys(data);
    keys.forEach(function(key) {
      app.gameInfo[key] = data[key];
    });
  });

  ws.on('new_player', function(player) {
    app.gameInfo.players.push(player);
  });
}

function OnSocketMessage(event)
{
  console.log("Recieved:");
  console.log(event);
}
