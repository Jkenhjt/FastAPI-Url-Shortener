from sqlalchemy.exc import MultipleResultsFound, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Executable

from fastapi import HTTPException

from utils.logger import logger


async def transaction_process(db: AsyncSession, transaction: Executable):
    try:
        result = await db.execute(transaction)

        await db.commit()

        return result

    except MultipleResultsFound as e:
        logger.exception(f"MultipleResultsFound: {e}!")

        await db.rollback()
        raise HTTPException(status_code=400)

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"sqlalchemy.exc.IntegrityError: {e}!")

        await db.rollback()

        raise HTTPException(status_code=500, detail="Server error!")
