from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, replace
from statistics import mean
from typing import Optional

from .engine import BatteryConfig, BatteryGame
from .model import PHASE_ORDER, DieColor, Phase, Tile, TileKind


@dataclass(frozen=True)
class SoloWinCondition:
    name: str
    label: str
    min_score: int
    min_tableau: int = 0
    min_completed_tiles: int = 0
    min_developments: int = 0
    min_worlds: int = 0
    min_production_worlds: int = 0
    min_distinct_world_colors: int = 0
    min_novelty_worlds: int = 0
    min_rare_worlds: int = 0
    min_alien_worlds: int = 0
    min_vp_chips: int = 0
    min_max_capacity: int = 0
    min_blue_capacity: int = 0
    min_red_capacity: int = 0


@dataclass(frozen=True)
class SoloDifficulty:
    key: str
    label: str
    great_score: int
    triumphant_score: int
    epic_score: int
    named_score: int
    industrial_capacity: int


SOLO_DIFFICULTIES: tuple[SoloDifficulty, ...] = (
    SoloDifficulty("easy", "Easy", 23, 30, 36, 24, 12),
    SoloDifficulty("normal", "Normal", 31, 36, 42, 32, 14),
    SoloDifficulty("advanced", "Advanced", 36, 42, 48, 36, 15),
    SoloDifficulty("very_hard", "Very Hard", 42, 48, 54, 40, 16),
)

SOLO_DIFFICULTY_MAP: dict[str, SoloDifficulty] = {
    difficulty.key: difficulty for difficulty in SOLO_DIFFICULTIES
}
DEFAULT_SOLO_DIFFICULTY = "normal"


def solo_win_conditions(difficulty: SoloDifficulty) -> tuple[SoloWinCondition, ...]:
    named = difficulty.named_score
    return (
        SoloWinCondition("great", "Great", difficulty.great_score),
        SoloWinCondition("triumphant", "Triumphant", difficulty.triumphant_score),
        SoloWinCondition("epic", "Epic", difficulty.epic_score),
        SoloWinCondition("builder", "Builder", named, min_completed_tiles=8),
        SoloWinCondition("developer", "Developer", named, min_developments=5),
        SoloWinCondition("colonizer", "Colonizer", named, min_worlds=6),
        SoloWinCondition("satisfied_populace", "Satisfied Populace", named, min_vp_chips=11),
        SoloWinCondition("industrial", "Industrial", named, min_max_capacity=difficulty.industrial_capacity),
        SoloWinCondition("production", "Production", named, min_production_worlds=4),
        SoloWinCondition("diverse", "Diverse", named, min_distinct_world_colors=4),
        SoloWinCondition("novelty", "Novelty", named, min_novelty_worlds=2),
        SoloWinCondition("rare", "Rare Elements", named, min_rare_worlds=2),
        SoloWinCondition("alien", "Alien Contact", named, min_alien_worlds=1),
        SoloWinCondition("military", "Military", named, min_red_capacity=4),
        SoloWinCondition("discovery", "Discovery", named, min_blue_capacity=4),
    )


SOLO_WIN_CONDITIONS: tuple[SoloWinCondition, ...] = solo_win_conditions(
    SOLO_DIFFICULTY_MAP[DEFAULT_SOLO_DIFFICULTY]
)

SOLO_ROUNDS = 12
SOLO_VP_POOL = 30


SOLO_WIN_CONDITION_MAP: dict[str, SoloWinCondition] = {
    condition.name: condition for condition in SOLO_WIN_CONDITIONS
}


@dataclass(frozen=True)
class SoloCampaign:
    key: str
    label: str
    condition_names: tuple[str, ...]

    @property
    def conditions(self) -> tuple[SoloWinCondition, ...]:
        return tuple(SOLO_WIN_CONDITION_MAP[name] for name in self.condition_names)


SOLO_CAMPAIGNS: tuple[SoloCampaign, ...] = (
    SoloCampaign("outreach", "Outreach", ("great", "colonizer", "builder", "industrial")),
    SoloCampaign("industry", "Industrial Base", ("triumphant", "developer", "industrial", "production")),
    SoloCampaign("survey", "Sector Survey", ("triumphant", "diverse", "novelty", "rare")),
    SoloCampaign("contact", "Alien Contact", ("triumphant", "alien", "diverse", "discovery")),
    SoloCampaign("mastery", "Mastery", ("epic", "novelty", "rare", "military")),
)

SOLO_CAMPAIGN_MAP: dict[str, SoloCampaign] = {campaign.key: campaign for campaign in SOLO_CAMPAIGNS}


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
        campaign: Optional[str] = None,
        dummy_count: int = 2,
        difficulty: str = DEFAULT_SOLO_DIFFICULTY,
    ):
        self.condition_filter = condition
        self.difficulty = SOLO_DIFFICULTY_MAP[difficulty]
        self.condition_map = {
            condition.name: condition for condition in solo_win_conditions(self.difficulty)
        }
        self.campaign = SOLO_CAMPAIGN_MAP[campaign] if campaign else None
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
        before_completed = self.player.completed_tiles
        for phase in selected:
            self.game.resolve_phase(self.player, phase)
        used = self.player.used_pips - before
        if used == 0 and self.player.completed_tiles == before_completed:
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
        if self.campaign is not None:
            return tuple(self.condition_map[name] for name in self.campaign.condition_names)
        if self.condition_filter == "all":
            return tuple(self.condition_map.values())
        return (self.condition_map[self.condition_filter],)

    def human_summary(self):
        summary = self.game.final_scores()[0][2]
        summary = dict(summary)
        summary["vp_chips"] = self.player.vp_chips
        summary["max_capacity"] = sum(
            track.maximum
            for color, track in self.player.tracks.items()
            if color is not DieColor.WHITE
        )
        summary.update(self.tableau_summary())
        summary["condition_filter"] = self.condition_filter
        summary["difficulty"] = self.difficulty.key
        summary["difficulty_name"] = self.difficulty.label
        summary["campaign"] = self.campaign.key if self.campaign else None
        summary["campaign_name"] = self.campaign.label if self.campaign else None
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
            and summary["developments"] >= condition.min_developments
            and summary["worlds"] >= condition.min_worlds
            and summary["production_worlds"] >= condition.min_production_worlds
            and summary["distinct_world_colors"] >= condition.min_distinct_world_colors
            and summary["novelty_worlds"] >= condition.min_novelty_worlds
            and summary["rare_worlds"] >= condition.min_rare_worlds
            and summary["alien_worlds"] >= condition.min_alien_worlds
            and summary["vp_chips"] >= condition.min_vp_chips
            and summary["max_capacity"] >= condition.min_max_capacity
            and self.player.tracks[DieColor.BLUE].maximum >= condition.min_blue_capacity
            and self.player.tracks[DieColor.RED].maximum >= condition.min_red_capacity
        )

    def tableau_summary(self):
        worlds = [tile for tile in self.player.tableau if tile.kind is TileKind.WORLD]
        developments = [tile for tile in self.player.tableau if tile.kind is TileKind.DEVELOPMENT]
        world_colors = {tile.world_color.strip().lower() for tile in worlds if tile.world_color.strip()}
        return {
            "developments": len(developments),
            "worlds": len(worlds),
            "production_worlds": sum(1 for tile in worlds if tile.produces),
            "distinct_world_colors": len(world_colors),
            "novelty_worlds": sum(1 for tile in worlds if "novelty" in tile.tags),
            "rare_worlds": sum(1 for tile in worlds if "rare_elemental" in tile.tags),
            "alien_worlds": sum(1 for tile in worlds if "alien_technology" in tile.tags),
        }

    def final_scores(self):
        return [("You", self.game.score(self.player), self.human_summary())]


def run_one(
    strategy: str,
    seed: int,
    config: BatteryConfig,
    condition: str,
    dummy_count: int,
    difficulty: str,
    campaign: Optional[str] = None,
):
    game = BatterySoloGame(
        strategy=strategy,
        seed=seed,
        config=config,
        condition=condition,
        campaign=campaign,
        dummy_count=dummy_count,
        difficulty=difficulty,
    )
    scores, reports = game.play()
    return game, scores, reports


def main():
    parser = argparse.ArgumentParser(description="Run the Roll phase-battery solo challenge prototype.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--strategy", default="balanced")
    parser.add_argument("--condition", choices=("all", *SOLO_WIN_CONDITION_MAP), default="all")
    parser.add_argument("--difficulty", choices=tuple(SOLO_DIFFICULTY_MAP), default=DEFAULT_SOLO_DIFFICULTY)
    parser.add_argument("--campaign", choices=tuple(SOLO_CAMPAIGN_MAP), default=None)
    parser.add_argument("--dummy-count", type=int, default=2)
    parser.add_argument("--max-track-capacity", type=int, default=6)
    parser.add_argument("--starting-capacity", type=int, default=2)
    parser.add_argument("--starting-credits", type=int, default=1)
    parser.add_argument("--max-credits", type=int, default=6)
    parser.add_argument("--free-recharge", type=int, default=0)
    parser.add_argument("--yellow-mode", choices=("ship", "alien"), default="alien")
    args = parser.parse_args()

    config = BatteryConfig(
        starting_capacity=args.starting_capacity,
        max_track_capacity=args.max_track_capacity,
        starting_credits=args.starting_credits,
        max_credits=args.max_credits,
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
    campaign_wins = 0
    campaign_marks = Counter()

    for index in range(args.games):
        if args.campaign:
            marked = set()
            campaign_win = True
            for game_index in range(4):
                game, scores, reports = run_one(
                    args.strategy,
                    args.seed + index * 4 + game_index,
                    config,
                    args.condition,
                    args.dummy_count,
                    args.difficulty,
                    args.campaign,
                )
                summary = scores[0][2]
                end_reasons[game.end_reason()] += 1
                rounds.append(game.game.round_number)
                human_scores.append(scores[0][1])
                claimed_tiles.append(summary["dummy_claimed_tiles"])
                drained_vp.append(summary["dummy_vp_chips_drained"])
                last_game = game
                last_scores = scores
                last_reports = reports
                unmarked = [
                    condition
                    for condition in summary["satisfied_conditions"]
                    if condition not in marked
                ]
                if not unmarked:
                    campaign_win = False
                    conditions["loss"] += 1
                    break
                chosen = unmarked[0]
                marked.add(chosen)
                conditions[chosen] += 1
                campaign_marks[chosen] += 1
            if campaign_win and len(marked) == 4:
                campaign_wins += 1
            continue

        game, scores, reports = run_one(
            args.strategy,
            args.seed + index,
            config,
            args.condition,
            args.dummy_count,
            args.difficulty,
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
    print(f"Difficulty: {SOLO_DIFFICULTY_MAP[args.difficulty].label}")
    if args.campaign:
        print(f"Campaign: {SOLO_CAMPAIGN_MAP[args.campaign].label}")
        print(f"Campaign wins: {campaign_wins / args.games:.1%}")
    print(f"Dummy phase cards: {args.dummy_count}")
    print(f"Average rounds: {mean(rounds):.1f}")
    print(f"Average score: {mean(human_scores):.1f}")
    print(f"Average dummy churn: {mean(claimed_tiles):.1f} tiles, {mean(drained_vp):.1f} VP chips")
    print("Win conditions")
    active_conditions = SOLO_CAMPAIGN_MAP[args.campaign].conditions if args.campaign else SOLO_WIN_CONDITIONS
    for condition in active_conditions:
        if args.campaign or args.condition == "all" or args.condition == condition.name:
            denominator = args.games if not args.campaign else max(1, sum(campaign_marks.values()))
            print(f"  {condition.label}: {conditions[condition.name] / denominator:.1%}")
    print(f"  No mark: {conditions['loss'] / args.games:.1%}")
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
