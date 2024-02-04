\connect davids_games

INSERT INTO roles (name)
  VALUES
    ('admin'),
    ('user')
ON CONFLICT (name) DO NOTHING;

INSERT INTO minesweeper_achievements (title, description, color)
  VALUES
    ('First Steps', 'Win 1 time on beginner difficulty.', 'rgb(169, 169, 169)'),
    ('Solid Progress', 'Win 5 times on beginner difficulty.', 'rgb(47, 79, 79)'),
    ('Permanent Baby', 'Win 20 times on beginner difficulty.', 'rgb(139, 69, 19)'),
    ('Mildly Average', 'Win 1 time on intermediate difficulty.', 'rgb(46, 139, 87)'),
    ('Moderately Average', 'Win 5 times on intermediate difficulty.', 'rgb(128, 128, 0)'),
    ('Fully Average', 'Win 20 times on intermediate difficulty.', 'rgb(72, 61, 139)'),
    ('Pure Luck', 'Win 1 time on expert difficulty.', 'rgb(0, 0, 139)'),
    ('Pure Skill', 'Win 5 times on expert difficulty.', 'rgb(255, 69, 0)'),
    ('Nerd', 'Win 20 times on expert difficulty.', 'rgb(255, 165, 0)'),
    ('Taste of Victory', 'Win 1 time.', 'rgb(64, 224, 208)'),
    ('Love to Win', 'Win 50 times.', 'rgb(0, 255, 0)'),
    ('Just A Blip', 'Lose 1 time.', 'rgb(186, 85, 211)'),
    ('Wounded Ego', 'Lose 50 times.', 'rgb(220, 20, 60)'),
    ('Welcome to Minesweeper', 'Play 1 time.', 'rgb(0, 191, 255)'),
    ('Still Here?', 'Play 50 times.', 'rgb(255, 0, 255)'),
    ('YOU are the Minesweeper', 'Play 100 times.', 'rgb(30, 144, 255)'),
    ('Speedy Beginner', 'Win on beginner difficulty in under 20 seconds.', 'rgb(219, 112, 147)'),
    ('Speedy Intermediate', 'Win on intermediate difficulty in under 80 seconds.', 'rgb(238, 232, 170)'),
    ('Speedy Expert', 'Win on expert difficulty in under 200 seconds.', 'rgb(255, 255, 84)'),
    ('Master Oogway', 'Take over 600 seconds to win a game.', 'rgb(255, 20, 147)'),
    ('Addicted', 'Accumulate over an hour of total playtime.', 'rgb(0, 0, 255)'),
    ('On A Roll', 'Win 5 times in a row.', 'rgb(255, 160, 122)'),
    ('Unstoppable', 'Win 10 times in a row.', 'rgb(152, 251, 152)')
ON CONFLICT (title) DO NOTHING;