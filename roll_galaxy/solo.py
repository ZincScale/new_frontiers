from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, replace
from statistics import mean
from typing import Optional

from .engine import BatteryConfig, BatteryGame
from .model import PHASE_ORDER, Phase, Tile, TileKind


@dataclass(frozen=True)
class SoloWinCondition:
    name: str
    label: str
    min_score: int
    min_tableau: int = 0
    min_completed_tiles: int = 0
    min_vp_chips: int = 0
    min_max_capacity: int = 0


SOLO_WIN_CONDITIONS: tuple[SoloWinCondition, ...] = (
    SoloWinCondition("great", "Great", 37),
    SoloWinCondition("triumphant", "Triumphant", 38),
    SoloWinCondition("epic", "Epic", 41),
    SoloWinCondition("builder", "Builder", 31, min_completed_tiles=7),
    SoloWinCondition("colonizer", "Colonizer", 31, min_tableau=10),
    SoloWinCondition("satisfied_populace", "Satisfied Populace", 31, min_vp_chips=10),
    SoloWinCondition("industrial", "Industrial", 31, min_max_capacity=16),
)

SOLO_ROUNDS = 12
SOLO_VP_POOL = 30


SOLO_WIN_CONDITION_MAP: dict[str, SoloWinCondition] = {
    condition.name: condition for condition in SOLO_WIN_CONDITIONS
}


@dataclass
class DummyState:
    claimed_tiles: list[Tile]
    goods: int = 0
    vp_chips_drained: int = 0


@dataclass(frozen=True)
class SoloRoundReport:
    round_number: int
    human_phase: Phase
    dummy_phases: tuple[Phase, ...]
    selected: tuple[Phase, ...]
    used_pips: int
    human_score: int
    dummy_claimed_tiles: int
    dummy_goods: int
    vp_pool: int


class BatterySoloGame:
    def __init__(
        self,
        strategy: str = "balanced",
        seed: Optional[int] = None,
        config: Optional[BatteryConfig] = None,
        condition: str = "all",
        dummy_count: int = 2,
    ):
        self.condition_filter = condition
        self.dummy_count = dummy_count
        base_config = config or BatteryConfig()
        solo_config = replace(
            base_config,
            vp_pool_per_player=SOLO_VP_POOL,
            max_rounds=SOLO_ROUNDS,
        )
        self.game = BatteryGame([("You", strategy)], seed=seed, config=solo_config)
        self.phase_deck = list(PHASE_ORDER)
        self.game.rng.shuffle(self.phase_deck)
        self.dummy = DummyState(claimed_tiles=[])
        self.reports: list[SoloRoundReport] = []

    @property
    def player(self):
        return self.game.players[0]

    def play(self):
        while not self.game_over():
            self.reports.append(self.play_round())
        return self.final_scores(), self.reports

    def play_round(self) -> SoloRoundReport:
        self.game.round_number += 1
        human_phase = self.game.choose_phase(self.player)
        dummy_phases = self.draw_dummy_phases()
        self.player.selected_phases.append(human_phase)
        selected = tuple(phase for phase in PHASE_ORDER if phase in {human_phase, *dummy_phases})

        before = self.player.used_pips
        for phase in selected:
            self.game.resolve_phase(self.player, phase)
        used = self.player.used_pips - before
        if used == 0:
            self.player.dead_rounds += 1

        for phase in dummy_phases:
            self.resolve_dummy_phase(phase)
        self.game.manage_empire(self.player)

        return SoloRoundReport(
            self.game.round_number,
            human_phase,
            dummy_phases,
            selected,
            used,
            self.game.score(self.player),
            len(self.dummy.claimed_tiles),
            self.dummy.goods,
            self.game.vp_pool,
        )

    def draw_dummy_phases(self) -> tuple[Phase, ...]:
        if len(self.phase_deck) < min(self.dummy_count, len(PHASE_ORDER)):
            self.phase_deck = list(PHASE_ORDER)
            self.game.rng.shuffle(self.phase_deck)
        phases = []
        for _ in range(self.dummy_count):
            if not self.phase_deck:
                self.phase_deck = list(PHASE_ORDER)
                self.game.rng.shuffle(self.phase_deck)
            phases.append(self.phase_deck.pop())
        return tuple(phases)

    def resolve_dummy_phase(self, phase: Phase):
        if phase is Phase.EXPLORE:
            self.claim_dummy_tile(TileKind.DEVELOPMENT)
            self.claim_dummy_tile(TileKind.WORLD)
            return
        if phase is Phase.DEVELOP:
            self.claim_dummy_tile(TileKind.DEVELOPMENT)
            return
        if phase is Phase.SETTLE:
            self.claim_dummy_tile(TileKind.WORLD)
            return
        if phase is Phase.PRODUCE:
            self.dummy.goods = min(4, self.dummy.goods + 1)
            return
        if phase is Phase.SHIP:
            drained = max(1, self.dummy.goods) * 2
            self.dummy.goods = 0
            self.drain_vp_pool(drained)
            return
        raise ValueError(f"unknown phase: {phase}")

    def claim_dummy_tile(self, kind: TileKind) -> Optional[Tile]:
        for index, tile in enumerate(self.game.tile_bag):
            if tile.kind is kind:
                self.dummy.claimed_tiles.append(tile)
                del self.game.tile_bag[index]
                return tile
        return None

    def drain_vp_pool(self, amount: int):
        drained = min(amount, self.game.vp_pool)
        self.dummy.vp_chips_drained += drained
        self.game.vp_pool -= drained

    def game_over(self) -> bool:
        if self.game.round_number >= SOLO_ROUNDS:
            return True
        if self.game.vp_pool <= 0:
            return True
        return len(self.player.tableau) >= self.game.config.target_tableau_squares

    def end_reason(self) -> str:
        if self.game.vp_pool <= 0:
            return "vp_pool"
        if len(self.player.tableau) >= self.game.config.target_tableau_squares:
            return "human_tableau"
        if self.game.round_number >= SOLO_ROUNDS:
            return "round_limit"
        return "in_progress"

    def satisfied_conditions(self):
        summary = self.human_summary()
        return [
            condition
            for condition in self.active_conditions()
            if self.condition_success_without_summary(condition, summary)
        ]

    def active_conditions(self) -> tuple[SoloWinCondition, ...]:
        if self.condition_filter == "all":
            return SOLO_WIN_CONDITIONS
        return (SOLO_WIN_CONDITION_MAP[self.condition_filter],)

    def human_summary(self):
        summary = self.game.final_scores()[0][2]
        summary = dict(summary)
        summary["vp_chips"] = self.player.vp_chips
        summary["max_capacity"] = sum(track.maximum for track in self.player.tracks.values())
        summary["condition_filter"] = self.condition_filter
        satisfied = []
        for condition in self.active_conditions():
            success = self.condition_success_without_summary(condition, summary)
            summary[f"{condition.name}_score"] = condition.min_score
            summary[f"{condition.name}_success"] = success
            if success:
                satisfied.append(condition.name)
        summary["satisfied_conditions"] = tuple(satisfied)
        summary["condition_success"] = bool(satisfied)
        summary["dummy_claimed_tiles"] = len(self.dummy.claimed_tiles)
        summary["dummy_vp_chips_drained"] = self.dummy.vp_chips_drained
        summary["dummy_goods"] = self.dummy.goods
        summary["end_reason"] = self.end_reason()
        return summary

    def condition_success_without_summary(self, condition: SoloWinCondition, summary) -> bool:
        return (
            self.game.score(self.player) >= condition.min_score
            and summary["tableau"] >= condition.min_tableau
            and summary["completed_tiles"] >= condition.min_completed_tiles
            and summary["vp_chips"] >= condition.min_vp_chips
            and summary["max_capacity"] >= condition.min_max_capacity
        )

    def final_scores(self):
        return [("You", self.game.score(self.player), self.human_summary())]


def run_one(strategy: str, seed: int, config: BatteryConfig, condition: str, dummy_count: int):
    game = BatterySoloGame(
        strategy=strategy,
        seed=seed,
        config=config,
        condition=condition,
        dummy_count=dummy_count,
    )
    scores, reports = game.play()
    return game, scores, reports


def main():
    parser = argparse.ArgumentParser(description="Run the Roll phase-battery solo challenge prototype.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--strategy", default="balanced")
    parser.add_argument("--condition", choices=("all", *SOLO_WIN_CONDITION_MAP), default="all")
    parser.add_argument("--dummy-count", type=int, default=2)
    parser.add_argument("--max-track-capacity", type=int, default=6)
    parser.add_argument("--starting-capacity", type=int, default=2)
    parser.add_argument("--starting-white-capacity", type=int, default=2)
    parser.add_argument("--starting-credits", type=int, default=1)
    parser.add_argument("--free-recharge", type=int, default=0)
    parser.add_argument("--yellow-mode", choices=("ship", "alien"), default="alien")
    args = parser.parse_args()

    config = BatteryConfig(
        starting_capacity=args.starting_capacity,
        starting_white_capacity=args.starting_white_capacity,
        max_track_capacity=args.max_track_capacity,
        starting_credits=args.starting_credits,
        minimum_recharge=args.free_recharge,
        yellow_mode=args.yellow_mode,
    )

    conditions = Counter()
    end_reasons = Counter()
    rounds = []
    human_scores = []
    claimed_tiles = []
    drained_vp = []
    last_game = None
    last_scores = None
    last_reports = None

    for index in range(args.games):
        game, scores, reports = run_one(
            args.strategy,
            args.seed + index,
            config,
            args.condition,
            args.dummy_count,
        )
        last_game = game
        last_scores = scores
        last_reports = reports
        summary = scores[0][2]
        if summary["satisfied_conditions"]:
            for condition in summary["satisfied_conditions"]:
                conditions[condition] += 1
        else:
            conditions["loss"] += 1
        end_reasons[game.end_reason()] += 1
        rounds.append(game.game.round_number)
        human_scores.append(scores[0][1])
        claimed_tiles.append(summary["dummy_claimed_tiles"])
        drained_vp.append(summary["dummy_vp_chips_drained"])

    print(f"Games: {args.games}")
    print(f"Strategy: {args.strategy}")
    print(f"Condition filter: {args.condition}")
    print(f"Dummy phase cards: {args.dummy_count}")
    print(f"Average rounds: {mean(rounds):.1f}")
    print(f"Average score: {mean(human_scores):.1f}")
    print(f"Average dummy churn: {mean(claimed_tiles):.1f} tiles, {mean(drained_vp):.1f} VP chips")
    print("Win conditions")
    for condition in SOLO_WIN_CONDITIONS:
        if args.condition == "all" or args.condition == condition.name:
            print(f"  {condition.label}: {conditions[condition.name] / args.games:.1%}")
    print(f"  No condition: {conditions['loss'] / args.games:.1%}")
    print("End reasons")
    for reason, count in end_reasons.most_common():
        print(f"  {reason}: {count}")
    print()
    print("Last game final table")
    for name, score, summary in last_scores or []:
        print(f"  {name}: {score} VP, {summary}")
    print()
    print("Last game final rounds")
    for report in (last_reports or [])[-5:]:
        phases = [phase.value for phase in report.selected]
        dummy = [phase.value for phase in report.dummy_phases]
        print(
            f"  R{report.round_number}: you {report.human_phase.value}, "
            f"dummy {dummy}, phases {phases}, score {report.human_score}, "
            f"bag churn {report.dummy_claimed_tiles}, VP pool {report.vp_pool}"
        )
    if last_game is not None:
        print(f"VP pool remaining: {last_game.game.vp_pool}")


if __name__ == "__main__":
    main()
