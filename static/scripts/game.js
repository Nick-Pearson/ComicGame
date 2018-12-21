// code for the game screen

var GameID = undefined;
var GameInfo = undefined;

// entry...
window.onload = OnPageLoad;

function OnPageLoad()
{
  // TODO:
  // Parse the Game ID from the URL
  GameID = GetQueryParam("id");

  if(!IsValidGameID(GameID))
  {
    document.location = "/";
  }

  // Get game details from server
  GetGameInfo(GameID, function(info) {
    GameInfo = info;
    RebuildUI();
  });

  // if game is valid display appropriate page otherwise show error message
}

// deletes and reconstructs the game UI
function RebuildUI()
{

}
