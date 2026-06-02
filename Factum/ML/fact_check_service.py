import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FACT_CHECK_API_KEY")

FACT_CHECK_URL = (
    "https://factchecktools.googleapis.com/v1alpha1/claims:search"
)


def normalize(text):
    return text.lower().strip()


def check_fact(text):

    normalized_text = normalize(text)

    try:
        response = requests.get(
            FACT_CHECK_URL,
            params={
                "query": text,
                "key": API_KEY,
                "languageCode": "pt-BR"
            },
            timeout=5
        )

        if response.status_code != 200:
            return None

        data = response.json()

        claims = data.get("claims")

        if not claims:
            return None

        for claim in claims:

            api_text = claim.get("text", "")
            api_normalized = normalize(api_text)

            print("\n===================")
            print("USUARIO:", normalized_text)
            print("API:", api_normalized)
            print("===================\n")

            if (
                normalized_text not in api_normalized
                and api_normalized not in normalized_text
            ):
                continue

            reviews = claim.get("claimReview", [])

            if not reviews:
                continue

            review = reviews[0]

            return {
                "source": review.get(
                    "publisher",
                    {}
                ).get(
                    "name",
                    "Desconhecido"
                ),
                "rating": review.get(
                    "textualRating",
                    "Sem classificação"
                ),
                "url": review.get("url", ""),
                "claim": api_text
            }

    except Exception as e:
        print("Erro Fact Check:", e)

    return None