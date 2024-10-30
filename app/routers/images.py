import asyncio

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import ProcessedImage as ImageModel
import io
from PIL import Image as PILImage
import base64

router = APIRouter()

async def process_image(image_id: int, image_data: bytes, filter_type: str, db: AsyncSession):
    # Apply the filter to the image
    print("ieofjioesjfoies")
    processed_image = await apply_filter(image_data, filter_type)
    print("ieofjioesjfoies")
    # Update the image entry in the database
    await db.execute(
        update(ImageModel)
        .where(ImageModel.id == image_id)
        .values(status='Saving')
    )
    await db.commit()
    await db.execute(
        update(ImageModel)
        .where(ImageModel.id == image_id)
        .values(image_data=processed_image, status='Completed')
    )
    await db.commit()


async def apply_filter(image_data: bytes, filter_type: str) -> bytes:
    # Open the image
    image = PILImage.open(io.BytesIO(image_data))

    # Apply the specified filter (just a placeholder for actual filter logic)
    if filter_type == "grayscale":
        image = image.convert("L")  # Convert to grayscale
    elif filter_type == "invert":
        image = PILImage.eval(image, lambda x: 255 - x)  # Invert colors
    # Add more filters as needed...

    # Save the processed image to bytes
    byte_io = io.BytesIO()
    image.save(byte_io, format='JPEG')
    byte_io.seek(0)
    return byte_io.read()

@router.post("/upload_image")
async def upload_image( background_tasks: BackgroundTasks,file: UploadFile = File(...), filter_type: str = Form(...), user_id: int = Form(...),
                       db: AsyncSession = Depends(get_db)):
    # Check file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Create a new image entry in the database with status 'processing'
    new_image = ImageModel(user_id=user_id, image_data=None, status='Processing', filter_type=filter_type)
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)

    # Start processing the image asynchronously
    background_tasks.add_task(process_image,new_image.id, await file.read(), filter_type, db)

    return {"id": new_image.id, "message": "Image successfully added for processing"}


@router.get("/image_status/{image_id}")
async def get_image_status(image_id: int, db: AsyncSession = Depends(get_db)):
    image_record = await db.execute(select(ImageModel).filter(ImageModel.id == image_id))
    image = image_record.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"id": image.id, "user_id": image.user_id, "filter_type": image.filter_type, "status": image.status}



from fastapi import Response

@router.get("/get_image/{image_id}")
async def get_image(image_id: int, db: AsyncSession = Depends(get_db)):
    image_record = await db.execute(select(ImageModel).filter(ImageModel.id == image_id))
    image = image_record.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Визначення типу зображення, наприклад 'image/jpeg' або 'image/png'
    content_type = 'image/jpeg'  # Змініть на 'image/png', якщо потрібно

    # Повертаємо зображення як байти
    return Response(content=image.image_data, media_type=content_type)


@router.get("/images/{user_id}")
async def get_user_images(user_id: int, db: AsyncSession = Depends(get_db)):
    images = await db.execute(select(ImageModel.id,ImageModel.status).filter(ImageModel.user_id == user_id))
    return  [{'id': row[0], 'status': row[1]} for row in images]
