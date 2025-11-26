"""
Front End Connection - Homepage and Dashboard
"""
from flask import Blueprint, render_template
from app import db
from app.models import Bug, Battle, User
from sqlalchemy import desc, func

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    Homepage - show recent activity and top bugs
    - .order_by() - sort results
    - .limit() - get only N results
    - desc() - descending order (newest first)
    """
    # Get 5 most recent battles
    recent_battles = Battle.query.order_by(desc(Battle.battle_date)).limit(5).all()
    
    # Get top 10 bugs by wins
    top_bugs = Bug.query.order_by(desc(Bug.wins)).limit(10).all()

    all_bugs = Bug.query.order_by(submission_date(Bug)).all()
    
    return render_template('index.html',
                         battles=recent_battles,
                         top_bugs=top_bugs)


@bp.route('/dashboard')
def dashboard():
    """
    Simple Admin Dashboard
    
    Shows key statistics about the arena
    
    TEACHING MOMENT:
    - .count() - count rows
    - func.avg() - SQL aggregate function for average
    - .scalar() - get single value from query
    """
    # Basic counts
    total_bugs = Bug.query.count()
    total_users = User.query.count()
    total_battles = Battle.query.count()
    total_tournaments = Tournament.query.count()
    
    # Calculate highest stats
    max_attack = db.session.query(func.max(Bug.attack)).scalar() or 0
    max_defense = db.session.query(func.max(Bug.defense)).scalar() or 0
    max_speed = db.session.query(func.max(Bug.speed)).scalar() or 0
    max_hp = db.session.query(func.max(Bug.HP)).scalar() or 0
  
    recent_bugs = Bug.query.order_by(desc(Bug.submission_date)).limit(5).all()
    recent_battles = Battle.query.order_by(desc(Battle.battle_date)).limit(5).all()
    
    # Top performers
    top_bugs = Bug.query.order_by(desc(Bug.wins)).limit(5).all()
    
    return render_template('dashboard.html',
                         total_bugs=total_bugs,
                         total_users=total_users,
                         total_battles=total_battles,
                         avg_attack=round(avg_attack, 1),
                         avg_defense=round(avg_defense, 1),
                         avg_speed=round(avg_speed, 1),
                         recent_bugs=recent_bugs,
                         recent_battles=recent_battles,
                         top_bugs=top_bugs)
