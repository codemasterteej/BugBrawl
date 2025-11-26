"""
Battle Engine

engine calc
bluebug & redbug stats
matchup matrix


"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Bug, Battle
import random

bp = Blueprint('battles', __name__)

@bp.route('/battles')
def list_battles():
    page = request.args.get('page', 1, type=int)
    battles = Battle.query.order_by(Battle.battle_date.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    return render_template('battle_list.html', battles=battles)


@bp.route('/battle/<int:battle_id>')
def view_battle(battle_id):
    """View a specific battle"""
    battle = Battle.query.get_or_404(battle_id)
    return render_template('battle_view.html', battle=battle)


@bp.route('/battle/new', methods=['GET', 'POST'])
@login_required
def new_battle():
    """Create a new battle"""
    if request.method == 'POST':
        red_corner_bug_id = request.form.get(' red_corner_bug_id', type=int)
         blue_corner_bug_id = request.form.get('blue_corner_bug_id', type=int)
        
        # Validation
        if not red_corner_bug_id or not blue_corner_bug_id:
            flash('Please select two bugs', 'danger')
            return redirect(url_for('battles.new_battle'))
        
        if red_corner_bug_id == blue_corner_bug_id:
            flash('A bug cannot battle itself!', 'warning')
            return redirect(url_for('battles.new_battle'))
        
        red_corner_bug = Bug.query.get_or_404(red_corner_bug_id)
        blue_corner_bug = Bug.query.get_or_404(blue_corner_bug_id)
        
        # battle sim
        battle = simulate_battle(red_corner_bug, blue_corner_bug)
        
        flash(f'Battle complete! {battle.winner.nickname} wins!', 'success')
        return redirect(url_for('battles.view_battle', battle_id=battle.id))
    
    bugs = Bug.query.all()
    return render_template('battle_new.html', bugs=bugs)
  
# Combat type system (offensive -> defensive multipliers)
# Offensive types: piercing, crushing, slashing, venom, chemical, grappling
# Defensive types: hard_shell, segmented_armor, evasive, hairy_spiny, toxic_skin, thick_hide

MATCHUP_MATRIX = {
    'piercing': {
        'hard_shell': 1.5, 'segmented_armor': 1.0, 'evasive': 0.7,
        'hairy_spiny': 1.0, 'toxic_skin': 1.5, 'thick_hide': 0.7
    },
    'crushing': {
        'hard_shell': 1.5, 'segmented_armor': 0.7, 'evasive': 1.0,
        'hairy_spiny': 1.0, 'toxic_skin': 0.7, 'thick_hide': 1.5
    },
    'slashing': {
        'hard_shell': 0.7, 'segmented_armor': 1.5, 'evasive': 1.5,
        'hairy_spiny': 0.7, 'toxic_skin': 1.0, 'thick_hide': 1.0
    },
    'venom': {
        'hard_shell': 1.0, 'segmented_armor': 1.5, 'evasive': 1.0,
        'hairy_spiny': 0.7, 'toxic_skin': 0.7, 'thick_hide': 1.5
    },
    'chemical': {
        'hard_shell': 1.0, 'segmented_armor': 1.0, 'evasive': 1.5,
        'hairy_spiny': 1.5, 'toxic_skin': 0.7, 'thick_hide': 0.7
    },
    'grappling': {
        'hard_shell': 0.7, 'segmented_armor': 0.7, 'evasive': 1.5,
        'hairy_spiny': 1.5, 'toxic_skin': 1.0, 'thick_hide': 1.0
    }
}

SIZE_ORDER = ['tiny', 'small', 'medium', 'large', 'massive']

SIZE_BASE_MODIFIER = {
    ('massive', 'tiny'): 1.5,
    ('massive', 'small'): 1.3,
    ('massive', 'medium'): 1.15,
    ('large', 'tiny'): 1.4,
    ('large', 'small'): 1.25,
    ('large', 'medium'): 1.1,
    ('medium', 'tiny'): 1.3,
    ('medium', 'small'): 1.15,
    ('small', 'tiny'): 1.2,
    ('tiny', 'massive'): 0.7,
    ('tiny', 'large'): 0.75,
    ('tiny', 'medium'): 0.8,
    ('small', 'massive'): 0.75,
    ('small', 'large'): 0.8,
    ('small', 'medium'): 0.85,
    ('medium', 'large'): 0.9,
    ('medium', 'massive'): 0.85,
    ('large', 'massive'): 0.9,
}
#the smaller bug cannot use a crushing attack against a larger bug
SIZE_DEPENDENT_ATTACKS = {'crushing', 'grappling', 'piercing', 'slashing'}
SIZE_AGNOSTIC_ATTACKS = {'venom', 'chemical'}

def get_matchup_multiplier(attack_type: str, defense_type: str) -> float:
    """Return multiplier for attack_type vs defense_type using MATCHUP_MATRIX.
    Falls back to 1.0 for unknown types."""
    if not attack_type or not defense_type:
        return 1.0
    attack = (attack_type or '').lower()
    defense = (defense_type or '').lower()
    return MATCHUP_MATRIX.get(attack, {}).get(defense, 1.0)

def get_size_multipliers(size_a: str, size_b: str, attack_type_a: Optional[str] = None, attack_type_b: Optional[str] = None) -> tuple[float, float]:
    """Return (mult_a, mult_b) based on size class and (optionally) attack types.

    Behavior:
    - If an attack type is size-agnostic (venom/chemical), that attack ignores size modifiers.
    - If size-pair explicit mapping exists in SIZE_BASE_MODIFIER, it is used.
    - Otherwise null
    """
    a = red_corner_bug.size
    b = blue_corner_bug.size

    # Unknown sizes -> neutral
    if a is None or b is None:
        return 1.0, 1.0

    # If attack types explicitly ignore size, respect that
    atk_a = (attack_type_a or '').lower() if attack_type_a else None
    atk_b = (attack_type_b or '').lower() if attack_type_b else None

    # If both attacks are size-agnostic, no size modifiers apply
    if (atk_a in SIZE_AGNOSTIC_ATTACKS) and (atk_b in SIZE_AGNOSTIC_ATTACKS):
        return 1.0, 1.0

    # Compute default diff-based multipliers (fallback)
    ia = SIZE_ORDER.index(a)
    ib = SIZE_ORDER.index(b)
    diff = ia - ib
    def default_for_diff(d):
        if d == 0:
            return 1.0
        if d == 1:
            return 1.15
        if d == 2:
            return 1.30
        if d >= 3:
            return 1.40
        if d == -1:
            return 1.0 / 1.15
        if d == -2:
            return 1.0 / 1.30
        if d <= -3:
            return 1.0 / 1.40
        return 1.0

    # Try explicit mapping first
    explicit_a = SIZE_BASE_MODIFIER.get((a, b))
    explicit_b = SIZE_BASE_MODIFIER.get((b, a))

    if explicit_a is not None or explicit_b is not None:
        # If one direction missing, try reciprocal of the other or fallback
        if explicit_a is None and explicit_b is not None:
            explicit_a = 1.0 / explicit_b if explicit_b != 0 else 1.0
        if explicit_b is None and explicit_a is not None:
            explicit_b = 1.0 / explicit_a if explicit_a != 0 else 1.0
        mult_a = explicit_a if explicit_a is not None else default_for_diff(diff)
        mult_b = explicit_b if explicit_b is not None else default_for_diff(-diff)
    else:
        mult_a = default_for_diff(diff)
        mult_b = default_for_diff(-diff)

    # If a given attack is size-agnostic, it should not receive the size-based boost/penalty
    if atk_a in SIZE_AGNOSTIC_ATTACKS:
        mult_a = 1.0
    if atk_b in SIZE_AGNOSTIC_ATTACKS:
        mult_b = 1.0

    return round(mult_a, 3), round(mult_b, 3)

def simulate_battle(red_corner_bug: Bug, blue_corner_bug: Bug) -> Battle:
    """
    Simulate a battle between two bugs
    
    BATTLE MECHANICS:
    1. Calculate base power (attack + defense + speed)
    2. Apply type advantages
    3. Add randomness (±10%)
    4. Determine winner
    5. Generate narrative
    6. Update records\
    7. Advance bug if tournament battle
    
    Args:
        red_corner_bug: First bug
        blue_corner_bug: Second bug
    
    Returns:
        Battle object with winner and narrative
    """

    battle = Battle(
        red_corner_bug_id=red_corner_bug.id,
        blue_corner_bug_id=blue_corner_bug.id,
        winner_id=winner.id if winner else None,
        battle_date=db.func.current_timestamp(),
        narrative=narrative,
        tournament_id=tournament_id,
        round_number=round_number,
    )
  
    # Calculate power with randomness
    red_corner_bug_power = calculate_battle_power(red_corner_bug)
    blue_corner_bug_power = calculate_battle_power(blue_corner_bug)
    
    # Determine winner
    if red_corner_bug_power > blue_corner_bug_power:
        winner = bug1
        loser = bug2
    elif bug2_power > bug1_power:
        winner = bug2
        loser = bug1
    else:
        # Tie - random winner
        winner = random.choice([bug1, bug2])
        loser = bug2 if winner == bug1 else bug1
    
    # Generate narrative
    narrative = generate_battle_narrative(bug1, bug2, winner)
    
    # Create battle record
    battle = Battle(
        bug1_id=bug1.id,
        bug2_id=bug2.id,
        winner_id=winner.id,
        narrative=narrative
    )
    
    # Update win/loss records
    winner.wins += 1
    loser.losses += 1
    
    # Save to database
    db.session.add(battle)
    db.session.commit()
    
    return battle


def calculate_battle_power(bug: Bug) -> float:
    """
    Calculate a bug's battle power
    
    FORMULA:
    - Attack is weighted 2x (offense wins fights)
    - Defense is weighted 1.5x (protection matters)
    - Speed is weighted 1.2x (going first helps)
    - Add ±10% randomness (critical hits, luck, etc.)
    
    Args:
        bug: Bug to calculate power for
    
    Returns:
        Total battle power (float)
    """
    base_power = (
        bug.attack * 2.0 +
        bug.defense * 1.5 +
        bug.speed * 1.2
    )
    
    # Add randomness (90% to 110% of base power)
    randomness = random.uniform(0.9, 1.1)
    
    return base_power * randomness

