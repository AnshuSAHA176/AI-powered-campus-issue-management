from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

text = "Water is leaking from the ceiling in room 204"

embedding = model.encode(
    text,
    normalize_embeddings=True
)

print("Embedding dimensions:", len(embedding))
print("First 5 values:", embedding)