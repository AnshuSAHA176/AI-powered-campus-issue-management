from sentence_transformers import SentenceTransformer
from celery import shared_task
from .models import Complaint
from pgvector.django import CosineDistance
from .models import ComplaintSimilarity
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)


def embedding_model(text: str):
    return model.encode(
        text,
        normalize_embeddings=True
    ).tolist()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def create_embedding(self, complaint_id):

    complaint = Complaint.objects.get(
        complaint_id=complaint_id
    )

    text = f"""
    {complaint.description}

    Building: {complaint.building}
    Room: {complaint.room_number}
    Landmark: {complaint.landmark}
    Category: {complaint.category}
    """

    embedding = embedding_model(text)

    complaint.embedding = embedding

    complaint.save(
        update_fields=["embedding"]
    )



@shared_task(bind=True, max_retries=3)
def duplicate_compliant_detection(self, complaint_id):

    try:
        complaint = Complaint.objects.get(
            complaint_id=complaint_id
        )

        embedding = complaint.embedding

        if embedding is None:
            raise ValueError(
                f"Embedding not available for {complaint_id}"
            )

        similar = (
            Complaint.objects
            .filter(embedding__isnull=False)
            .exclude(id=complaint.id)
            .annotate(
                distance=CosineDistance(
                    "embedding",
                    embedding
                )
            )
            .order_by("distance")[:6]
        )

        for match in similar:

            if match.distance is None:
                continue

            similarity = 1 - match.distance

            if similarity >= 0.85:
                ComplaintSimilarity.objects.get_or_create(
                    complaint=complaint,
                    similar_complaint=match,
                    defaults={
                        "similarity_score": similarity
                    }
                )

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=4
        )


