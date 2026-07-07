from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, replace
from statistics import mean
from typing import Optional

from roll_galaxy.model import PHASE_ORDER, Phase, Tile, TileKind

from .engine import PhaseBatteryConfig, PhaseBatteryGame


SOLO_ROUNDS = 15
SOLO_VP_POOL_PER_SEAT = 12
SOLO_VP_POOL_SEATS = 2


@dataclass
class DummyState:
    claimed_tiles: list[Tile]
    goods: int = 0
    shipped_goods: int = 0


@dataclass(frozen=True)
class SoloRoundReport:
    round_number: int
    player_phases: tuple[Phase, ...]
    dummy_phases: tuple[Phase, ...]
    selected_phases: tuple[Phase, ...]
    score: int
    tableau: int
    dummy_claimed_tiles: int
    dummy_goods: int


class PhaseBatterySoloGame:
    def __init__(
        self,
        strategy: str = "balanced",
        seed: Optional[int] = None,
        config: Optional[PhaseBatteryConfig] = None,
        dummy_count: int = 2,
    ):
        self.dummy_count = dummy_count
        base_config = config or PhaseBatteryConfig()
        solo_config = replace(
            base_config,
            max_rounds=SOLO_ROUNDS,
            vp_pool_per_player=base_config.vp_pool_per_player
            if config is not None and base_config.vp_pool_per_player is not None
            else SOLO_VP_POOL_PER_SEAT * SOLO_VP_POOL_SEATS,
        )
        self.game = PhaseBatteryGame([("You", strategy)], seed=seed, config=solo_config)
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
        before_pips = self.player.used_pips
        before_completed = self.player.completed_tiles

        player_phases = self.game.choose_phases(self.player, 2)
        dummy_phases = self.draw_dummy_phases()
        phase_set = set(dummy_phases)
        phase_set.update(player_phases)
        selected_phases = tuple(phase for phase in PHASE_ORDER if phase in phase_set)

        for phase in selected_phases:
            self.game.resolve_phase(self.player, phase)
            if phase in dummy_phases:
                self.resolve_dummy_phase(phase)
        if self.player.used_pips == before_pips and self.player.completed_tiles == before_completed:
            self.player.dead_rounds += 1

        self.game.manage_empire(self.player)

        return SoloRoundReport(
            self.game.round_number,
            player_phases,
            dummy_phases,
            selected_phases,
            self.game.score(self.player),
            len(self.player.tableau),
            len(self.dummy.claimed_tiles),
            self.dummy.goods,
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
            self.dummy.shipped_goods += self.dummy.goods
            self.dummy.goods = 0
            return
        raise ValueError(f"unknown phase: {phase}")

    def claim_dummy_tile(self, kind: TileKind) -> Optional[Tile]:
        for index, tile in enumerate(self.game.tile_bag):
            if tile.kind is kind:
                self.dummy.claimed_tiles.append(tile)
                del self.game.tile_bag[index]
                return tile
        return None

    def game_over(self) -> bool:
        if self.game.round_number >= self.game.config.max_rounds:
            return True
        return len(self.player.tableau) >= self.game.config.target_tableau_squares

    def end_reason(self) -> str:
        if len(self.player.tableau) >= self.game.config.target_tableau_squares:
            return "tableau"
        if self.game.round_number >= self.game.config.max_rounds:
            return "round_limit"
        return "in_progress"

    def summary(self):
        summary = self.game.player_summary(self.player)
        summary["score"] = self.game.score(self.player)
        summary["dummy_claimed_tiles"] = len(self.dummy.claimed_tiles)
        summary["dummy_goods"] = self.dummy.goods
        summary["dummy_shipped_goods"] = self.dummy.shipped_goods
        summary["end_reason"] = self.end_reason()
        return summary

    def final_scores(self):
        return [("You", self.game.score(self.player), self.summary())]


def run_one(strategy: str, seed: int, config: PhaseBatteryConfig, dummy_count: int):
    game = PhaseBatterySoloGame(strategy=strategy, seed=seed, config=config, dummy_count=dummy_count)
    scores, reports = game.play()
    return game, scores, reports


def main():
    parser = argparse.ArgumentParser(description="Run the main Roll Phase Battery solo prototype.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--strategy", default="balanced")
    parser.add_argument("--dummy-count", type=int, default=2)
    parser.add_argument("--max-track-capacity", type=int, default=6)
    parser.add_argument("--starting-capacity", type=int, default=3)
    parser.add_argument("--starting-credits", type=int, default=1)
    parser.add_argument("--free-recharge", type=int, default=0)
    parser.add_argument("--yellow-mode", choices=("ship", "alien"), default="alien")
    parser.add_argument("--construction-limit", type=int, default=3)
    parser.add_argument("--red-grants-max-only", action="store_true")
    args = parser.parse_args()

    config = PhaseBatteryConfig(
        starting_capacity=args.starting_capacity,
        starting_credits=args.starting_credits,
        max_track_capacity=args.max_track_capacity,
        minimum_recharge=args.free_recharge,
        yellow_mode=args.yellow_mode,
        construction_limit=args.construction_limit,
        red_grants_current=not args.red_grants_max_only,
    )

    scores = []
    rounds = []
    tableau = []
    completed = []
    dummy_claims = []
    dummy_shipments = []
    end_reasons = Counter()
    last_scores = None
    last_reports = None

    for index in range(args.games):
        game, final_scores, reports = run_one(args.strategy, args.seed + index, config, args.dummy_count)
        summary = final_scores[0][2]
        scores.append(final_scores[0][1])
        rounds.append(summary["rounds"])
        tableau.append(summary["tableau"])
        completed.append(summary["completed_tiles"])
        dummy_claims.append(summary["dummy_claimed_tiles"])
        dummy_shipments.append(summary["dummy_shipped_goods"])
        end_reasons[summary["end_reason"]] += 1
        last_scores = final_scores
        last_reports = reports

    print(f"Games: {args.games}")
    print(f"Strategy: {args.strategy}")
    print(f"Dummy phase cards: {args.dummy_count}")
    print(f"Round cap: {SOLO_ROUNDS}")
    print(f"Construction limit: {config.construction_limit}")
    print(f"Starting credits: {config.starting_credits}")
    print(f"VP pool: {config.vp_pool_per_player or SOLO_VP_POOL_PER_SEAT * SOLO_VP_POOL_SEATS}")
    print("Credits: unlimited chips")
    print(f"Red grants current: {config.red_grants_current}")
    print(f"Average rounds: {mean(rounds):.1f}")
    print(f"Average score: {mean(scores):.1f}")
    print(f"Average tableau/completed: {mean(tableau):.1f}/{mean(completed):.1f}")
    print("Scoring: tableau VP + VP chips + 6-cost bonuses")
    print(f"Average dummy churn: {mean(dummy_claims):.1f} tiles, {mean(dummy_shipments):.1f} shipped goods")
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
        dummy = [phase.value for phase in report.dummy_phases]
        selected = [phase.value for phase in report.selected_phases]
        player_phases = [phase.value for phase in report.player_phases]
        print(
            f"  R{report.round_number}: player {player_phases}, dummy {dummy}, selected {selected}, score {report.score}, "
            f"tableau {report.tableau}, dummy goods {report.dummy_goods}"
        )


if __name__ == "__main__":
    main()
