// Shared frontend code

/*
STARTING      = Waiting for players to join the game
DRAWING       = Creating panels
DISTRIBUTING  = Internal state: finishing up image upload from clients, randomising the panels and distributing them to players
CREATING      = players are making strips
GATHERING     = Internal state: finishing upload of any created strips
RATING        = Quick fire rating strips off against eachother
SCOREBOARD    = Game is over, display scoreboard. The game remains in this state forevermore
*/
var GameState = Object.freeze({"STARTING": 0, "DRAWING": 1, "DISTRIBUTING": 2, "CREATING": 3, "GATHERING": 4, "RATING": 5, "SCOREBOARD": 6});

//closure JS magic so it works in NodeJS and browsers
(function(e){

   e.IsValidGameID = function(id)
   {
     return e.isString(id) && (/^(\s)*[A-Z][A-Z][A-Z][A-Z](\s)*$/i).test(id);
   }

   e.isString = function(value)
   {
     return typeof value === 'string' || value instanceof String;
   }

   e.GetQueryParam = function(key)
   {
     let query = document.location.search;
     if(query.length == 0) return undefined;

     query = query.substr(1);
     parts = query.split('&');

     for(let i = 0; i < parts.length; i++)
     {
       let values = parts[i].split('=');
       if(values.length < 2) return;

       if(values[0] == key)
       {
         return decodeURIComponent(values[1]);
       }
     }

     return undefined;
   }

   e.GetGameInfo = function(gameID, oncompleted)
   {
     if(!e.IsValidGameID(gameID)) return;

     let req = new XMLHttpRequest();
     req.onreadystatechange = function() {
       if(this.readyState == 4)
       {
         oncompleted(JSON.parse(this.responseText), this.status == 200);
       }
     };

     req.open("GET", e.GetAPIRoot() + "/game/" + gameID, true);
     req.send();
   }

   e.GetAPIRoot = function()
   {
     return document.location.origin + "/api"
   }
})(typeof exports === 'undefined'? this : exports);
