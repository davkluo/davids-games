from models import (
    User, MinesweeperAchievement, UserMinesweeperAchievement, MinesweeperStat
)

MINESWEEPER_LEVELS = {
    'beginner': {
        'rows': 9,
        'cols': 9,
        'mines': 10
    },
    'intermediate': {
        'rows': 16,
        'cols': 16,
        'mines': 40
    },
    'expert': {
        'rows': 16,
        'cols': 30,
        'mines': 99
    }
}

def calc_minesweeper_achievements(stats, last_game_stats):
    """ Calculate new achievements given stats for a user """

    return

def calc_time_achievements(last_game_stats):
    """ Calculate time-related achievements """
    return

"""
Achievements:

Win 1, 5, 20 times on beginner ('First Steps', 'Solid Progress', 'Switch It Up, Will Ya?')
Win 1, 5, 20 times on intermediate ('Mildly Average', 'Moderately Average', 'Fully Average')
Win 1, 5, 20 times on expert ('I Bet It Was Luck', 'Nah, It Was Skill', 'Nerd')
Win 1, 50 times ('Taste of Victory', 'Yeah, I Like To Win')
Lose 1, 50 times ('Tis But A Scratch', 'Wounded Ego')
Play 1, 50, 100 times ('Welcome', 'Still Here?', 'You Are The Minesweeper')
Beat beginner in < 20s ('Speedy Beginner')
Beat intermediate in < 80s ('Speedy Intermediate')
Beat expert in < 200s ('Speedy Expert')
Take > 600s ('Slow & Steady')
Play for total of > 3600s ('Obsessed')
Win Streak 5, 10 ('On A Roll', 'Unstoppable')
"""