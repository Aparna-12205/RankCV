from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

skill1 = "artificial intelligence"
skill2 = "AI"

embedding1 = model.encode([skill1])
embedding2 = model.encode([skill2])

similarity = cosine_similarity(
    embedding1,
    embedding2
)

print(similarity)