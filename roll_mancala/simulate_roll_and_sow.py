from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from statistics import mean

from .roll_and_sow import RollAndSowConfig, RollAndSowGame


def parse_players(values: list[str]):
    players = []
    for index, value in enumerate(values):
        if ":" in value:
            name, strategy = value.split(":", 1)
        else:
            name, strategy = f"P{index + 1}", value
        players.append((name, strategy))
    return players


def main():
    parser = argparse.ArgumentParser(description="Test the activate-use-sow Roll mancala loop.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument(
        "--players",
        nargs="+",
        default=("P1:balanced", "P2:builder", "P3:producer", "P4:shipper"),
    )
    parser.add_argument("--max-rounds", type=int, default=30)
    parser.add_argument("--vp-pool-per-player", type=int, default=7)
    parser.add_argument("--interaction-weight", type=int, default=2)
    parser.add_argument("--no-two-player-dummy", action="store_true")
    args = parser.parse_args()

    specs = parse_players(list(args.players))
    if not 1 <= len(specs) <= 4:
        parser.error("roll-and-sow supports 1 to 4 players")
    config = RollAndSowConfig(
        max_rounds=args.max_rounds,
        vp_pool_per_player=args.vp_pool_per_player,
        interaction_weight=args.interaction_weight,
        two_player_dummy_phase=not args.no_two_player_dummy,
    )
    wins = Counter()
    phase_calls = Counter()
    phase_occurrences = Counter()
    totals = defaultdict(Counter)
    appearances = Counter()
    rounds = []
    collisions = 0
    total_rounds = 0
    end_reasons = Counter()
    last_scores = None
    last_reports = None

    for game_index in range(args.games):
        game = RollAndSowGame(specs, seed=args.seed + game_index, config=config)
        scores, reports = game.play()
        rounds.append(game.round_number)
        total_rounds += len(reports)
        wins[scores[0][2]["strategy"]] += 1
        if game.vp_pool <= 0:
            end_reasons["vp_pool"] += 1
        elif any(summary["tableau"] >= config.target_tableau_squares for _, _, summary in scores):
            end_reasons["tableau"] += 1
        else:
            end_reasons["round_limit"] += 1

        for report in reports:
            selected_calls = [phase for phase in report.selections.values() if phase is not None]
            collisions += int(len(set(selected_calls)) < len(selected_calls))
            phase_calls.update(phase.value for phase in selected_calls)
            phase_occurrences.update(phase.value for phase in report.selected)

        for _name, _score, summary in scores:
            strategy = summary["strategy"]
            appearances[strategy] += 1
            for key in (
                "score",
                "tableau",
                "completed_tiles",
                "vp_chips",
                "goods",
                "owned_dice",
                "bowl_dice",
                "citizenry_dice",
                "construction_dice",
                "used_dice",
                "sown_dice",
                "forced_sown_dice",
                "activations",
                "opponent_activations",
                "zero_use_activations",
                "dead_rounds",
                "recruited_dice",
                "recalled_dice",
                "credits_earned",
                "credits_spent",
                "shipped_goods",
                "explore_candidates_seen",
                "reassigned_dice",
                "power_credits",
                "power_vp",
                "virtual_workers",
                "goal_score",
            ):
                totals[strategy][key] += summary[key]
            totals[strategy]["goal_commits"] += int(
                summary["goal_commit_round"] is not None
            )
            totals[strategy]["committed_goal_count"] += len(
                summary["committed_goals"]
            )
            totals[strategy]["fulfilled_goals"] += sum(
                requirement["fulfilled"]
                for requirement in summary["goal_requirements"].values()
            )
        last_scores = scores
        last_reports = reports

    print(f"Games: {args.games}")
    print("Rules: select bowl -> activate/use -> sow unused dice")
    print("Opening: roll 3 white dice, 2 white dice in Citizenry")
    print("Explore: 4 candidates with first die, +1 per extra die")
    print(
        "Goals: shared pool of players + 2; commit at half VP pool or 6 completed; "
        f"miss = -{config.endgame_goal_penalty} VP"
    )
    if len(specs) == 2:
        print(f"Two-player supply die: {config.two_player_dummy_phase}")
    if len(specs) == 1:
        print(
            f"Solo phase deck: {config.solo_dummy_phase}; "
            f"VP pool {config.solo_vp_pool}; round limit {config.solo_max_rounds}"
        )
    print(f"Players: {', '.join(f'{name}:{strategy}' for name, strategy in specs)}")
    print(f"Average rounds: {mean(rounds):.1f}")
    print(f"Selection collision rounds: {collisions / max(1, total_rounds):.1%}")
    print("End reasons: " + ", ".join(f"{reason} {count}" for reason, count in end_reasons.most_common()))
    print()
    print("Wins")
    for strategy, count in wins.most_common():
        print(f"  {strategy}: {count}")
    print()
    print("Phase calls / occurrences")
    for phase, count in phase_calls.most_common():
        print(f"  {phase}: {count} calls, {phase_occurrences[phase]} rounds")
    print()
    print("Average final metrics")
    for _name, strategy in specs:
        denom = appearances[strategy]
        data = totals[strategy]
        print(
            f"  {strategy}: score {data['score'] / denom:.1f}, "
            f"tableau/completed {data['tableau'] / denom:.1f}/{data['completed_tiles'] / denom:.1f}, "
            f"dice owned/bowl/citizenry/build {data['owned_dice'] / denom:.1f}/"
            f"{data['bowl_dice'] / denom:.1f}/{data['citizenry_dice'] / denom:.1f}/"
            f"{data['construction_dice'] / denom:.1f}, "
            f"used/sown/forced {data['used_dice'] / denom:.1f}/"
            f"{data['sown_dice'] / denom:.1f}/{data['forced_sown_dice'] / denom:.1f}, "
            f"activations/opponent {data['activations'] / denom:.1f}/"
            f"{data['opponent_activations'] / denom:.1f}, "
            f"zero-use {data['zero_use_activations'] / denom:.1f}, "
            f"dead rounds {data['dead_rounds'] / denom:.2f}, "
            f"recruits/recalls {data['recruited_dice'] / denom:.1f}/"
            f"{data['recalled_dice'] / denom:.1f}, "
            f"credits earned/spent {data['credits_earned'] / denom:.1f}/"
            f"{data['credits_spent'] / denom:.1f}, "
            f"shipped {data['shipped_goods'] / denom:.1f}, "
            f"candidates {data['explore_candidates_seen'] / denom:.1f}, "
            f"powers route/credits/vp/virtual {data['reassigned_dice'] / denom:.1f}/"
            f"{data['power_credits'] / denom:.1f}/{data['power_vp'] / denom:.1f}/"
            f"{data['virtual_workers'] / denom:.1f}, "
            f"goals committed/fulfilled/VP {data['committed_goal_count'] / denom:.1f}/"
            f"{data['fulfilled_goals'] / denom:.1f}/{data['goal_score'] / denom:.1f}"
        )
    print()
    print("Last game final table")
    for name, score, summary in last_scores or ():
        print(f"  {name}: {score} VP, {summary}")
    print()
    print("Last game final rounds")
    for report in (last_reports or ())[-5:]:
        selections = {
            name: phase.value if phase is not None else None
            for name, phase in report.selections.items()
        }
        print(
            f"  R{report.round_number}: selected {[phase.value for phase in report.selected]}, "
            f"calls {selections}, used {report.used_dice}, sown {report.sown_dice}"
        )


if __name__ == "__main__":
    main()
