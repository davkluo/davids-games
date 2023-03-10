'use strict';

const DEFAULT_DIFFICULTY = 'beginner';
const DIFFICULTY_LEVELS = {
  beginner: {
    rows: 9,
    cols: 9,
    mines: 10
  },
  intermediate: {
    rows: 16,
    cols: 16,
    mines: 40
  },
  expert: {
    rows: 16,
    cols: 30,
    mines: 99
  }
};
const NEIGHBOUR_CELL_OFFSETS = [
  [-1, -1], [-1, 0], [-1, 1],
  [0, -1], [0, 1],
  [1, -1], [1, 0], [1, 1]
];
const NUM_SCORES_ON_LEADERBOARD = 20;

const BOMB_ICON_HTML = '<i class="fa-solid fa-bomb"></i>';
const FLAG_ICON_HTML = '<i class="fa-solid fa-flag"></i>';
const PAUSE_ICON_HTML = '<i class="fa-solid fa-pause"></i>';
const PLAY_ICON_HTML = '<i class="fa-solid fa-play"></i>';
const CROWN_ICON_HTML = '<i class="fa-solid fa-crown"></i>';
const SUSPEND_SCREEN_HTML = '<div id="suspend-screen">TEST</div>';

const $startScreen = $('#start-screen');
const $gameScreen = $('#game-screen');
const $leaderboardScreen = $('#leaderboard');

const $gameLevelSetting = $('#game-level');
const $decLevelBtn = $('#dec-level-btn');
const $incLevelBtn = $('#inc-level-btn');
const $playBtn = $('#play-btn');
const $pauseBtn = $('#pause-btn');
const $restartBtn = $('#restart-btn');
const $homeBtn = $('#home-btn');
const $leaderboardBtn = $('#leaderboard-btn');
const $clickActionToggle = $('#click-action-toggle');
const $gameBoard = $('#game-board');
const $timerDisplay = $('#game-timer-display');
const $mineCountDisplay = $('#mine-count-display');

const $toastContainer = $('.toast-container');

let levelIndex = 0;
let game;


/** Create game board */
function generateBoardHtml(rows, cols) {
  $gameBoard.empty();
  $gameBoard.css("grid-template-columns", `repeat(${cols}, 1fr)`);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      $gameBoard.append(`<div class='game-cell' id='${Cell.getCellId(row, col)}'></div>`);
    }
  }

  $gameBoard.append(SUSPEND_SCREEN_HTML);
  $('#suspend-screen').hide();
}


/** Show game suspend screen */
function showSuspendScreen(content) {
  const $suspendScreen = $('#suspend-screen');
  $suspendScreen.html(content)
  $('#suspend-screen').show();
}


/** Update level buttons depending on current difficulty */
function updateLevelButtons() {
  $decLevelBtn.removeClass('visibility-hidden');
  $incLevelBtn.removeClass('visibility-hidden');

  if (levelIndex === 0) {
    $decLevelBtn.addClass('visibility-hidden');
  } else if (levelIndex === Object.keys(DIFFICULTY_LEVELS).length - 1) {
    $incLevelBtn.addClass('visibility-hidden');
  }
}


/** Load default game difficulty */
function loadDefaultDifficulty() {
  $gameLevelSetting.html(DEFAULT_DIFFICULTY);
  updateLevelButtons();
}


/** Grab game level setting */
function getGameConfigs() {
  const gameLevel = $gameLevelSetting.html();

  return {
    rows: DIFFICULTY_LEVELS[gameLevel].rows,
    cols: DIFFICULTY_LEVELS[gameLevel].cols,
    mines: DIFFICULTY_LEVELS[gameLevel].mines
  };
}


/** Create HTML board and data board in game class */
function createBoard() {
  const { rows, cols, mines } = getGameConfigs();
  generateBoardHtml(rows, cols);
  game = new Game(rows, cols, mines);
}


/** Clear timer from previous game */
function resetPrevGame() {
  if (game) {
    game.stopTimer();
    game = null;
  }
}


/** Start minesweeper game */
function startGame(evt) {
  console.debug('startGame', evt);

  resetPrevGame();

  createBoard();
  updateClickAction();

  $pauseBtn.html(PAUSE_ICON_HTML);

  updateTimerDisplay(0);
  updateMineCount(game.mines);

  $gameScreen.show();
  $startScreen.hide();
}


/** Reveal cell and show either its value or a bomb icon */
function revealCellHtml(cell) {
  const cellHtml = (cell.status.mine) ? BOMB_ICON_HTML : cell.val || '';
  cell.$cell.html(cellHtml);
  cell.$cell.addClass('revealed');

  if (cell.status.mine) {
    cell.$cell.addClass('mine');
  } else {
    cell.$cell.attr('data-value', cell.val);
  }
}


/** Update flag icon on a cell */
function updateCellFlag(cell) {
  const cellHtml = (cell.status.flag) ? FLAG_ICON_HTML : '';
  cell.$cell.html(cellHtml);
  cell.$cell.toggleClass('flagged');
}


/** Update timer display */
function updateTimerDisplay(timeInSeconds) {
  $timerDisplay.html(convertSecondsForDisplay(timeInSeconds));
}


/** Update mine count display */
function updateMineCount(numMinesLeft) {
  $mineCountDisplay.html(numMinesLeft.toString().padStart(2, '0'));
}


/** Event handler for cell click */
function handleClick(evt) {
  console.debug('handleClick', evt);
  const $clickedCell = $(evt.target).closest('.game-cell');
  const clickedCellId = $clickedCell.attr('id');
  const clickedCell = game.cells[clickedCellId];

  // First click has special conditions
  if (game.firstClick) {
    game.handleFirstClick(clickedCell);
    return;
  }

  if (clickedCell.status.revealed) {
    game.revealNeighbourCells(clickedCell);
    return;
  }

  if (game.clickAction === 'reveal') {
    game.revealCells(clickedCell);
  }
  else {
    game.toggleFlag(clickedCell);
  }
}


/** Event handler for cell right click */
function handleRightClick(evt) {
  console.debug('handleRightClick', evt);
  evt.preventDefault();

  if (game.firstClick) {
    return;
  }

  const $clickedCell = $(evt.target).closest('.game-cell');
  const clickedCellId = $clickedCell.attr('id');

  game.toggleFlag(game.cells[clickedCellId]);
}


/** Update action to perform when user clicks based on setting */
function updateClickAction(evt) {
  console.debug('updateClickAction', evt);
  if ($clickActionToggle.hasClass('flag-mode')) {
    game.clickAction = 'flag';
  } else {
    game.clickAction = 'reveal';
  }
}


/** Toggle setting for click action */
function toggleClickAction(evt) {
  console.debug('toggleClickAction', evt);

  if (evt.key === 'f' || evt.type === 'click') {
    $clickActionToggle.toggleClass('flag-mode');
    updateClickAction(evt);
  }
}


/** Decrease game difficulty level */
function decreaseLevel(evt) {
  console.debug('decreaseLevel', evt);
  levelIndex = Math.max(0, levelIndex - 1);
  $gameLevelSetting.html(Object.keys(DIFFICULTY_LEVELS)[levelIndex]);
  updateLevelButtons();
}


/** Increase game difficulty level */
function increaseLevel(evt) {
  console.debug('increaseLevel', evt);
  levelIndex = Math.min(levelIndex + 1, Object.keys(DIFFICULTY_LEVELS).length - 1);
  $gameLevelSetting.html(Object.keys(DIFFICULTY_LEVELS)[levelIndex]);
  updateLevelButtons();
}


/** Pause game */
function pauseGame(evt) {
  if (game.gameOver || !game.gameStarted) {
    return;
  }

  if (game.scoreTimerId) {
    $pauseBtn.html(PLAY_ICON_HTML);
    game.stopTimer();
    showSuspendScreen('PAUSED');
  } else {
    $pauseBtn.html(PAUSE_ICON_HTML);
    game.startTimer();
    $('#suspend-screen').hide();
  }
}


/** Return to home screen */
function goHome(evt) {
  game.stopTimer();
  game = null;
  $startScreen.show();
  $gameScreen.hide();
}


/** Convert input in seconds to MM:SS format */
function convertSecondsForDisplay(timeInSeconds) {
  const minutes = Math.floor(timeInSeconds / 60);
  const seconds = timeInSeconds % 60;
  const minutesDisplay = minutes.toString().padStart(2, '0');
  const secondsDisplay = seconds.toString().padStart(2, '0');

  return `${minutesDisplay}:${secondsDisplay}`;
}


/** Convert UTC date string to YYYY/MM/DD format */
function convertUTCToYYYYMMDD(dateInUTC) {
  const date = new Date(dateInUTC);
  return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
}


/** Display achievement in toast container */
function displayAchievement(achievement) {
  $toastContainer.append(
    `<div class="toast align-items-center text-light bg-dark border-0" data-bs-animation='true' data-bs-delay="10000" data-bs-autohide="true" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <span>Achievement Unlocked:<span>
          <p class='mt-2 mb-0 pb-0'>
            <i class="fa-solid fa-medal" style="color:${achievement.color}"></i>
            <b>${achievement.title}</b>: ${achievement.description}
          </p>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>`
  )
}


/** Initialize and show all toasts */
function initializeAndShowToasts() {
  $('.toast').toast();
  $('.toast').toast('show');
}


/** Creates markup for entry on game leaderboard */
function generateLeaderboardListItem(score, rank) {
  let $listItem = $('<li>');
  if (score) {
    // Left side of list item
    const $leftDiv = $('<div>');
    const $userLink = $('<a>');

    $leftDiv.addClass('leaderboard-left-div');
    $userLink.attr('href', `/users/${score.user_id}`);
    $userLink.html(score.user_display_name);

    $leftDiv.append($userLink);
    if (rank < 3) $leftDiv.append(CROWN_ICON_HTML);

    // Right side of list item
    const $rightDiv = $('<div>');
    const $timeDiv = $('<div>');
    const $dateDiv = $('<div>');

    $rightDiv.addClass('leaderboard-right-div');
    $timeDiv.html(convertSecondsForDisplay(score.time));
    $timeDiv.addClass('leaderboard-time-div');
    $dateDiv.html(convertUTCToYYYYMMDD(score.submitted_at));
    $dateDiv.addClass('leaderboard-date-div');

    $rightDiv.append($timeDiv);
    $rightDiv.append($dateDiv);

    $listItem.append($leftDiv);
    $listItem.append($rightDiv);
  }
  return $listItem;
}


/** Get scores to display on leaderboard */
async function fillLeaderboard() {
  const response = await axios.get(
    `${DAVIDS_GAMES_BASE_API_URL}/api/minesweeper/scores`
  );

  const scores = response.data.scores;

  for (let level in scores) {
    $(`#${level}-scores`).empty();
    for (let i = 0; i < NUM_SCORES_ON_LEADERBOARD; i++) {
      $(`#${level}-scores`).append(
        generateLeaderboardListItem(scores[level][i], i)
      );
    }
  }
}


/** Show and hide leaderboard */
function toggleLeaderboard(evt) {
  if ($leaderboardScreen.is(':hidden')) {
    fillLeaderboard();
    $leaderboardScreen.show();
  } else {
    $leaderboardScreen.hide();
  }
}

loadDefaultDifficulty();
$gameScreen.hide();
$leaderboardScreen.hide();
$decLevelBtn.on('click', decreaseLevel);
$incLevelBtn.on('click', increaseLevel);
$playBtn.on('click', startGame);
$pauseBtn.on('click', pauseGame);
$restartBtn.on('click', startGame);
$homeBtn.on('click', goHome);
$gameBoard.on('click', '.game-cell', handleClick);
$gameBoard.on('contextmenu', '.game-cell', handleRightClick);
$clickActionToggle.on('click', toggleClickAction);
$(document).on('keydown', toggleClickAction);
$leaderboardBtn.on('click', toggleLeaderboard);