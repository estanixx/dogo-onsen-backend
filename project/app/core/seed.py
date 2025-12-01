from app.models import (
    SpiritType,
    TypeRelation,
    PrivateVenue,
    BanquetTableCreate,
    VenueAccount,
    Spirit,
)
from app.services import BanquetService
from app.models import Service
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta

# name, kanji, dangerScore, image
spirit_types_data = [
    ("Onryō", "怨霊", 9, "onryio.png", [2, 1, 2, 1, 2]),
    ("Ubume", "産女", 4, "ubume.png", [1, 0, 1, 0, 2]),
    ("Funayūrei", "船幽霊", 8, "funa.png", [2, 1, 0, 0, 2]),
    ("Zashiki-warashi", "座敷童子", 2, "zashi.png", [1, 0, 0, 0, 2]),
    ("Jikininki", "食人鬼", 10, "jiki.png", [2, 2, 2, 2, 2]),
]
spirit_img_prefix = "https://dogo-user-images.s3.us-east-2.amazonaws.com/spirit_types/"


async def seed_spirit_types(session: AsyncSession):
    # Add all spirit types, then commit once for efficiency
    for idx, (name, kanji, dangerScore, image, _) in enumerate(
        spirit_types_data, start=1
    ):
        spirit_type = SpiritType(
            id=f"{idx}",
            name=name,
            kanji=kanji,
            dangerScore=dangerScore,
            image=spirit_img_prefix + image,
        )
        session.add(spirit_type)
    await session.commit()


async def seed_spirit_type_relations(session: AsyncSession):
    # Add all spirit type relations, then commit once for efficiency
    for idx, (_, _, _, _, relations) in enumerate(spirit_types_data, start=1):
        for target_idx, relation_value in enumerate(relations, start=1):
            if relation_value == 2:
                relation_type = "forbidden"
            elif relation_value == 1:
                relation_type = "separation"
            else:
                relation_type = "allow"
            type_relation = TypeRelation(
                source_type_id=f"{idx}",
                target_type_id=f"{target_idx}",
                relation=relation_type,
            )
            session.add(type_relation)
    await session.commit()


async def seed_private_venue(venues: int, session: AsyncSession):
    # Placeholder for seeding private venues if needed in the future
    for i in range(1, venues + 1):
        venue = PrivateVenue(id=i)
        session.add(venue)
    await session.commit()


async def seed_banquet(tables: int, session: AsyncSession):
    # Placeholder for seeding banquet data if needed in the future
    for _ in range(tables):
        await BanquetService.create_table(BanquetTableCreate(), session)
    await session.commit()


startTime = datetime.now()
endTime = datetime.now() + timedelta(days=60)
password = "1234"
spirit_data = [
    # id, name, image
    (
        "1",
        "Samuel Colorado",
        "https://static.wikia.nocookie.net/bobesponja/images/8/87/Holand%C3%A9s_Volador.png/revision/latest/scale-to-width/360?cb=20101128010045",
    ),
    (
        "2",
        "Estanix Arango",
        "https://preview.redd.it/whats-episode-is-this-picture-where-spongebob-was-a-ghost-v0-0pr0srvi24vc1.png?width=640&crop=smart&auto=webp&s=519b6dfa0bf0df3f8303729de1ea0d13b09a7838",
    ),
    (
        "3",
        "Juanpa Mejía",
        "https://wallpapers.com/images/thumbnail/goofy-ahh-picture-6pgwqo9l9y70ejek.webp",
    ),
    (
        "4",
        "Wendy Yurani",
        "https://i.pinimg.com/474x/ae/90/43/ae904345a7603bd8feec04caa48d97c1.jpg",
    ),
    (
        "5",
        "Kelsier",
        "https://uploads.coppermind.net/thumb/Kelsier_by_Deandra_Scicluna.jpg/250px-Kelsier_by_Deandra_Scicluna.jpg",
    ),
]

service_data = [
    # name, eiltRate, image, description
    (
        "Exorcism Ritual",
        150,
        "https://i0.wp.com/www.americamagazine.org/wp-content/uploads/2020/10/20200813T0915-VATICAN-LETTER-EXORCISM-EXPLAINED-1003611.JPG-884415.JPG?fit=2300%2C1647&ssl=1",
        "A powerful ritual to banish malevolent spirits.",
    ),
    (
        "Spirit Cleansing",
        100,
        "https://images-static.naikaa.com/beauty-blog/wp-content/uploads/2024/10/double-cleansing-banner.jpg",
        "Cleansing services to purify haunted locations.",
    ),
    (
        "Protective Charm",
        75,
        "https://i.etsystatic.com/9773885/r/il/319eb3/1178376308/il_570xN.1178376308_3cjs.jpg",  
        "Protective charms to ward off evil spirits.",
    ),
    (
        "Poker",
        50,
        "https://store-images.s-microsoft.com/image/apps.51959.14272217582130616.02bf9982-d980-42d9-93e6-372b4b7e36d8.31c1e585-05c9-4f32-b695-4b900c913466",
        "A classic card game for entertainment.",
    ),
    (
        "Banquete",
        60,
        "https://media.istockphoto.com/id/465210583/photo/banquet-wedding.jpg?s=612x612&w=0&k=20&c=gulM34pOvyjY8UvVaaPLjX83ZjxY6Plv7RInbmgWtsY=",
        "A grand banquet event for all guests.",
    ),
]


async def seed_spirits(session: AsyncSession):
    for idx, (id, name, image) in enumerate(spirit_data, start=1):
        spirit = Spirit(
            id=id,
            name=name,
            typeId=f"{idx}",  # Assigning all to type "Onryō" for simplicity
            image=image,
            active=True,
        )
        session.add(spirit)
    await session.commit()


async def seed_venue_accounts(session: AsyncSession):
    for idx, (id, name, image) in enumerate(spirit_data, start=1):
        account = VenueAccount(
            id=idx,
            spiritId=id,
            privateVenueId=idx,
            startTime=startTime,
            endTime=endTime,
            pin=password,
        )
        session.add(account)
    await session.commit()

async def seed_services(session: AsyncSession):
    for name, eiltRate, image, description in service_data:
        service = Service(
            name=name,
            eiltRate=eiltRate,
            image=image,
            description=description,
        )
        session.add(service)
    await session.commit()

async def run_seeds(session: AsyncSession):
    try:
        await seed_spirit_types(session)
        await seed_spirit_type_relations(session)
        await seed_spirits(session)
        await seed_services(session)
        await seed_private_venue(10, session)
        await seed_venue_accounts(session)
        await seed_banquet(10, session)
        return "ok"
    except Exception as e:
        print(f"Error seeding spirit types or relations: {e}")
        return "error"
