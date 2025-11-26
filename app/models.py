"""
Database Models
Each class represents a table in your database
SQLAlchemy handles all the SQL for you!
"""
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# This tells Flask how to load a user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: one user has many bugs
    bugs = db.relationship('Bug', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
      #hashes password before storing
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User {self.username}>'


class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    nickname = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(200))  # Scientific or common name
    image_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Combat stats (1-100 scale)
    attack = db.Column(db.Integer, default=50)
    defense = db.Column(db.Integer, default=50)
    speed = db.Column(db.Integer, default=50)
    health = db.Column(db.Integer, default=500)
        # STATS (visible + hidden xfactor)

    attack = db.Column(db.Integer, default=5)
    defense = db.Column(db.Integer, default=5)
    speed = db.Column(db.Integer, default=5)
    special_attack = db.Column(db.Integer, default=5)
    special_defense = db.Column(db.Integer, default=5)
    health = db.Column(db.Integer, default=100)
    # Combat characteristic fields (visible + used in battle logic)
    attack_type = db.Column(db.String(50))   # e.g., piercing, crushing, slashing, venom, chemical, grappling
    defense_type = db.Column(db.String(50))  # e.g., hard_shell, segmented_armor, evasive, hairy_spiny, toxic_skin, thick_hide
    size_class = db.Column(db.String(20))    # tiny, small, medium, large, massive
    
    xfactor = db.Column(db.Float, default=0.0)  # -5.0 to +5.0 hidden modifier
    xfactor_reason = db.Column(db.Text)
    
    special_ability = db.Column(db.String(200))
    
    stats_generated = db.Column(db.Boolean, default=False)
    stats_generation_method = db.Column(db.String(50))
    
    flair = db.Column(db.String(100))
    title = db.Column(db.String(100))

    # Location data
    location_found = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    found_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Tier system (for tournaments)
    tier = db.Column(db.String(20))  # 'uber', 'ou', 'uu', 'ru', 'nu', 'zu'

  # Battle record or win %
    wins = db.Column(db.Integer, default=0),
    losses = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    red_corner_bug = db.relationship('Battle', 
                                      foreign_keys='Battle.red_corner_bug_id',
                                      backref='bluebug', 
                                      lazy='dynamic')
    battles_as_bug2 = db.relationship('Battle',
                                      foreign_keys='Battle.blue_corner_bug__id', 
                                      backref='redbug',
                                      lazy='dynamic')
    
    @property
    def win_rate(self):
        total = self.wins + self.losses
        return (self.wins / total * 100) if total > 0 else 0
    
    @property
    def power_level(self):
        return self.attack + self.defense + self.speed
    
    def __repr__(self):
        return f'<Bug {self.nickname}>'

    def generate_flair(self):
        """Auto-generate flair based on performance"""
        if self.win_rate >= 1:
            self.flair = "Undefeated"
        elif self.win_rate >= 80 and self.wins >= 5:
            self.flair = "Dominator"
        elif self.wins >= 5:
            self.flair = "Veteran"
        elif self.speed >= 80:
            self.flair = "Speedster"
        elif self.defense >= 80:
            self.flair = "Tank"
        elif self.attack >= 80:
            self.flair = "Powerhouse"
        else:
            self.flair = Null

class Species(db.Model):
  #taxonomy api still tbd
  id = db.Column(db.Integer, primary_key=True)
  scientific_name = db.Column(db.String(200))
  common_name = db.Column(db.String(200))
  genus = db.Column(db.String(200))
  family = db.Column(db.String(200))
  species = db.Column(db.String(200))
  descrition = db.Column(db.String(200))
  habitat = db.Column(db.String(200))
  diet = db.Column(db.String(200)) #<-maybe used in matchup advantage?
  avg_size = db.Column(db.Integer(5))
  avg_weight = db.Column(db.Integer(5))
  
  #combat traits for zero sum game    
    has_venom = db.Column(db.Boolean, default=False)
    has_pincers = db.Column(db.Boolean, default=False)
    has_stinger = db.Column(db.Boolean, default=False)
    can_fly = db.Column(db.Boolean, default=False)
    has_armor = db.Column(db.Boolean, default=False)

        # API references
    gbif_id = db.Column(db.String(100))
    inaturalist_id = db.Column(db.String(100))
    wikipedia_url = db.Column(db.String(500))
    data_source = db.Column(db.String(100))

    bugs = db.relationship('Bug', lazy='dynamic')

    def add_to_dict(self):
      return{
            'id': self.id,
            'scientific_name': self.scientific_name,
            'common_name': self.common_name,
            'order': self.order,
            'family': self.family,
            'characteristics': {
                'has_venom': self.has_venom,
                'has_pincers': self.has_pincers,
                'has_stinger': self.has_stinger,
                'can_fly': self.can_fly,
                'has_armor': self.has_armor
            }
      }

class Battle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # The two bugs fighting
    red_corner_bug_id = db.Column(db.Integer, db.ForeignKey('bug.id'), nullable=False)
    blue_corner_bug__id = db.Column(db.Integer, db.ForeignKey('bug.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('bug.id'))
    narrative = db.Column(db.Text)
    battle_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    winner = db.relationship('Bug', foreign_keys=[winner_id])
    
    def __repr__(self):
        return f'<Battle {self.id}: {self.red_corner_bug_id} vs {self.blue_corner_bug__id}>'
