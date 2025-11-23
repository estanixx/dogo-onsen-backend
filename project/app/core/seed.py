from app.models import SpiritType
from sqlmodel.ext.asyncio.session import AsyncSession


# name, kanji, dangerScore, image
spirit_types_data = [
    ("Onryō", "怨霊", 9, "onryio.png"),
    ("Ubume", "産女", 4, "ubume.png"),
    ("Funayūrei", "船幽霊", 8, "funa.png"),
    ("Zashiki-warashi", "座敷童子", 2, "zashi.png"),
    ("Jikininki", "食人鬼", 10, "jiki.png"),
]

spirit_img_prefix = "https://dogo-user-images.s3.us-east-2.amazonaws.com/spirit_types/"


async def seed_spirit_types(session: AsyncSession):
    # Add all spirit types, then commit once for efficiency
    for idx, (name, kanji, dangerScore, image) in enumerate(spirit_types_data, start=1):
        spirit_type = SpiritType(
            id=f"{idx}",
            name=name,
            kanji=kanji,
            dangerScore=dangerScore,
            image=spirit_img_prefix + image,
        )
        session.add(spirit_type)
    await session.commit()


async def run_seeds(session: AsyncSession):
    await seed_spirit_types(session)
