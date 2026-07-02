from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, replace
from statistics import mean
from typing import Optional

from .engine import BatteryConfig, BatteryGame
from .model import PHASE_ORDER, Phase, Tile, TileKind


@dataclass(frozen=True)
class SoloDifficulty:
    name: str
    starting_score: int
    vp_pool: int = 30


SOLO_DIFFICULTIES: dict[str, SoloDifficulty] = {
    "training": SoloDifficulty("training", 8),
    "standard": SoloDifficulty("standard", 12),
    "advanced": SoloDifficulty("advanced", 14),
    "expert": SoloDifficulty("expert", 16),
}


@dataclass
class RivalState:
    difficulty: SoloDifficulty
    score: int
    vp_chips: int = 0
    virtual_tiles: int = 3
    goods: int = 0
    insight: int = 0


@dataclass(frozen=True)
class SoloRoundReport:
    round_number: int
    human_phase: Phase
    rival_phase: Phase
    selected: tuple[Phase, ...]
    used_pips: int
    human_score: int
    rival_score: int
    rival_virtual_tiles: int
    rival_goods: int
    rival_insight: int


class BatterySoloGame:
    def __init__(
        self,
        strategy: str = "balanced",
        seed: Optional[int] = None,
        config: Optional[BatteryConfig] = None,
        difficulty: str = "standard",
    ):
        self.difficulty = SOLO_DIFFICULTIES[difficulty]
        base_config = config or BatteryConfig()
        solo_config = replace(base_config, vp_pool_per_player=self.difficulty.vp_pool)
        self.game = BatteryGame([("You", strategy)], seed=seed, config=solo_config)
        self.rival = RivalState(self.difficulty, score=self.difficulty.starting_score)
        self.phase_deck = list(PHASE_ORDER)
        self.game.rng.shuffle(self.phase_deck)
        self.rival_claimed_tiles: list[Tile] = []
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
        rival_phase = self.draw_rival_phase()
        self.player.selected_phases.append(human_phase)
        selected = tuple(phase for phase in PHASE_ORDER if phase in {human_phase, rival_phase})

        before = self.player.used_pips
        for phase in selected:
            self.game.resolve_phase(self.player, phase)
        used = self.player.used_pips - before
        if used == 0:
            self.player.dead_rounds += 1

        self.resolve_rival_phase(rival_phase)
        self.game.manage_empire(self.player)

        return SoloRoundReport(
            self.game.round_number,
            human_phase,
            rival_phase,
            selected,
            used,
            self.game.score(self.player),
            self.rival.score,
            self.rival.virtual_tiles,
            self.rival.goods,
            self.rival.insight,
        )

    def draw_rival_phase(self) -> Phase:
        if not self.phase_deck:
            self.phase_deck = list(PHASE_ORDER)
            self.game.rng.shuffle(self.phase_deck)
        return self.phase_deck.pop()

    def resolve_rival_phase(self, phase: Phase):
        if phase is Phase.EXPLORE:
            self.rival.insight = min(3, self.rival.insight + 1)
            return
        if phase in (Phase.DEVELOP, Phase.SETTLE):
            points = 2
            kind = TileKind.DEVELOPMENT if phase is Phase.DEVELOP else TileKind.WORLD
            if self.claim_rival_tile(kind) is not None:
                self.rival.virtual_tiles += 1
            if self.rival.insight:
                points += 1
                self.rival.insight -= 1
            self.score_rival(points)
            return
        if phase is Phase.PRODUCE:
            self.rival.goods = min(4, self.rival.goods + 1)
            return
        if phase is Phase.SHIP:
            shipped = max(1, self.rival.goods)
            self.rival.goods = 0
            self.score_rival(shipped * 2)
            return
        raise ValueError(f"unknown phase: {phase}")

    def claim_rival_tile(self, kind: TileKind) -> Optional[Tile]:
        for index, tile in enumerate(self.game.tile_bag):
            if tile.kind is kind:
                self.rival_claimed_tiles.append(tile)
                del self.game.tile_bag[index]
                return tile
        return None

    def score_rival(self, points: int):
        scored = min(points, self.game.vp_pool)
        self.rival.vp_chips += scored
        self.rival.score += scored
        self.game.vp_pool -= scored

    def game_over(self) -> bool:
        if self.game.round_number >= self.game.config.max_rounds:
            return True
        if self.game.vp_pool <= 0:
            return True
        return len(self.player.tableau) >= self.game.config.target_tableau_squares

    def end_reason(self) -> str:
        if self.game.vp_pool <= 0:
            return "vp_pool"
        if len(self.player.tableau) >= self.game.config.target_tableau_squares:
            return "human_tableau"
        if self.game.round_number >= self.game.config.max_rounds:
            return "round_limit"
        return "in_progress"

    def final_scores(self):
        human_score = self.game.score(self.player)
        human_summary = self.game.final_scores()[0][2]
        rival_summary = {
            "difficulty": self.difficulty.name,
            "rounds": self.game.round_number,
            "virtual_tiles": self.rival.virtual_tiles,
            "credits": 0,
            "goods": self.rival.goods,
            "insight": self.rival.insight,
            "claimed_tiles": len(self.rival_claimed_tiles),
            "vp_chips": self.rival.vp_chips,
            "starting_score": self.difficulty.starting_score,
            "end_reason": self.end_reason(),
        }
        rows = [
            ("You", human_score, human_summary),
            ("Rival", self.rival.score, rival_summary),
        ]
        return sorted(rows, key=lambda row: row[1], reverse=True)


def run_one(strategy: str, seed: int, config: BatteryConfig, difficulty: str):
    game = BatterySoloGame(strategy=strategy, seed=seed, config=config, difficulty=difficulty)
    scores, reports = game.play()
    return game, scores, reports


def main():
    parser = argparse.ArgumentParser(description="Run the Roll phase-battery solo prototype.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--strategy", default="balanced")
    parser.add_argument("--difficulty", choices=tuple(SOLO_DIFFICULTIES), default="standard")
    parser.add_argument("--max-track-capacity", type=int, default=6)
    parser.add_argument("--starting-capacity", type=int, default=2)
    parser.add_argument("--starting-white-capacity", type=int, default=2)
    parser.add_argument("--starting-credits", type=int, default=1)
    parser.add_argument("--free-recharge", type=int, default=0)
    parser.add_argument("--yellow-mode", choices=("ship", "alien"), default="alien")
    parser.add_argument("--max-rounds", type=int, default=40)
    args = parser.parse_args()

    config = BatteryConfig(
        starting_capacity=args.starting_capacity,
        starting_white_capacity=args.starting_white_capacity,
        max_track_capacity=args.max_track_capacity,
        starting_credits=args.starting_credits,
        minimum_recharge=args.free_recharge,
        yellow_mode=args.yellow_mode,
        max_rounds=args.max_rounds,
    )

    wins = Counter()
    end_reasons = Counter()
    rounds = []
    human_scores = []
    rival_scores = []
    last_game = None
    last_scores = None
    last_reports = None

    for index in range(args.games):
        game, scores, reports = run_one(args.strategy, args.seed + index, config, args.difficulty)
        last_game = game
        last_scores = scores
        last_reports = reports
        human = next(score for name, score, _summary in scores if name == "You")
        rival = next(score for name, score, _summary in scores if name == "Rival")
        wins["human" if human > rival else "rival"] += 1
        end_reasons[game.end_reason()] += 1
        rounds.append(game.game.round_number)
        human_scores.append(human)
        rival_scores.append(rival)

    print(f"Games: {args.games}")
    print(f"Strategy: {args.strategy}")
    print(f"Difficulty: {args.difficulty}")
    print(f"Average rounds: {mean(rounds):.1f}")
    print(f"Average score: human {mean(human_scores):.1f}, rival {mean(rival_scores):.1f}")
    print(f"Win rate: human {wins['human'] / args.games:.1%}, rival {wins['rival'] / args.games:.1%}")
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
        print(
            f"  R{report.round_number}: you {report.human_phase.value}, "
            f"rival {report.rival_phase.value}, phases {phases}, "
            f"scores human {report.human_score} / rival {report.rival_score}"
        )
    if last_game is not None:
        print(f"VP pool remaining: {last_game.game.vp_pool}")


if __name__ == "__main__":
    main()
