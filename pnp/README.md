# Print And Play

Open the desired HTML file in a browser and print at 100% scale.

## Contents

### Tiny Galaxy Upgrade Module

- 12 upgrade cards
- 4 Rival Empire profile cards
- 4 Rival difficulty cards
- 7 reference / solo procedure cards

### Roll & Sow

- 4 activate-use-sow player boards
- 1 quick-reference sheet with setup, full round sequence, and worked example
- 10 six-cost goal reference cards with minimums and converted printed bonuses
- five phase bowls that retain rolled die faces
- Citizenry recruitment and printed die-location reminders
- provisional solo procedure

The complete rules are in `../docs/roll_and_sow_rules.pdf`.

### Roll Phase Battery Variant

- 4 deterministic phase-track boards
- 1 combined multiplayer reference aid sheet
- 1 combined solo guide / campaign aid sheet
- 5 solo Dummy phase cards
- printable max markers and setup strips
- Red is Military value/readiness; White settles non-Military Worlds
- printed Cup, Citizenry, and World placement controls die readiness
- Reassign powers temporarily route ready pips without changing track maxima
- multiplayer VP pool is currently 7/player
- six-cost Developments are delayed end-game goals

## Files

- `print-and-play.html`: Tiny Galaxy printable card sheets.
- `roll-and-sow.html`: Roll & Sow boards, quick reference, and goal cards.
- `roll-and-sow.pdf`: generated Roll & Sow print-and-play PDF.
- `roll-phase-battery.html`: Roll phase battery boards, aid sheets, and Dummy cards.
- `roll-phase-battery.pdf`: generated Roll phase battery print-and-play PDF.
- `styles/cards.css`: print layout and card styling.
- `styles/roll.css`: Roll variant print layout.
- `assets/source/upgrade-art-sheet.png`: 12-panel representative upgrade art.
- `assets/source/upgrade-art-sheet-v1.png`: earlier 6-panel art sheet kept for reference.
- `assets/source/rival-art-sheet.png`: representative rival art.

The card text is HTML, not embedded in the art, so rules can be edited quickly
as balance changes.

## Print Notes

- Use letter paper.
- Print at actual size / 100%.
- Turn off "fit to page" if your print dialog shrinks the layout.
- Cut along the card borders or crop marks.

For Roll & Sow, die faces do matter. Roll new Cup dice immediately into their
face-matching bowl. When a phase activates, use any desired dice and sow every
unused die clockwise, beginning with the next phase bowl. Six-cost Developments
form a shared goal pool and do not enter construction. If all phase bowls are
empty during Manage Empire, Recall and reroll one committed die to prevent
lockout.

## Roll Solo Tuning

The Roll Phase Battery solo mode uses a 15-round clock with two Dummy phase
cards per round. Solo has Easy, Normal, Advanced, and Very Hard threshold tiers:
Easy removes most VP pressure but still requires each condition's structural
goal, Normal named conditions average roughly 60% in simulation, and Advanced /
Very Hard are below 50%. Campaign sheets combine named conditions into arcs
such as Outreach, Industrial Base, Sector Survey, Alien Contact, and Mastery.
