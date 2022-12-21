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

const BOMB_ICON_HTML = '<i class="fa-solid fa-bomb"></i>';
const FLAG_ICON_HTML = '<i class="fa-solid fa-flag"></i>';

const $startScreen = $('#start-screen');
const $gameLevelSetting = $('#game-level');
const $decLevelBtn = $('#dec-level-btn');
const $incLevelBtn = $('#inc-level-btn');
const $playBtn = $('#play-btn');
const $clickActionSwitch = $('#click-action-switch');
const $clickActionSwitchLabel = $('#click-action-switch-label');
const $gameBoard = $('#game-board');
const $timerDisplay = $('#game-timer');

let levelIndex = 0;
let game;

function generateBoardHtml(rows, cols) {
  $gameBoard.empty();
  $gameBoard.css("grid-template-columns", `repeat(${cols}, 1fr)`);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      $gameBoard.append(`<div class='game-cell' id='${Cell.getCellId(row, col)}'></div>`);
    }
  }
}

function updateLevelButtons() {
  $decLevelBtn.removeClass('visibility-hidden');
  $incLevelBtn.removeClass('visibility-hidden');

  if (levelIndex === 0) {
    $decLevelBtn.addClass('visibility-hidden');
  } else if (levelIndex === Object.keys(DIFFICULTY_LEVELS).length - 1) {
    $incLevelBtn.addClass('visibility-hidden');
  }
}

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

function startGame(evt) {
  console.debug('startGame', evt);

  if (game) {
    game.stopTimer();
    game = null;
    updateTimerDisplay(0);
  }

  createBoard();
  updateClickAction();
  $clickActionSwitch.on('change', updateClickAction);
  $(document).on('keydown', toggleClickAction);

  $startScreen.hide();
}

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

function updateCellFlag(cell) {
  const cellHtml = (cell.status.flag) ? FLAG_ICON_HTML : '';
  cell.$cell.html(cellHtml);
  cell.$cell.toggleClass('flagged');
}

function updateTimerDisplay(timeInSeconds) {
  const minutes = Math.floor(timeInSeconds / 60);
  const seconds = timeInSeconds % 60;
  const minutesDisplay = minutes.toString().padStart(2, '0');
  const secondsDisplay = seconds.toString().padStart(2, '0');
  $timerDisplay.html(`${minutesDisplay}:${secondsDisplay}`);
}

function handleClick(evt) {
  console.debug('handleClick', evt);
  const $clickedCell = ($(evt.target).hasClass('game-cell'))
    ? $(evt.target)
    : $(evt.target).closest('.game-cell');
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

function handleRightClick(evt) {
  console.debug('handleRightClick', evt);
  evt.preventDefault();

  if (game.firstClick) {
    return;
  }

  const $clickedCell = ($(evt.target).hasClass('game-cell'))
    ? $(evt.target)
    : $(evt.target).closest('.game-cell');
  const clickedCellId = $clickedCell.attr('id');

  game.toggleFlag(game.cells[clickedCellId]);
}

function updateClickAction(evt) {
  console.debug('updateClickAction', evt);
  if ($clickActionSwitch.prop('checked')) {
    game.clickAction = 'flag';
    $clickActionSwitchLabel.html('Flag Cells');
  } else {
    game.clickAction = 'reveal';
    $clickActionSwitchLabel.html('Reveal Cells');
  }
}

function toggleClickAction(evt) {
  console.debug('toggleClickAction', evt);
  if (evt.key === 'f') {
    $clickActionSwitch.prop('checked', !$clickActionSwitch.prop('checked'));
    updateClickAction(evt);
  }
}

function decreaseLevel(evt) {
  console.debug('decreaseLevel', evt);
  levelIndex = Math.max(0, levelIndex - 1);
  $gameLevelSetting.html(Object.keys(DIFFICULTY_LEVELS)[levelIndex]);
  updateLevelButtons();
}

function increaseLevel(evt) {
  console.debug('increaseLevel', evt);
  levelIndex = Math.min(levelIndex + 1, Object.keys(DIFFICULTY_LEVELS).length - 1);
  $gameLevelSetting.html(Object.keys(DIFFICULTY_LEVELS)[levelIndex]);
  updateLevelButtons();
}

//call function to set default values for rows/cols/mines
loadDefaultDifficulty();
$decLevelBtn.on('click', decreaseLevel);
$incLevelBtn.on('click', increaseLevel);
$playBtn.on('click', startGame);
$gameBoard.on('click', '.game-cell', handleClick);
$gameBoard.on('contextmenu', '.game-cell', handleRightClick);



/*

GAME PLAN

Minesweeper game with the following features:
Color theme selector
Difficulty selection/custom size input
Timer for recording high score
Show number of safe cells and mine cells left
Start/pause game/new game
Tips/tutorial?
Save custom board size in localstorage
Can use a radio button group for the reveal/flag click

DONE- Choose default click to be reveal, flag
DONE- Right click for flag
DONE- Click on revealed with correct number of flags around it for auto-reveal of rest
DONE- First click always a 0, and you shouldn't be able to flag mark on first click
DONE- 0 values always propagate out to the next non-zero value
DONE- keyboard shortcuts for switching click action

Program flow:

- User chooses difficulty/size starts game
DONE- Data board is generated with mine positions and number values
DONE- HTML board is generated with correct number of cells
DONE- HTML cell is correlated with data board via its HTML id
DONE- When the first click happens, take the clicked cell and all of its neighbours
  DONE- For any mines within these cells, move them elsewhere and update their cell values
DONE- When a subsequent click happens, determine what kind of click it was based on the configs and left/right click
  DONE- Determine which cell was clicked
  DONE- If it is a mine, end the game
  DONE- If it is not a mine, reveal the cell value
    DONE- If the cell value was a 0, propagate the reveal out until it is non-zero
  DONE- If it is a revealed cell, check if there are enough flags around it

* Animations where appropriate
- HTML content populated all the time and hidden vs changing it on the go?

Styling:
- Spin button + input text design for the configurations
- Show and hide settings menu
- Play button should be a new game button instead
- Pause and resume button should be the same button


DONE- Look into refactoring some methods into Cell class
DONE- Color cells depending on the value

DONE- Reset click action on new game, or make sure its value is updated?
disable switch before first click, but still allow its configuration to be saved?
Click action switch can be switched before first click?

error handling for rows/cols/mines input
*/