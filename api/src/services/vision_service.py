import base64
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
import json
from ..config import settings

class VisionService:
    def __init__(self, google_api_key: str, openai_api_key: str):
        self.google_api_key = google_api_key
        self.openai_api_key = openai_api_key
        self.google_vision_url = "https://vision.googleapis.com/v1/images:annotate"

    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image using Google Vision API"""
        try:
            # Convert bytes to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Prepare request payload
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {"type": "LABEL_DETECTION", "maxResults": 20},
                            {"type": "TEXT_DETECTION", "maxResults": 20},
                            {"type": "OBJECT_LOCALIZATION", "maxResults": 20},
                            {"type": "SAFE_SEARCH_DETECTION"},
                            {"type": "IMAGE_PROPERTIES"}
                        ]
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.google_vision_url}?key={self.google_api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Google Vision API error: {error_text}")

                    result = await response.json()

                    if "responses" not in result or not result["responses"]:
                        raise Exception("No response from Google Vision API")

                    vision_response = result["responses"][0]

                    # Extract relevant information
                    labels = []
                    if "labelAnnotations" in vision_response:
                        labels = [
                            {
                                "description": label["description"],
                                "confidence": label["score"]
                            }
                            for label in vision_response["labelAnnotations"]
                        ]

                    texts = []
                    if "textAnnotations" in vision_response:
                        texts = [text["description"] for text in vision_response["textAnnotations"]]

                    objects = []
                    if "localizedObjectAnnotations" in vision_response:
                        objects = [
                            {
                                "name": obj["name"],
                                "confidence": obj["score"]
                            }
                            for obj in vision_response["localizedObjectAnnotations"]
                        ]

                    colors = []
                    if "imagePropertiesAnnotation" in vision_response:
                        color_props = vision_response["imagePropertiesAnnotation"]
                        if "dominantColors" in color_props:
                            colors = [
                                {
                                    "color": color["color"],
                                    "percentage": color["pixelFraction"]
                                }
                                for color in color_props["dominantColors"]["colors"][:5]
                            ]

                    return {
                        "service": "google_vision",
                        "labels": labels,
                        "texts": texts,
                        "objects": objects,
                        "colors": colors,
                        "confidence": max([label["confidence"] for label in labels]) if labels else 0.0
                    }

        except Exception as e:
            return {
                "service": "google_vision",
                "error": str(e),
                "labels": [],
                "texts": [],
                "objects": [],
                "colors": [],
                "confidence": 0.0
            }