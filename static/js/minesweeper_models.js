'use strict';

const GAME_TIMER_UPDATE_INTERVAL_MS = 50;
const MS_PER_SEC = 1000;
const MAX_GAME_TIME_S = 59 * 60 + 59;

const DAVIDS_GAMES_BASE_API_URL = 'http://localhost:5001'

/**
 * Game class for Minesweeper
 *
 * PROPERTIES
 * rows: int number of rows in board
 * cols: int number of cols in board
 * mines: int number of mines in board
 * cells: object storing (cellId: Cell instance) pairs
 * firstClick: boolean flag for first click
 * clickAction: string configuration for click action
 * numRevealed: int count of revealed cells
 * numFlagged: int count of flagged cells
 * startTime:
 * scoreTime:
 * scoreTimerId:
 *
 * METHODS
 * getValidNeighbours
 * placeMines
 * calcCellValues
 * generateBoardData
 * checkForWin
 * endGame
 * revealCells
 * toggleFlag
 * revealNeighbourCells
 * handleFirstClick
 * startTimer
 * updateTimer
 * stopTimer
 *
 */
class Game {
  constructor(rows, cols, mines) {
    this.rows = rows;
    this.cols = cols;
    this.mines = mines;
    this.cells = {};
    this.firstClick = true;
    this.clickAction = 'reveal';
    this.numRevealed = 0;
    this.numFlagged = 0;
    this.startTime = null;
    this.scoreTime = 0;
    this.scoreTimerId = null;
    this.gameOver = false;
    this.gameStarted = false;
    this.level = Object.keys(DIFFICULTY_LEVELS)[levelIndex]

    this.generateBoardData();
    this.updateTimer = this.updateTimer.bind(this);
  }


  /**
   * getValidNeighbours: Given a Cell, determine all valid neighbour Cells
   * that are on the board and return them in an array
   *
   * cell: Cell instance
   *
   * return: array of Cells
   */
  getValidNeighbours(cell) {
    const row = cell.row;
    const col = cell.col;

    return NEIGHBOUR_CELL_OFFSETS
      .map(([rowOffset, colOffset]) => [row + rowOffset, col + colOffset])
      .filter(([nRow, nCol]) => nRow >= 0 && nRow < this.rows && nCol >= 0 && nCol < this.cols)
      .map(([nRow, nCol]) => this.cells[Cell.getCellId(nRow, nCol)]);
  }


  /**
   * placeMines: Place mines randomly on the board provided the number of mines
   * and optionally an array of Cell exceptions. Cells provided in exceptions
   * will not be considered for mine placement. Returns an array of Cells where
   * the mines were placed.
   *
   * mines: int
   * exceptions: array of Cells
   *
   * return: array of Cells
   */
  placeMines(mines, ...exceptions) {
    // Store ids of exception Cells as a set for more efficient search
    const exceptionIds = new Set(exceptions.map(cell => cell.id));

    const validMineLocations =
      Cell.filterCells(Object.values(this.cells), 'mine', false)
        .filter(cell => !exceptionIds.has(cell.id));

    const mineCells = _.sampleSize(validMineLocations, mines);
    for (let cell of mineCells) {
      cell.status.mine = true;
      cell.val = null;
    }

    return mineCells;
  }


  /**
   * calcCellValues: Given a variable number of Cells, calculate for each its
   * value indicating how many mines it is surrounded by.
   *
   * cells: argument array of Cells
   */
  calcCellValues(...cells) {
    for (let cell of cells) {
      const mineNeighbours = Cell.filterCells(this.getValidNeighbours(cell), 'mine', true);
      cell.val = mineNeighbours.length;
    }
  }


  /**
   * generateBoardData: Place mines, determine cell values, and populate
   * cells with (cell id: Cell instance) pairs
   */
  generateBoardData() {
    // Create a new (cell id: Cell instance) pair in cells for each cell
    for (let row = 0; row < this.rows; row++) {
      for (let col = 0; col < this.cols; col++) {
        this.cells[Cell.getCellId(row, col)] = new Cell(row, col);
      }
    }

    // Assign mine cells on the board
    this.placeMines(this.mines);

    // Calculate cell values for all non-mine cells
    const nonMineCells = Cell.filterCells(Object.values(this.cells), 'mine', false);
    this.calcCellValues(...nonMineCells);
  }


  /**
   * checkForWin: Check for a win condition by comparing the number of revealed
   * safe cells to the total number of safe cells
   */
  checkForWin() {
    if (this.numRevealed === (this.rows * this.cols - this.mines)) {
      this.endGame(true);
    }
  }


  endGame(win) {
    this.stopTimer();
    this.gameOver = true;

    if (win) {
      this.sendScore();
      showSuspendScreen('YOU WIN!');
    } else {
      showSuspendScreen('GAME OVER');
    }

    this.sendGameStats(win);
  }


  async sendScore() {
    const scoreData = {
      time: this.scoreTime,
      level: this.level
    }

    const response = await axios.post(
      `${DAVIDS_GAMES_BASE_API_URL}/api/minesweeper/scores`,
      scoreData
    );
  }


  async sendGameStats(win) {
    const gameData = {
      games_played: 1,
      games_won: win ? 1 : 0,
      beginner_games_won: (this.level === 'beginner' && win) ? 1 : 0,
      intermediate_games_won: (this.level === 'intermediate' && win) ? 1 : 0,
      expert_games_won: (this.level === 'expert' && win) ? 1 : 0,
      time_played: this.scoreTime,
      cells_revealed: this.numRevealed,
      last_played_at: (new Date()).toUTCString()
    }

    const response = await axios.post(
      `${DAVIDS_GAMES_BASE_API_URL}/api/minesweeper/stats`,
      gameData
    );

    // Remove all previous toasts
    $('.toast').remove();

    for (let achievement of response.data.new_achievements) {
      displayAchievement(achievement);
      console.log(achievement.title, achievement.description, achievement.color);
    }

    initializeAndShowToasts();
  }

  /**
   * revealCells: Given a variable number of Cells, reveal them if they are not
   * already revealed or flagged. If the revealed cell has a value of 0,
   * automatically reveal its neighbours.
   *
   * cells: array of Cells
   */
  revealCells(...cells) {
    for (let cell of cells) {
      if (cell.status.revealed || cell.status.flag) {
        continue;
      }

      revealCellHtml(cell);
      cell.status.revealed = true;

      if (cell.status.mine) {
        this.endGame(false);
        return;
      }

      this.numRevealed++;
      if (cell.val === 0) {
        this.revealCells(...this.getValidNeighbours(cell));
      }
    }

    this.checkForWin();
  }

  /**
   * toggleFlag: Toggle the flag status of a Cell provided it is not revealed,
   * update the numFlagged counter accordingly, and call updateCellFlag to update
   * the HTML for the cell
   *
   * cell: Cell instance
   */
  toggleFlag(cell) {
    if (cell.status.revealed) {
      return;
    }

    cell.status.flag = !cell.status.flag;
    this.numFlagged = this.numFlagged + ((cell.status.flag) ? 1 : -1);
    updateCellFlag(cell);
    updateMineCount(this.mines - this.numFlagged);
  }

  /**
   * revealNeighbourCells: Given a Cell, determine if its value is equal
   * to the number of flagged neighbours for that cell. If they match,
   * reveal all neighbour cells using revealCells. revealCells will take care
   * of the logic ensuring the neighbour cells are not revealed and not flagged.
   *
   * cell: Cell instance
   */
  revealNeighbourCells(cell) {
    const flaggedNeighbours = Cell.filterCells(this.getValidNeighbours(cell), 'flag', true);

    if (cell.val === flaggedNeighbours.length) {
      this.revealCells(...this.getValidNeighbours(cell));
    }
  }

  /**
   * moveMines: Move all mines at the cell locations provided and update all
   * affected cell values.
   *
   * mineExemptCells: array of Cell instances
   */
  moveMines(...mineExemptCells) {
    const minesToMove = Cell.filterCells(mineExemptCells, 'mine', true);
    let cellsToUpdate = [...mineExemptCells];

    // Update cell and neighbours where mine was moved from
    for (let cell of minesToMove) {
      cell.status.mine = false;
      cellsToUpdate.push(cell);
      cellsToUpdate.push(...this.getValidNeighbours(cell));
    }

    // Update non-mine neighbours where mine was moved to
    const newMineLocations = this.placeMines(minesToMove.length, ...mineExemptCells);
    for (let cell of newMineLocations) {
      const nonMineNeighbours = Cell.filterCells(this.getValidNeighbours(cell), 'mine', false);
      cellsToUpdate.push(...nonMineNeighbours);
    }

    // Update cell values after mine move
    cellsToUpdate = Array.from(new Set(cellsToUpdate));
    this.calcCellValues(...cellsToUpdate);
  }

  /**
   * handleFirstClick: The first click should guarantee a cell with 0 mines around
   * it. If there are any mines in the clicked cell or its neighbouring cells,
   * moves them elsewhere and update cell values on the board as appropriate.
   *
   * cell: Cell instance
   */
  handleFirstClick(cell) {
    this.firstClick = false;
    this.moveMines(cell, ...this.getValidNeighbours(cell));
    this.revealCells(cell);
    this.gameStarted = true;
    this.startTimer();
  }

  startTimer() {
    this.startTime = Date.now() - this.scoreTime * MS_PER_SEC;
    this.scoreTimerId = setInterval(
      this.updateTimer,
      GAME_TIMER_UPDATE_INTERVAL_MS
    );
  }

  updateTimer() {
    const timeElapsed = Date.now() - this.startTime;
    const secondsElapsed = Math.floor(timeElapsed / 1000);

    // If one second has passed since the last score time
    if ((secondsElapsed - this.scoreTime) > 1) {
      this.scoreTime++;
      this.scoreTime = Math.min(this.scoreTime, MAX_GAME_TIME_S);
      updateTimerDisplay(this.scoreTime);
    }
  }

  stopTimer() {
    clearInterval(this.scoreTimerId);
    this.scoreTimerId = null;
  }
}

class Cell {
  constructor(row, col) {
    this.row = row;
    this.col = col;
    this.val = null;
    this.status = {
      mine: false,
      flag: false,
      revealed: false
    };
    this.id = Cell.getCellId(row, col);
    this.$cell = $(`#${this.id}`);
  }

  /**
   * filterCells: Filters an array of Cells based on a filterStatus and
   * boolean condition. Returns the new array of Cells.
   *
   * cells: array of Cell instances
   * filterStatus: string from the following options:
   * - 'mine' to target mine status of cells
   * - 'flag' to target flag status of cells
   * - 'revealed' to target revealed status of cells
   * condition: boolean target condition for filterStatus
   *
   * return: array of Cell instances
   */
  static filterCells(cells, filterStatus, condition) {
    return cells.filter(
      cell => cell.status[filterStatus] === condition
    );
  }

  /**
   * getCellId: Takes in the row and col indices of a cell and returns the
   * string id corresponding to that cell.
   *
   * row: int
   * col: int
   *
   * return: id string
   */
  static getCellId(row, col) {
    return `c-${row}-${col}`;
  }
}