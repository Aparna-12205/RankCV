from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = None

def get_model():

    global model

    if model is None:

        print(
            "Loading SentenceTransformer model..."
        )

        model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print(
            "Model loaded successfully."
        )

    return model


def semantic_score(
    text1,
    text2
):

    model = get_model()

    embedding1 = model.encode(
        [text1]
    )

    embedding2 = model.encode(
        [text2]
    )

    similarity = cosine_similarity(
        embedding1,
        embedding2
    )[0][0]

    return float(similarity)