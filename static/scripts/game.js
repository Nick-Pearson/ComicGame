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
    console.log("hello");

    window.setInterval(() => {
        this.now = Math.round((new Date()).getTime() / 1000);
        console.log("tick");
    },1000);
  },
  data: function() {
    return {
      now: Math.round((new Date()).getTime() / 1000)
    }
  },
  computed: {
    rem_time: function() {
      return this.end_time - this.now;
    },
    minutes: function() {
      return Math.floor(this.rem_time / 60);
    },
    seconds: function() {
      return this.rem_time % 60;
    }
  },
  template: `<div class="countdown">{{ minutes }}:{{ seconds | two_digits}}</div>`
})

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
  GetGameInfo(GameID, function(info) {
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
        app.drawEndTime = res.end_time;
        app.gameInfo.state = GameState.DRAWING;
      }
    }
  };

  req.open("POST", GetAPIRoot() + "/game/start", true);
  req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  req.send("gameID=" + encodeURIComponent(GameID));
}
