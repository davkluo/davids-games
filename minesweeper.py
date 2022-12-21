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

def calc_minesweeper_achievements(user, last_game_stats):
    """ Calculate new achievements given stats for a user """

    user_achievements = user.minesweeper_achievements
    user_stats = MinesweeperStat.query.get(user.id)
    new_achievements = []

    new_achievements.extend(
        calc_speed_achievements(user_achievements, last_game_stats)
    )

    new_achievements.extend(
        calc_time_achievements(user_achievements, user_stats)
    )

    new_achievements.extend(
        calc_win_achievements(user_achievements, user_stats)
    )

    new_achievements.extend(
        calc_streak_achievements(user_achievements, user_stats)
    )

    new_achievements.extend(
        calc_loss_achievements(user_achievements, user_stats)
    )

    new_achievements.extend(
        calc_play_achievements(user_achievements, user_stats)
    )

    return new_achievements


def calc_speed_achievements(user_achievements, last_game_stats):
    """ Calculate speed-related achievements """

    new_achievements = []

    # Speedy Beginner achievement
    if (last_game_stats['beginner_games_won']
        and last_game_stats['time_played'] <= 20):
        speed_beginner = MinesweeperAchievement.query.filter_by(
            title = 'Speedy Beginner'
        ).one()

        if speed_beginner not in user_achievements:
            new_achievements.append(speed_beginner)

    # Speedy Intermediate achievement
    if (last_game_stats['intermediate_games_won']
        and last_game_stats['time_played'] <= 80):
        speed_intermediate = MinesweeperAchievement.query.filter_by(
            title = 'Speedy Intermediate'
        ).one()

        if speed_intermediate not in user_achievements:
            new_achievements.append(speed_intermediate)

    # Speedy Expert achievement
    if (last_game_stats['expert_games_won']
        and last_game_stats['time_played'] <= 200):
        speed_expert = MinesweeperAchievement.query.filter_by(
            title = 'Speedy Expert'
        ).one()

        if speed_expert not in user_achievements:
            new_achievements.append(speed_expert)

    # Master Oogway achievement
    if (last_game_stats['games_won']
        and last_game_stats['time_played'] >= 600):
        speed_slow = MinesweeperAchievement.query.filter_by(
            title = 'Master Oogway'
        ).one()

        if speed_slow not in user_achievements:
            new_achievements.append(speed_slow)

    return new_achievements


def calc_time_achievements(user_achievements, user_stats):
    """ Calculate time-related achievements """

    new_achievements = []

    # Addicted achievement
    if user_stats.time_played >= 3600:
        time_hour = MinesweeperAchievement.query.filter_by(
            title = 'Addicted'
        ).one()

        if time_hour not in user_achievements:
            new_achievements.append(time_hour)

    return new_achievements


def calc_win_achievements(user_achievements, user_stats):
    """ Calculate win-related achievements """

    new_achievements = []

    # Taste of Victory achievement
    if user_stats.games_won >= 1:
        win_1 = MinesweeperAchievement.query.filter_by(
            title = 'Taste of Victory'
        ).one()

        if win_1 not in user_achievements:
            new_achievements.append(win_1)

    # Love to Win achievement
    if user_stats.games_won >= 50:
        win_50 = MinesweeperAchievement.query.filter_by(
            title = 'Love to Win'
        ).one()

        if win_50 not in user_achievements:
            new_achievements.append(win_50)

    # First Steps achievement
    if user_stats.beginner_games_won >= 1:
        win_1_beginner = MinesweeperAchievement.query.filter_by(
            title = 'First Steps'
        ).one()

        if win_1_beginner not in user_achievements:
            new_achievements.append(win_1_beginner)

    # Solid Progress achievement
    if user_stats.beginner_games_won >= 5:
        win_5_beginner = MinesweeperAchievement.query.filter_by(
            title = 'Solid Progress'
        ).one()

        if win_5_beginner not in user_achievements:
            new_achievements.append(win_5_beginner)

    # Permanent Baby achievement
    if user_stats.beginner_games_won >= 20:
        win_20_beginner = MinesweeperAchievement.query.filter_by(
            title = 'Permanent Baby'
        ).one()

        if win_20_beginner not in user_achievements:
            new_achievements.append(win_20_beginner)

    # Mildly Average achievement
    if user_stats.intermediate_games_won >= 1:
        win_1_intermediate = MinesweeperAchievement.query.filter_by(
            title = 'Mildly Average'
        ).one()

        if win_1_intermediate not in user_achievements:
            new_achievements.append(win_1_intermediate)

    # Moderately Average achievement
    if user_stats.intermediate_games_won >= 5:
        win_5_intermediate = MinesweeperAchievement.query.filter_by(
            title = 'Moderately Average'
        ).one()

        if win_5_intermediate not in user_achievements:
            new_achievements.append(win_5_intermediate)

    # Fully Average achievement
    if user_stats.intermediate_games_won >= 20:
        win_20_intermediate = MinesweeperAchievement.query.filter_by(
            title = 'Fully Average'
        ).one()

        if win_20_intermediate not in user_achievements:
            new_achievements.append(win_20_intermediate)

    # Pure Luck achievement
    if user_stats.expert_games_won >= 1:
        win_1_expert = MinesweeperAchievement.query.filter_by(
            title = 'Pure Luck'
        ).one()

        if win_1_expert not in user_achievements:
            new_achievements.append(win_1_expert)

    # Pure Skill achievement
    if user_stats.expert_games_won >= 5:
        win_5_expert = MinesweeperAchievement.query.filter_by(
            title = 'Pure Skill'
        ).one()

        if win_5_expert not in user_achievements:
            new_achievements.append(win_5_expert)

    # Nerd achievement
    if user_stats.expert_games_won >= 20:
        win_20_expert = MinesweeperAchievement.query.filter_by(
            title = 'Nerd'
        ).one()

        if win_20_expert not in user_achievements:
            new_achievements.append(win_20_expert)

    return new_achievements


def calc_streak_achievements(user_achievements, user_stats):
    """ Calculate streak-related achievements """

    new_achievements = []

    # On A Roll
    if user_stats.win_streak >= 5:
        streak_5 = MinesweeperAchievement.query.filter_by(
            title = 'On A Roll'
        ).one()

        if streak_5 not in user_achievements:
            new_achievements.append(streak_5)

    # Unstoppable
    if user_stats.win_streak >= 10:
        streak_10 = MinesweeperAchievement.query.filter_by(
            title = 'Unstoppable'
        ).one()

        if streak_10 not in user_achievements:
            new_achievements.append(streak_10)

    return new_achievements


def calc_loss_achievements(user_achievements, user_stats):
    """ Calculate loss-related achievements """

    new_achievements = []

    # Just A Blip achievement
    if (user_stats.games_played - user_stats.games_won) >= 1:
        loss_1 = MinesweeperAchievement.query.filter_by(
            title = 'Just A Blip'
        ).one()

        if loss_1 not in user_achievements:
            new_achievements.append(loss_1)

    # Wounded Ego achievement
    if (user_stats.games_played - user_stats.games_won) >= 50:
        loss_50 = MinesweeperAchievement.query.filter_by(
            title = 'Wounded Ego'
        ).one()

        if loss_50 not in user_achievements:
            new_achievements.append(loss_50)

    return new_achievements


def calc_play_achievements(user_achievements, user_stats):
    """ Calculate play-related achievements """

    new_achievements = []

    # Welcome to Minesweeper achievement
    if user_stats.games_played >= 1:
        play_1 = MinesweeperAchievement.query.filter_by(
            title = 'Welcome to Minesweeper'
        ).one()

        if play_1 not in user_achievements:
            new_achievements.append(play_1)

    # Still Here? achievement
    if user_stats.games_played >= 50:
        play_50 = MinesweeperAchievement.query.filter_by(
            title = 'Still Here?'
        ).one()

        if play_50 not in user_achievements:
            new_achievements.append(play_50)

    # YOU are the Minesweeper achievement
    if user_stats.games_played >= 100:
        play_100 = MinesweeperAchievement.query.filter_by(
            title = 'YOU are the Minesweeper'
        ).one()

        if play_100 not in user_achievements:
            new_achievements.append(play_100)

    return new_achievements