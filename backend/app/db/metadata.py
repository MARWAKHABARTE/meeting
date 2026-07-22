from sqlalchemy import MetaData

# Convention de nommage PostgreSQL pour éviter les conflits et faciliter les migrations Alembic
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Objet MetaData global configuré avec les conventions
metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
