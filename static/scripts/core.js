// Shared frontend code

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
     if(!IsValidGameID(gameID)) return;

     let req = new XMLHttpRequest();
     req.onreadystatechange = function() {
       if(this.readyState == 4)
       {
         oncompleted(JSON.parse(this.responseText));
       }
     };

     req.open("GET", GetAPIRoot() + "/game/" + gameID, true);
     req.send();
   }

   e.GetAPIRoot = function()
   {
     return document.location.origin + "/api"
   }
})(typeof exports === 'undefined'? this : exports);
