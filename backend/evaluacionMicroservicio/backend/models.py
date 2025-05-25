import enum
from sqlalchemy import CheckConstraint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Enum

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)
    rol = db.Column(db.String(20), default="Cliente")
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_joined = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.username}>'

class Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    city = db.Column(db.String(30), nullable=False)
    general_objective = db.Column(db.String(250), nullable = False)
    description = db.Column(db.String(300), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('software', cascade='all, delete', lazy=True))
    evaluations = db.relationship("Evaluation", backref="software", cascade="all, delete-orphan")
    def __repr__(self):
        return f'<Software {self.name}>'
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'general_objective': self.general_objective,
            'description': self.description,
            'version': self.version,
            'user_id': self.user_id,
            'registered_at': self.registered_at.strftime('%d-%m-%Y') if self.registered_at else None
        }
class SoftwareParticipant(db.Model):
    __tablename__ = 'software_participants'

    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)

    software = db.relationship('Software', backref=db.backref('participants', cascade='all, delete-orphan', lazy=True))

    def __repr__(self):
        return f'<SoftwareParticipant {self.name} - {self.role}>'

class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    global_score_percentage = db.Column(db.Numeric(5, 2), nullable=True)

    details = db.relationship('EvaluationDetail', backref='evaluation', cascade='all, delete-orphan')
    characteristic_summaries = db.relationship('EvaluationCharacteristicSummary', backref='evaluation', cascade='all, delete-orphan')


class EvaluationCharacteristicSummary(db.Model):
    __tablename__ = 'evaluation_characteristic_summary'

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id', ondelete='CASCADE'), nullable=False)
    characteristic_id = db.Column(db.Integer, db.ForeignKey('quality_characteristics.id', ondelete='SET NULL'))  

    value = db.Column(db.Integer, nullable=False)
    max_value = db.Column(db.Integer, nullable=False)
    result_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    weighted_percentage = db.Column(db.Numeric(5, 2), nullable=False)

    characteristic_name = db.Column(db.String(100), nullable=False)
    weight_percentage = db.Column(db.Numeric(5, 2), nullable=False)


class EvaluationDetail(db.Model):
    __tablename__ = 'evaluation_details'

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id', ondelete='CASCADE'), nullable=False)
    subcharacteristic_id = db.Column(db.Integer, db.ForeignKey('subcharacteristics.id', ondelete='SET NULL'))
    score = db.Column(db.SmallInteger, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    subcharacteristic_name = db.Column(db.String(100), nullable=False)
    subcharacteristic_description = db.Column(db.Text)
    max_score = db.Column(db.SmallInteger, nullable=False)

    __table_args__ = (
        db.CheckConstraint('score BETWEEN 0 AND 3', name='check_score_between_0_and_3'),
    )

class QualityCharacteristic(db.Model):
    __tablename__ = 'quality_characteristics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    weight_percentage = db.Column(db.Numeric(5, 2), nullable=False)

    subcharacteristics = db.relationship('Subcharacteristic', backref='characteristic', cascade='all, delete-orphan', lazy=True)

    __table_args__ = (
        CheckConstraint('weight_percentage >= 0 AND weight_percentage <= 100', name='check_weight_percentage'),
    )
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'weight_percentage': float(self.weight_percentage)
        }

    def __repr__(self):
        return f'<QualityCharacteristic {self.name}>'


class Subcharacteristic(db.Model):
    __tablename__ = 'subcharacteristics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    characteristic_id = db.Column(db.Integer, db.ForeignKey('quality_characteristics.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_score = db.Column(db.SmallInteger, default=3, nullable=False)

    __table_args__ = (
        CheckConstraint('max_score > 0', name='check_max_score'),
    )
    
    def serialize(self):
        return {
            'id': self.id,
            'characteristic_id': self.characteristic_id,
            'name': self.name,
            'description': self.description,
            'max_score': self.max_score
        }

    def __repr__(self):
        return f'<Subcharacteristic {self.name} (max {self.max_score})>'
    
class SoftwareRisk(db.Model):
    __tablename__ = 'software_risks'

    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id', ondelete='CASCADE'))
    risk_code = db.Column(db.String(50))
    identified_at = db.Column(db.Date)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    causes = db.Column(db.Text)
    affects_critical_infrastructure = db.Column(db.Boolean)
    process = db.Column(db.String(100))

    ownership = db.relationship('RiskOwnership', backref='risk', cascade="all, delete-orphan", uselist=False)
    classification = db.relationship('RiskClassification', backref='risk', cascade="all, delete-orphan", uselist=False)
    evaluation = db.relationship('RiskEvaluation', backref='risk', cascade="all, delete-orphan", uselist=False)
    controls = db.relationship('RiskControl', backref='risk', cascade="all, delete-orphan", uselist=False)

class RiskOwnership(db.Model):
    __tablename__ = 'risk_ownership'

    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('software_risks.id', ondelete='CASCADE'))
    owner_name = db.Column(db.String(100))
    owner_role = db.Column(db.String(100))

class RiskTypeEnum(enum.Enum):
    Logico = 'Lógico'
    Fisico = 'Físico'
    Locativo = 'Locativo'
    Legal = 'Legal'
    Reputacional = 'Reputacional'
    Financiero = 'Financiero'

class RiskClassification(db.Model):
    __tablename__ = 'risk_classification'

    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('software_risks.id', ondelete='CASCADE'))
    risk_type = db.Column(Enum(RiskTypeEnum))
    confidentiality = db.Column(db.Boolean)
    integrity = db.Column(db.Boolean)
    availability = db.Column(db.Boolean)
    impact_type = db.Column(db.String(30))

class LikelihoodEnum(enum.Enum):
    RARO = 1
    IMPROBABLE = 2
    POSIBLE = 3
    PROBABLE = 4
    CASI_SEGURO = 5

class ImpactEnum(enum.Enum):
    INSIGNIFICANTE = 1
    MENOR = 2
    MODERADO = 3
    MAYOR = 4
    CATASTROFICO = 5

class RiskEvaluation(db.Model):
    __tablename__ = 'risk_evaluation'

    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('software_risks.id', ondelete='CASCADE'), nullable=False)
    likelihood = db.Column(Enum(LikelihoodEnum), nullable=False)
    impact = db.Column(Enum(ImpactEnum), nullable=False)
    risk_zone = db.Column(db.String(100))
    acceptance = db.Column(db.Text)

class RiskControl(db.Model):
    __tablename__ = 'risk_controls'

    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('software_risks.id', ondelete='CASCADE'))
    control_type = db.Column(db.String(100))
    has_mechanism = db.Column(db.Boolean)
    has_manuals = db.Column(db.Boolean)
    control_effective = db.Column(db.Boolean)
    responsible_defined = db.Column(db.Boolean)
    control_frequency_adequate = db.Column(db.Boolean)
    control_rating = db.Column(db.Numeric(5, 2))
    preventive_controls_avg = db.Column(db.Numeric(5, 2))
    reduce_likelihood_quadrants = db.Column(db.Integer)
    corrective_controls_avg = db.Column(db.Numeric(5, 2))
    reduce_impact_quadrants = db.Column(db.Integer)

    __table_args__ = (
        CheckConstraint('reduce_likelihood_quadrants BETWEEN 0 AND 2'),
        CheckConstraint('reduce_impact_quadrants BETWEEN 0 AND 2'),
    )
    
    """
        #Es una tabla intermedia para vincular los parametros a un software en especial
class SoftwareCharacteristic(db.Model):
    __tablename__ = 'software_characteristics'

    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id', ondelete='CASCADE'), nullable=False)
    characteristic_id = db.Column(db.Integer, db.ForeignKey('quality_characteristics.id', ondelete='CASCADE'), nullable=False)

    software = db.relationship('Software', backref=db.backref('software_characteristics', cascade='all, delete-orphan'))
    characteristic = db.relationship('QualityCharacteristic', backref=db.backref('software_assignments', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('software_id', 'characteristic_id', name='unique_software_characteristic'),
    )
 """
class ResponseTypeEnum(enum.Enum):
    EVITAR = 'Evitar'
    MITIGAR = 'Mitigar'
    TRANSFERIR = 'Transferir'
    ACEPTAR = 'Aceptar'

class RiskMitigation(db.Model):
    __tablename__ = 'risk_mitigation'

    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('software_risks.id', ondelete='CASCADE'), nullable=False)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('risk_evaluation.id', ondelete='CASCADE'))
    ownership_id = db.Column(db.Integer, db.ForeignKey('risk_ownership.id', ondelete='SET NULL'))
    risk_code = db.Column(db.String(50))
    risk_description = db.Column(db.Text)
    risk_zone = db.Column(db.String(100))
    responsible = db.Column(db.String(100))
    phase = db.Column(db.String(100))
    response_type = db.Column(Enum(ResponseTypeEnum))
    mitigation_plan = db.Column(db.Text)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    risk = db.relationship('SoftwareRisk', backref=db.backref('mitigations', cascade='all, delete-orphan'))
    evaluation = db.relationship('RiskEvaluation', backref='mitigation')
    ownership = db.relationship('RiskOwnership', backref='mitigation')

    def __repr__(self):
        return f'<RiskMitigation {self.risk_code} - {self.response_type.name}>'