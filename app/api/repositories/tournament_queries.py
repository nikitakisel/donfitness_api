def TOURNAMENT_STANDINGS_SQL(tournament_id):
    return f"""
        WITH team_results AS (
            SELECT
                home_team_id AS team_id,
                CASE
                    WHEN home_team_score > guest_team_score THEN 1
                    ELSE 0
                END AS wins,
                CASE
                    WHEN home_team_score = guest_team_score THEN 1
                    ELSE 0
                END AS draws,
                CASE
                    WHEN home_team_score < guest_team_score THEN 1
                    ELSE 0
                END AS losses,
                home_team_score AS goals_scored_in_match,
                guest_team_score AS goals_conceded_in_match
            FROM
                matches
            WHERE
                home_team_score IS NOT NULL
                AND guest_team_score IS NOT NULL
                AND tournament_id = {tournament_id}
        
            UNION ALL
        
            SELECT
                guest_team_id AS team_id,
                CASE
                    WHEN guest_team_score > home_team_score THEN 1
                    ELSE 0
                END AS wins,
                CASE
                    WHEN guest_team_score = home_team_score THEN 1
                    ELSE 0
                END AS draws,
                CASE
                    WHEN guest_team_score < home_team_score THEN 1
                    ELSE 0
                END AS losses,
                guest_team_score AS goals_scored_in_match,
                home_team_score AS goals_conceded_in_match
            FROM
                matches
            WHERE
                home_team_score IS NOT NULL
                AND guest_team_score IS NOT NULL
                AND tournament_id = {tournament_id}
        ),
        tournament_teams AS (
            SELECT
                FT.id AS team_id,
                FT.team_name
            FROM
                football_teams AS FT
            JOIN
                football_teams_to_tournaments AS FTT
                ON FT.id = FTT.football_team_id
            WHERE
                FTT.tournament_id = {tournament_id}
        )
        SELECT
            TT.team_name,
            COUNT(TR.team_id) AS matches_played,
            (3 * COALESCE(SUM(TR.wins), 0) + COALESCE(SUM(TR.draws), 0)) AS score,
            COALESCE(SUM(TR.wins), 0) AS wins,
            COALESCE(SUM(TR.draws), 0) AS draws,
            COALESCE(SUM(TR.losses), 0) AS losses,
            COALESCE(SUM(TR.goals_scored_in_match), 0) AS goals_scored,
            COALESCE(SUM(TR.goals_conceded_in_match), 0) AS goals_conceded,
            COALESCE(SUM(TR.goals_scored_in_match), 0) - COALESCE(SUM(TR.goals_conceded_in_match), 0) AS goal_difference
        FROM
            tournament_teams AS TT
        LEFT JOIN
            team_results AS TR ON TR.team_id = TT.team_id
        GROUP BY
            TT.team_name, TT.team_id
        ORDER BY
            score DESC,
            goal_difference DESC,
            goals_scored DESC,
            TT.team_name;
    """
